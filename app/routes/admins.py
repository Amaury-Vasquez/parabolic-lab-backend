from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.admin import Admin
from app.models.usuario import Usuario
from app.schemas.admin import AdminRead

router = APIRouter(prefix="/admins", tags=["Admins"])


@router.get("/", response_model=list[AdminRead])
async def listar_admins(
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    result = await db.execute(select(Admin))
    return result.scalars().all()


@router.get("/{idadmin}", response_model=AdminRead)
async def obtener_admin(
    idadmin: UUID,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    result = await db.execute(select(Admin).where(Admin.idadmin == idadmin))
    admin = result.scalar_one_or_none()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin no encontrado")
    return admin
