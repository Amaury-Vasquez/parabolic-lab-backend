import random
import string
from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.functions import coalesce

from app.dependencies import get_current_user, get_db
from app.models.alumno import Alumno
from app.models.alumno_en_salon import AlumnoEnSalon
from app.models.escenario import Escenario
from app.models.interaccion_escenario import InteraccionEscenario
from app.models.salon import Salon
from app.models.usuario import Usuario
from app.schemas.salon import (
    AgregarEstudianteRequest,
    EstudianteEnSalon,
    SalonCreate,
    SalonProgresoAlumno,
    SalonRead,
    SalonUpdate,
    SalonUpdateFull,
    SalonWithDetails,
)

router = APIRouter(prefix="/salones", tags=["Salones"])


def _generar_codigo(longitud: int = 6) -> str:
    """Genera un código de acceso alfanumérico en mayúsculas."""
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=longitud))


def _require_docente(current_user: Usuario) -> None:
    if current_user.tipousuario != "docente" or not current_user.docente:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los docentes pueden realizar esta acción",
        )


# ── READ ──────────────────────────────────────────────────────────────────────


@router.get("/me", response_model=list[SalonWithDetails])
async def mis_salones(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Devuelve los salones del usuario actual con detalles."""
    if current_user.tipousuario == "docente":
        if not current_user.docente:
            return []
        query = (
            select(Salon)
            .where(Salon.iddocente == current_user.docente.iddocente)
            .where(Salon.activo.is_(True))
            .options(selectinload(Salon.escenarios), selectinload(Salon.alumnos))
        )
    elif current_user.tipousuario == "alumno":
        if not current_user.alumno:
            return []
        query = (
            select(Salon)
            .join(AlumnoEnSalon, AlumnoEnSalon.idsalon == Salon.idsalon)
            .where(AlumnoEnSalon.idalumno == current_user.alumno.idalumno)
            .where(AlumnoEnSalon.activo.is_(True))
            .where(Salon.activo.is_(True))
            .options(selectinload(Salon.escenarios), selectinload(Salon.alumnos))
        )
    elif current_user.tipousuario == "admin":
        query = (
            select(Salon)
            .where(Salon.idinstitucion == current_user.idinstitucion)
            .where(Salon.activo.is_(True))
            .options(selectinload(Salon.escenarios), selectinload(Salon.alumnos))
        )
    else:
        return []

    result = await db.execute(query)
    salones = result.scalars().unique().all()
    return [
        SalonWithDetails(
            idsalon=s.idsalon,
            nombresalon=s.nombresalon,
            codigoacceso=s.codigoacceso,
            activo=s.activo,
            escenarios=[e.nombre for e in s.escenarios if e.activo],
            num_estudiantes=sum(1 for a in s.alumnos if a.activo),
        )
        for s in salones
    ]


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


# ── WRITE ─────────────────────────────────────────────────────────────────────


@router.post("/", response_model=SalonRead, status_code=status.HTTP_201_CREATED)
async def crear_salon(
    data: SalonCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Crea un nuevo salón. Solo docentes."""
    _require_docente(current_user)

    # Generar código único dentro de la institución
    for _ in range(10):
        codigo = _generar_codigo()
        existe = await db.execute(
            select(Salon).where(
                Salon.codigoacceso == codigo,
                Salon.idinstitucion == current_user.idinstitucion,
            )
        )
        if not existe.scalar_one_or_none():
            break

    salon = Salon(
        iddocente=current_user.docente.iddocente,
        idinstitucion=current_user.idinstitucion,
        codigoacceso=codigo,
        nombresalon=data.nombresalon,
    )
    db.add(salon)
    await db.commit()
    await db.refresh(salon)
    return salon


@router.put("/{idsalon}", response_model=SalonRead)
async def actualizar_salon(
    idsalon: UUID,
    data: SalonUpdateFull,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Edita un salón. Solo el docente dueño."""
    _require_docente(current_user)

    result = await db.execute(select(Salon).where(Salon.idsalon == idsalon))
    salon = result.scalar_one_or_none()
    if not salon:
        raise HTTPException(status_code=404, detail="Salon no encontrado")
    if salon.iddocente != current_user.docente.iddocente:
        raise HTTPException(status_code=403, detail="No tienes permiso para editar este salon")

    if data.nombresalon is not None:
        salon.nombresalon = data.nombresalon
    if data.activo is not None:
        salon.activo = data.activo
    salon.fechamodificacion = datetime.now(UTC).replace(tzinfo=None)

    await db.commit()
    await db.refresh(salon)
    return salon


@router.patch("/{idsalon}", response_model=SalonRead)
async def actualizar_nombre_salon(
    idsalon: UUID,
    data: SalonUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Actualiza solo el nombre de un salón via PATCH. Solo el docente dueño."""
    _require_docente(current_user)

    result = await db.execute(select(Salon).where(Salon.idsalon == idsalon))
    salon = result.scalar_one_or_none()
    if not salon:
        raise HTTPException(status_code=404, detail="Salon no encontrado")
    if salon.iddocente != current_user.docente.iddocente:
        raise HTTPException(status_code=403, detail="No tienes permiso para editar este salon")

    salon.nombresalon = data.nombresalon
    salon.fechamodificacion = datetime.now(UTC).replace(tzinfo=None)

    await db.commit()
    await db.refresh(salon)
    return salon


@router.delete("/{idsalon}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_salon(
    idsalon: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Desactiva un salón (soft delete). Solo el docente dueño."""
    _require_docente(current_user)

    result = await db.execute(select(Salon).where(Salon.idsalon == idsalon))
    salon = result.scalar_one_or_none()
    if not salon:
        raise HTTPException(status_code=404, detail="Salon no encontrado")
    if salon.iddocente != current_user.docente.iddocente:
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar este salon")

    salon.activo = False
    salon.fechamodificacion = datetime.now(UTC).replace(tzinfo=None)
    await db.commit()


@router.get("/{idsalon}/progreso", response_model=list[SalonProgresoAlumno])
async def obtener_progreso_salon(
    idsalon: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Obtiene el progreso de todos los alumnos en un salón.
    Solo el docente dueño del salón puede acceder.
    Retorna estadísticas agregadas de interacciones para cada alumno.
    """
    _require_docente(current_user)

    # Verificar que el salon existe y que el usuario es el dueño
    result = await db.execute(select(Salon).where(Salon.idsalon == idsalon))
    salon = result.scalar_one_or_none()
    if not salon:
        raise HTTPException(status_code=404, detail="Salon no encontrado")
    if salon.iddocente != current_user.docente.iddocente:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver el progreso de este salon")

    # Query para obtener estadísticas de alumnos con outer join para incluir alumnos sin interacciones
    query = (
        select(
            Alumno.idalumno,
            Usuario.nombre,
            Usuario.apellidopaterno,
            Usuario.apellidomaterno,
            coalesce(func.count(InteraccionEscenario.idinteraccion), 0).label("total_interacciones"),
            func.avg(InteraccionEscenario.puntuacion).label("promedio_puntuacion"),
            func.max(InteraccionEscenario.puntuacion).label("mejor_puntuacion"),
            coalesce(func.sum(InteraccionEscenario.intentosrealizados), 0).label("total_intentos"),
            coalesce(
                func.sum(
                    case(
                        (InteraccionEscenario.completado.is_(True), 1),
                        else_=0,
                    )
                ),
                0,
            ).label("escenarios_completados"),
            coalesce(func.sum(InteraccionEscenario.tiempototal) / 60.0, 0.0).label("tiempo_total_minutos"),
        )
        .join(AlumnoEnSalon, Alumno.idalumno == AlumnoEnSalon.idalumno)
        .join(Usuario, Alumno.idusuario == Usuario.idusuario)
        .outerjoin(InteraccionEscenario, Alumno.idalumno == InteraccionEscenario.idalumno)
        .where(AlumnoEnSalon.idsalon == idsalon)
        .where(AlumnoEnSalon.activo.is_(True))
        .group_by(
            Alumno.idalumno,
            Usuario.nombre,
            Usuario.apellidopaterno,
            Usuario.apellidomaterno,
        )
        .order_by(Usuario.nombre, Usuario.apellidopaterno)
    )

    result = await db.execute(query)
    rows = result.all()

    # Convertir rows a SalonProgresoAlumno objects
    return [
        SalonProgresoAlumno(
            idalumno=row.idalumno,
            nombre=row.nombre,
            apellidopaterno=row.apellidopaterno,
            apellidomaterno=row.apellidomaterno,
            total_interacciones=row.total_interacciones,
            promedio_puntuacion=row.promedio_puntuacion,
            mejor_puntuacion=row.mejor_puntuacion,
            total_intentos=row.total_intentos,
            escenarios_completados=row.escenarios_completados,
            tiempo_total_minutos=float(row.tiempo_total_minutos),
        )
        for row in rows
    ]


# ── GESTIÓN DE ESTUDIANTES ────────────────────────────────────────────────────


@router.get("/{idsalon}/estudiantes", response_model=list[EstudianteEnSalon])
async def listar_estudiantes_salon(
    idsalon: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Obtiene la lista de estudiantes en un salón con su información de progreso.
    Solo el docente dueño del salón puede acceder.
    """
    _require_docente(current_user)

    # Verificar que el salon existe y que el usuario es el dueño
    result = await db.execute(select(Salon).where(Salon.idsalon == idsalon))
    salon = result.scalar_one_or_none()
    if not salon:
        raise HTTPException(status_code=404, detail="Salon no encontrado")
    if salon.iddocente != current_user.docente.iddocente:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver los estudiantes de este salon")

    # Obtener el total de escenarios activos en el salón
    total_escenarios_result = await db.execute(
        select(func.count(Escenario.idescenario)).where(
            Escenario.idsalon == idsalon,
            Escenario.activo.is_(True),
        )
    )
    total_escenarios = total_escenarios_result.scalar() or 0

    # Query para obtener estudiantes con información de progreso
    query = (
        select(
            Alumno.idalumno,
            Usuario.nombre,
            Usuario.apellidopaterno,
            Usuario.apellidomaterno,
            Usuario.email,
            Usuario.ultimoacceso,
            coalesce(
                func.count(
                    case(
                        (InteraccionEscenario.completado.is_(True), 1),
                        else_=None,
                    )
                ),
                0,
            ).label("escenarios_completados"),
        )
        .join(AlumnoEnSalon, Alumno.idalumno == AlumnoEnSalon.idalumno)
        .join(Usuario, Alumno.idusuario == Usuario.idusuario)
        .outerjoin(InteraccionEscenario, Alumno.idalumno == InteraccionEscenario.idalumno)
        .where(AlumnoEnSalon.idsalon == idsalon)
        .where(AlumnoEnSalon.activo.is_(True))
        .group_by(
            Alumno.idalumno,
            Usuario.nombre,
            Usuario.apellidopaterno,
            Usuario.apellidomaterno,
            Usuario.email,
            Usuario.ultimoacceso,
        )
        .order_by(Usuario.nombre, Usuario.apellidopaterno)
    )

    result = await db.execute(query)
    rows = result.all()

    return [
        EstudianteEnSalon(
            idalumno=row.idalumno,
            nombre=row.nombre,
            apellidopaterno=row.apellidopaterno,
            apellidomaterno=row.apellidomaterno,
            email=row.email,
            ultimo_acceso=row.ultimoacceso,
            escenarios_completados=row.escenarios_completados,
            total_escenarios=total_escenarios,
        )
        for row in rows
    ]


@router.post("/{idsalon}/agregar-estudiante", status_code=status.HTTP_201_CREATED)
async def agregar_estudiante_salon(
    idsalon: UUID,
    data: AgregarEstudianteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Agrega un estudiante a un salón por su email.
    Solo el docente dueño del salón puede realizar esta acción.
    Retorna la información del alumno agregado.
    """
    _require_docente(current_user)

    # Verificar que el salon existe y que el usuario es el dueño
    result = await db.execute(select(Salon).where(Salon.idsalon == idsalon))
    salon = result.scalar_one_or_none()
    if not salon:
        raise HTTPException(status_code=404, detail="Salon no encontrado")
    if salon.iddocente != current_user.docente.iddocente:
        raise HTTPException(status_code=403, detail="No tienes permiso para agregar estudiantes a este salon")

    # Buscar al usuario por email
    result = await db.execute(select(Usuario).where(Usuario.email == data.correo))
    usuario = result.scalar_one_or_none()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado con ese email")

    # Verificar que el usuario es alumno
    if usuario.tipousuario != "alumno" or not usuario.alumno:
        raise HTTPException(status_code=422, detail="El usuario no es un alumno valido")

    # Verificar que el alumno no esté ya en el salón
    result = await db.execute(
        select(AlumnoEnSalon).where(
            AlumnoEnSalon.idalumno == usuario.alumno.idalumno,
            AlumnoEnSalon.idsalon == idsalon,
        )
    )
    alumno_en_salon = result.scalar_one_or_none()
    if alumno_en_salon:
        if alumno_en_salon.activo:
            raise HTTPException(
                status_code=409,
                detail="El estudiante ya está inscrito en este salon",
            )
        else:
            # Reactivar si estaba inactivo
            alumno_en_salon.activo = True
            await db.commit()
            await db.refresh(alumno_en_salon)
            return {
                "mensaje": "Estudiante reactivado en el salon",
                "idalumno": usuario.alumno.idalumno,
                "nombre": usuario.nombre,
                "email": usuario.email,
            }

    # Crear la relación alumno-salon
    nuevo_alumno_en_salon = AlumnoEnSalon(
        idalumno=usuario.alumno.idalumno,
        idsalon=idsalon,
    )
    db.add(nuevo_alumno_en_salon)
    await db.commit()
    await db.refresh(nuevo_alumno_en_salon)

    return {
        "mensaje": "Estudiante agregado al salon correctamente",
        "idalumno": usuario.alumno.idalumno,
        "nombre": usuario.nombre,
        "email": usuario.email,
    }


@router.delete("/{idsalon}/estudiantes/{idalumno}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_estudiante_salon(
    idsalon: UUID,
    idalumno: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Elimina (desactiva) un estudiante de un salón.
    Solo el docente dueño del salón puede realizar esta acción.
    """
    _require_docente(current_user)

    # Verificar que el salon existe y que el usuario es el dueño
    result = await db.execute(select(Salon).where(Salon.idsalon == idsalon))
    salon = result.scalar_one_or_none()
    if not salon:
        raise HTTPException(status_code=404, detail="Salon no encontrado")
    if salon.iddocente != current_user.docente.iddocente:
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar estudiantes de este salon")

    # Buscar la relación alumno-salon
    result = await db.execute(
        select(AlumnoEnSalon).where(
            AlumnoEnSalon.idalumno == idalumno,
            AlumnoEnSalon.idsalon == idsalon,
        )
    )
    alumno_en_salon = result.scalar_one_or_none()
    if not alumno_en_salon:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado en este salon")

    # Soft delete: desactivar la relación
    alumno_en_salon.activo = False
    await db.commit()
