from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.actividad_alumno import ActividadAlumno
from app.models.usuario import Usuario
from app.schemas.actividad_alumno import (
    ActividadAlumnoCreate,
    ActividadAlumnoRead,
    ActividadAlumnoUpdate,
)

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


@router.post("/", response_model=ActividadAlumnoRead, status_code=201)
async def crear_actividad_alumno(
    data: ActividadAlumnoCreate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    registro = ActividadAlumno(
        idactividad=data.idactividad,
        idalumno=data.idalumno,
    )
    db.add(registro)
    await db.commit()
    await db.refresh(registro)
    return registro


@router.patch("/{idactividadalumno}", response_model=ActividadAlumnoRead)
async def actualizar_actividad_alumno(
    idactividadalumno: UUID,
    data: ActividadAlumnoUpdate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    result = await db.execute(select(ActividadAlumno).where(ActividadAlumno.idactividadalumno == idactividadalumno))
    registro = result.scalar_one_or_none()
    if not registro:
        raise HTTPException(status_code=404, detail="Actividad de alumno no encontrada")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(registro, field, value)

    await db.commit()
    await db.refresh(registro)
    return registro
