from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.salon import Salon
from app.models.usuario import Usuario
from app.schemas.salon import SalonRead

router = APIRouter(prefix="/salones", tags=["Salones"])


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
