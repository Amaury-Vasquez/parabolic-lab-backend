from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.actividad_alumno import ActividadAlumno
from app.models.usuario import Usuario
from app.schemas.actividad_alumno import ActividadAlumnoRead

router = APIRouter(prefix="/actividades-alumno", tags=["ActividadesAlumno"])


@router.get("/", response_model=list[ActividadAlumnoRead])
async def listar_actividades_alumno(
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    result = await db.execute(select(ActividadAlumno))
    return result.scalars().all()


@router.get("/{idactividadalumno}", response_model=ActividadAlumnoRead)
async def obtener_actividad_alumno(
    idactividadalumno: UUID,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    result = await db.execute(select(ActividadAlumno).where(ActividadAlumno.idactividadalumno == idactividadalumno))
    registro = result.scalar_one_or_none()
    if not registro:
        raise HTTPException(status_code=404, detail="Actividad de alumno no encontrada")
    return registro
