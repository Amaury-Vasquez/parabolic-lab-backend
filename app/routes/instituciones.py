from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.institucion import Institucion
from app.models.usuario import Usuario
from app.schemas.institucion import InstitucionRead

router = APIRouter(prefix="/instituciones", tags=["Instituciones"])


@router.get("/", response_model=list[InstitucionRead])
async def listar_instituciones(
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    result = await db.execute(select(Institucion))
    return result.scalars().all()


@router.get("/{idinstitucion}", response_model=InstitucionRead)
async def obtener_institucion(
    idinstitucion: UUID,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    result = await db.execute(select(Institucion).where(Institucion.idinstitucion == idinstitucion))
    institucion = result.scalar_one_or_none()
    if not institucion:
        raise HTTPException(status_code=404, detail="Institucion no encontrada")
    return institucion
