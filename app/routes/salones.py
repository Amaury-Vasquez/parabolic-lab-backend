from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.dependencies import get_current_user, get_db
from app.models.alumno_en_salon import AlumnoEnSalon
from app.models.salon import Salon
from app.models.usuario import Usuario
from app.schemas.salon import SalonRead, SalonWithDetails

router = APIRouter(prefix="/salones", tags=["Salones"])


@router.get("/me", response_model=list[SalonWithDetails])
async def mis_salones(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Devuelve los salones del usuario actual con detalles (escenarios y conteo de alumnos)."""
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
