from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.docente import Docente
from app.models.usuario import Usuario
from app.schemas.docente import DocenteRead

router = APIRouter(prefix="/docentes", tags=["Docentes"])


@router.get("/", response_model=list[DocenteRead])
async def listar_docentes(
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    result = await db.execute(select(Docente))
    return result.scalars().all()


@router.get("/{iddocente}", response_model=DocenteRead)
async def obtener_docente(
    iddocente: UUID,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    result = await db.execute(select(Docente).where(Docente.iddocente == iddocente))
    docente = result.scalar_one_or_none()
    if not docente:
        raise HTTPException(status_code=404, detail="Docente no encontrado")
    return docente
