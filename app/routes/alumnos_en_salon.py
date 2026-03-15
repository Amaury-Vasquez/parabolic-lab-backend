from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.alumno_en_salon import AlumnoEnSalon
from app.models.usuario import Usuario
from app.schemas.alumno_en_salon import AlumnoEnSalonRead

router = APIRouter(prefix="/alumnos-en-salon", tags=["AlumnosEnSalon"])


@router.get("/", response_model=list[AlumnoEnSalonRead])
async def listar_alumnos_en_salon(
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    result = await db.execute(select(AlumnoEnSalon))
    return result.scalars().all()


@router.get("/{idalumno}/{idsalon}", response_model=AlumnoEnSalonRead)
async def obtener_alumno_en_salon(
    idalumno: UUID,
    idsalon: UUID,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    result = await db.execute(
        select(AlumnoEnSalon).where(
            AlumnoEnSalon.idalumno == idalumno,
            AlumnoEnSalon.idsalon == idsalon,
        )
    )
    registro = result.scalar_one_or_none()
    if not registro:
        raise HTTPException(status_code=404, detail="Registro de alumno en salon no encontrado")
    return registro
