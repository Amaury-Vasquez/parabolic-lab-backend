from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.escenario import Escenario
from app.models.salon import Salon
from app.models.usuario import Usuario
from app.schemas.escenario import AsignarEscenarioRequest, EscenarioCreate, EscenarioRead, EscenarioUpdate

router = APIRouter(prefix="/escenarios", tags=["Escenarios"])


def _require_docente(current_user: Usuario) -> None:
    if current_user.tipousuario != "docente" or not current_user.docente:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los docentes pueden realizar esta acción",
        )


async def _verificar_salon_del_docente(idsalon: UUID, docente_id: UUID, db: AsyncSession) -> Salon:
    """Verifica que el salón existe y pertenece al docente."""
    result = await db.execute(select(Salon).where(Salon.idsalon == idsalon))
    salon = result.scalar_one_or_none()
    if not salon:
        raise HTTPException(status_code=404, detail="Salon no encontrado")
    if salon.iddocente != docente_id:
        raise HTTPException(status_code=403, detail="No tienes permiso sobre este salon")
    return salon


# ── READ ──────────────────────────────────────────────────────────────────────
@router.get("/me", response_model=list[EscenarioRead])
async def mis_escenarios(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Devuelve todos los escenarios de los salones del docente actual."""
    _require_docente(current_user)

    result = await db.execute(
        select(Escenario)
        .join(Salon, Salon.idsalon == Escenario.idsalon)
        .where(Salon.iddocente == current_user.docente.iddocente)
        .where(Escenario.activo.is_(True))
        .order_by(Escenario.fechacreacion.desc())
    )
    return result.scalars().all()


@router.get("/", response_model=list[EscenarioRead])
async def listar_escenarios(
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    result = await db.execute(select(Escenario))
    return result.scalars().all()


@router.get("/{idescenario}", response_model=EscenarioRead)
async def obtener_escenario(
    idescenario: UUID,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    result = await db.execute(select(Escenario).where(Escenario.idescenario == idescenario))
    escenario = result.scalar_one_or_none()
    if not escenario:
        raise HTTPException(status_code=404, detail="Escenario no encontrado")
    return escenario


# ── WRITE ─────────────────────────────────────────────────────────────────────


@router.post("/", response_model=EscenarioRead, status_code=status.HTTP_201_CREATED)
async def crear_escenario(
    data: EscenarioCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Crea un escenario en un salón. Solo el docente dueño del salón."""
    _require_docente(current_user)
    await _verificar_salon_del_docente(data.idsalon, current_user.docente.iddocente, db)

    escenario = Escenario(
        idsalon=data.idsalon,
        nombre=data.nombre,
        descripcion=data.descripcion,
        niveldificultad=data.niveldificultad,
        tipoescenario=data.tipoescenario,
        objetivosaprendizaje=data.objetivosaprendizaje,
        instrucciones=data.instrucciones,
        tiempolimite=data.tiempolimite,
        intentospermitidos=data.intentospermitidos,
        configuracionescenario=data.configuracionescenario or {},
    )
    db.add(escenario)
    await db.commit()
    await db.refresh(escenario)
    return escenario


@router.post("/{idescenario}/asignar", response_model=EscenarioRead, status_code=status.HTTP_201_CREATED)
async def asignar_escenario(
    idescenario: UUID,
    data: AsignarEscenarioRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Copia un escenario a otro salón. Solo el docente dueño de ambos salones."""
    _require_docente(current_user)

    # Obtener el escenario original
    result = await db.execute(select(Escenario).where(Escenario.idescenario == idescenario))
    escenario_original = result.scalar_one_or_none()
    if not escenario_original:
        raise HTTPException(status_code=404, detail="Escenario no encontrado")

    # Verificar que el docente es dueño del salón actual del escenario
    await _verificar_salon_del_docente(escenario_original.idsalon, current_user.docente.iddocente, db)

    # Verificar que el docente es dueño del salón destino
    await _verificar_salon_del_docente(data.idsalon, current_user.docente.iddocente, db)

    # Crear una copia del escenario en el salón destino
    nuevo_escenario = Escenario(
        idsalon=data.idsalon,
        nombre=escenario_original.nombre,
        descripcion=escenario_original.descripcion,
        niveldificultad=escenario_original.niveldificultad,
        tipoescenario=escenario_original.tipoescenario,
        objetivosaprendizaje=escenario_original.objetivosaprendizaje,
        instrucciones=escenario_original.instrucciones,
        tiempolimite=escenario_original.tiempolimite,
        intentospermitidos=escenario_original.intentospermitidos,
        configuracionescenario=escenario_original.configuracionescenario or {},
    )
    db.add(nuevo_escenario)
    await db.commit()
    await db.refresh(nuevo_escenario)
    return nuevo_escenario


async def _actualizar_escenario_impl(
    idescenario: UUID,
    data: EscenarioUpdate,
    db: AsyncSession,
    current_user: Usuario,
):
    """Implementación compartida de actualización para PUT y PATCH."""
    _require_docente(current_user)

    result = await db.execute(select(Escenario).where(Escenario.idescenario == idescenario))
    escenario = result.scalar_one_or_none()
    if not escenario:
        raise HTTPException(status_code=404, detail="Escenario no encontrado")

    await _verificar_salon_del_docente(escenario.idsalon, current_user.docente.iddocente, db)

    campos = data.model_dump(exclude_unset=True)
    for campo, valor in campos.items():
        setattr(escenario, campo, valor)
    escenario.fechamodificacion = datetime.now(UTC).replace(tzinfo=None)

    await db.commit()
    await db.refresh(escenario)
    return escenario


@router.put("/{idescenario}", response_model=EscenarioRead)
async def actualizar_escenario_put(
    idescenario: UUID,
    data: EscenarioUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Edita un escenario (PUT). Solo el docente dueño del salón al que pertenece."""
    return await _actualizar_escenario_impl(idescenario, data, db, current_user)


@router.patch("/{idescenario}", response_model=EscenarioRead)
async def actualizar_escenario_patch(
    idescenario: UUID,
    data: EscenarioUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Edita un escenario (PATCH). Solo el docente dueño del salón al que pertenece."""
    return await _actualizar_escenario_impl(idescenario, data, db, current_user)


@router.delete("/{idescenario}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_escenario(
    idescenario: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Desactiva un escenario (soft delete). Solo el docente dueño."""
    _require_docente(current_user)

    result = await db.execute(select(Escenario).where(Escenario.idescenario == idescenario))
    escenario = result.scalar_one_or_none()
    if not escenario:
        raise HTTPException(status_code=404, detail="Escenario no encontrado")

    await _verificar_salon_del_docente(escenario.idsalon, current_user.docente.iddocente, db)

    escenario.activo = False
    escenario.fechamodificacion = datetime.now(UTC).replace(tzinfo=None)
    await db.commit()
