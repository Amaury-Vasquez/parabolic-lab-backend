from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.alumno import Alumno
from app.models.alumno_en_salon import AlumnoEnSalon
from app.models.salon import Salon
from app.models.usuario import Usuario
from app.schemas.alumno_en_salon import AlumnoEnSalonJoin, AlumnoEnSalonRead

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


@router.post("/unirse", response_model=AlumnoEnSalonRead, status_code=201)
async def unirse_a_salon(
    data: AlumnoEnSalonJoin,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    salon_result = await db.execute(
        select(Salon).where(Salon.codigoacceso == data.codigoacceso)
    )
    salon = salon_result.scalar_one_or_none()
    if not salon:
        raise HTTPException(status_code=404, detail="Salon no encontrado")

    alumno_result = await db.execute(
        select(Alumno).where(Alumno.idusuario == current_user.idusuario)
    )
    alumno = alumno_result.scalar_one_or_none()
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")

    existing = await db.execute(
        select(AlumnoEnSalon).where(
            AlumnoEnSalon.idalumno == alumno.idalumno,
            AlumnoEnSalon.idsalon == salon.idsalon,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Ya estás inscrito en este salón")

    registro = AlumnoEnSalon(idalumno=alumno.idalumno, idsalon=salon.idsalon)
    db.add(registro)
    await db.commit()
    await db.refresh(registro)
    return registro
