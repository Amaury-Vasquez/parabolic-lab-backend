from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.interaccion_escenario import InteraccionEscenario
from app.models.usuario import Usuario
from app.schemas.interaccion_escenario import (
    InteraccionEscenarioCreate,
    InteraccionEscenarioRead,
    InteraccionEscenarioUpdate,
)

router = APIRouter(prefix="/interacciones-escenario", tags=["InteraccionesEscenario"])


@router.get("/", response_model=list[InteraccionEscenarioRead])
async def listar_interacciones_escenario(
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    result = await db.execute(select(InteraccionEscenario))
    return result.scalars().all()


@router.get("/{idinteraccion}", response_model=InteraccionEscenarioRead)
async def obtener_interaccion_escenario(
    idinteraccion: UUID,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    result = await db.execute(select(InteraccionEscenario).where(InteraccionEscenario.idinteraccion == idinteraccion))
    interaccion = result.scalar_one_or_none()
    if not interaccion:
        raise HTTPException(status_code=404, detail="Interaccion de escenario no encontrada")
    return interaccion


@router.post("/", response_model=InteraccionEscenarioRead, status_code=201)
async def crear_interaccion_escenario(
    data: InteraccionEscenarioCreate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    interaccion = InteraccionEscenario(
        idescenario=data.idescenario,
        idalumno=data.idalumno,
    )
    db.add(interaccion)
    await db.commit()
    await db.refresh(interaccion)
    return interaccion


@router.patch("/{idinteraccion}", response_model=InteraccionEscenarioRead)
async def actualizar_interaccion_escenario(
    idinteraccion: UUID,
    data: InteraccionEscenarioUpdate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    result = await db.execute(select(InteraccionEscenario).where(InteraccionEscenario.idinteraccion == idinteraccion))
    interaccion = result.scalar_one_or_none()
    if not interaccion:
        raise HTTPException(status_code=404, detail="Interaccion de escenario no encontrada")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(interaccion, field, value)

    await db.commit()
    await db.refresh(interaccion)
    return interaccion
