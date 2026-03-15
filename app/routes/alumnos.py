from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.alumno import Alumno
from app.models.usuario import Usuario
from app.schemas.alumno import AlumnoRead

router = APIRouter(prefix="/alumnos", tags=["Alumnos"])


@router.get("/", response_model=list[AlumnoRead])
async def listar_alumnos(
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    result = await db.execute(select(Alumno))
    return result.scalars().all()


@router.get("/{idalumno}", response_model=AlumnoRead)
async def obtener_alumno(
    idalumno: UUID,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    result = await db.execute(select(Alumno).where(Alumno.idalumno == idalumno))
    alumno = result.scalar_one_or_none()
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    return alumno
