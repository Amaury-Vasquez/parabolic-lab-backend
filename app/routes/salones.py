import random
import string
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.dependencies import get_current_user, get_db
from app.models.alumno_en_salon import AlumnoEnSalon
from app.models.salon import Salon
from app.models.usuario import Usuario
from app.schemas.salon import SalonCreate, SalonRead, SalonUpdate, SalonWithDetails

router = APIRouter(prefix="/salones", tags=["Salones"])


def _generar_codigo(longitud: int = 6) -> str:
    """Genera un código de acceso alfanumérico en mayúsculas."""
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=longitud))


def _require_docente(current_user: Usuario) -> None:
    if current_user.tipousuario != "docente" or not current_user.docente:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los docentes pueden realizar esta acción",
        )


# ── READ ──────────────────────────────────────────────────────────────────────

@router.get("/me", response_model=list[SalonWithDetails])
async def mis_salones(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Devuelve los salones del usuario actual con detalles."""
    if current_user.tipousuario == "docente":
        if not current_user.docente:
            return []
        query = (
            select(Salon)
            .where(Salon.iddocente == current_user.docente.iddocente)
            .where(Salon.activo.is_(True))
            .options(selectinload(Salon.escenarios), selectinload(Salon.alumnos))
        )
    elif current_user.tipousuario == "alumno":
        if not current_user.alumno:
            return []
        query = (
            select(Salon)
            .join(AlumnoEnSalon, AlumnoEnSalon.idsalon == Salon.idsalon)
            .where(AlumnoEnSalon.idalumno == current_user.alumno.idalumno)
            .where(AlumnoEnSalon.activo.is_(True))
            .where(Salon.activo.is_(True))
            .options(selectinload(Salon.escenarios), selectinload(Salon.alumnos))
        )
    elif current_user.tipousuario == "admin":
        query = (
            select(Salon)
            .where(Salon.idinstitucion == current_user.idinstitucion)
            .where(Salon.activo.is_(True))
            .options(selectinload(Salon.escenarios), selectinload(Salon.alumnos))
        )
    else:
        return []

    result = await db.execute(query)
    salones = result.scalars().unique().all()
    return [
        SalonWithDetails(
            idsalon=s.idsalon,
            nombresalon=s.nombresalon,
            codigoacceso=s.codigoacceso,
            activo=s.activo,
            escenarios=[e.nombre for e in s.escenarios if e.activo],
            num_estudiantes=sum(1 for a in s.alumnos if a.activo),
        )
        for s in salones
    ]


@router.get("/", response_model=list[SalonRead])
async def listar_salones(
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    result = await db.execute(select(Salon))
    return result.scalars().all()


@router.get("/{idsalon}", response_model=SalonRead)
async def obtener_salon(
    idsalon: UUID,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    result = await db.execute(select(Salon).where(Salon.idsalon == idsalon))
    salon = result.scalar_one_or_none()
    if not salon:
        raise HTTPException(status_code=404, detail="Salon no encontrado")
    return salon


# ── WRITE ─────────────────────────────────────────────────────────────────────

@router.post("/", response_model=SalonRead, status_code=status.HTTP_201_CREATED)
async def crear_salon(
    data: SalonCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Crea un nuevo salón. Solo docentes."""
    _require_docente(current_user)

    # Generar código único dentro de la institución
    for _ in range(10):
        codigo = _generar_codigo()
        existe = await db.execute(
            select(Salon).where(
                Salon.codigoacceso == codigo,
                Salon.idinstitucion == current_user.idinstitucion,
            )
        )
        if not existe.scalar_one_or_none():
            break

    salon = Salon(
        iddocente=current_user.docente.iddocente,
        idinstitucion=current_user.idinstitucion,
        codigoacceso=codigo,
        nombresalon=data.nombresalon,
    )
    db.add(salon)
    await db.commit()
    await db.refresh(salon)
    return salon


@router.put("/{idsalon}", response_model=SalonRead)
async def actualizar_salon(
    idsalon: UUID,
    data: SalonUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Edita un salón. Solo el docente dueño."""
    _require_docente(current_user)

    result = await db.execute(select(Salon).where(Salon.idsalon == idsalon))
    salon = result.scalar_one_or_none()
    if not salon:
        raise HTTPException(status_code=404, detail="Salon no encontrado")
    if salon.iddocente != current_user.docente.iddocente:
        raise HTTPException(status_code=403, detail="No tienes permiso para editar este salon")

    if data.nombresalon is not None:
        salon.nombresalon = data.nombresalon
    if data.activo is not None:
        salon.activo = data.activo
    salon.fechamodificacion = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(salon)
    return salon


@router.delete("/{idsalon}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_salon(
    idsalon: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Desactiva un salón (soft delete). Solo el docente dueño."""
    _require_docente(current_user)

    result = await db.execute(select(Salon).where(Salon.idsalon == idsalon))
    salon = result.scalar_one_or_none()
    if not salon:
        raise HTTPException(status_code=404, detail="Salon no encontrado")
    if salon.iddocente != current_user.docente.iddocente:
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar este salon")

    salon.activo = False
    salon.fechamodificacion = datetime.now(timezone.utc)
    await db.commit()