from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import coalesce

from app.dependencies import get_current_user, get_db
from app.models.alumno import Alumno
from app.models.alumno_en_salon import AlumnoEnSalon
from app.models.docente import Docente
from app.models.interaccion_escenario import InteraccionEscenario
from app.models.salon import Salon
from app.models.usuario import Usuario
from app.schemas.docente import DocenteRead, EstudianteGlobalStats

router = APIRouter(prefix="/docentes", tags=["Docentes"])


def _require_docente(current_user: Usuario) -> None:
    """Verifica que el usuario actual es un docente."""
    if current_user.tipousuario != "docente" or not current_user.docente:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los docentes pueden realizar esta acción",
        )


@router.get("/me/estudiantes-global", response_model=list[EstudianteGlobalStats])
async def obtener_estudiantes_global(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    sort_by: str = "nombre",  # nombre | promedio | interacciones | salon
    order: str = "asc",  # asc | desc
    idsalon: UUID | None = None,  # Filtrar por salón específico (opcional)
):
    """
    Obtiene todos los estudiantes de todos los salones del docente actual.
    Devuelve una lista única de alumnos con estadísticas globales de interacciones.
    
    Query parameters:
    - sort_by: Campo por el que ordenar (nombre, promedio, interacciones, salon) - default: nombre
    - order: Dirección de ordenamiento (asc, desc) - default: asc
    - idsalon: UUID opcional para filtrar por un salón específico
    
    Cada estudiante se lista una sola vez, asociado a su salón.
    
    Responde con:
    - nombre, apellidopaterno, apellidomaterno
    - email, matricula
    - nombresalon (del salón al que pertenece)
    - Estadísticas: total_interacciones, promedio_puntuacion, mejor_puntuacion, 
      total_intentos, escenarios_completados, tiempo_total_minutos
    - progreso_total (calculado como promedio de puntuación normalizado)
    """
    _require_docente(current_user)

    # Obtener todos los salones del docente actual
    salones_query = select(Salon).where(Salon.iddocente == current_user.docente.iddocente)
    result = await db.execute(salones_query)
    salones = result.scalars().all()

    if not salones:
        return []

    idsalones = [s.idsalon for s in salones]

    # Si se proporciona un idsalon, verificar que pertenece al docente
    if idsalon:
        if idsalon not in idsalones:
            raise HTTPException(status_code=403, detail="No tienes acceso a este salón")
        idsalones = [idsalon]

    # Query para obtener todos los alumnos de estos salones con estadísticas de progreso
    query = (
        select(
            Alumno.idalumno,
            Alumno.idusuario,
            Alumno.matricula,
            Usuario.nombre,
            Usuario.apellidopaterno,
            Usuario.apellidomaterno,
            Usuario.email,
            Salon.idsalon,
            Salon.nombresalon,
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
        .join(Salon, AlumnoEnSalon.idsalon == Salon.idsalon)
        .outerjoin(InteraccionEscenario, Alumno.idalumno == InteraccionEscenario.idalumno)
        .where(AlumnoEnSalon.idsalon.in_(idsalones))
        .where(AlumnoEnSalon.activo.is_(True))
        .group_by(
            Alumno.idalumno,
            Alumno.idusuario,
            Alumno.matricula,
            Usuario.nombre,
            Usuario.apellidopaterno,
            Usuario.apellidomaterno,
            Usuario.email,
            Salon.idsalon,
            Salon.nombresalon,
        )
    )

    # Aplicar ordenamiento basado en sort_by y order
    desc_order = order.lower() == "desc"

    if sort_by == "promedio":
        query = query.order_by(
            func.avg(InteraccionEscenario.puntuacion).desc() if desc_order
            else func.avg(InteraccionEscenario.puntuacion).asc()
        )
    elif sort_by == "interacciones":
        query = query.order_by(
            func.count(InteraccionEscenario.idinteraccion).desc() if desc_order
            else func.count(InteraccionEscenario.idinteraccion).asc()
        )
    elif sort_by == "salon":
        query = query.order_by(
            Salon.nombresalon.desc() if desc_order else Salon.nombresalon.asc()
        )
    else:  # nombre (default)
        query = query.order_by(
            Usuario.nombre.desc() if desc_order else Usuario.nombre.asc(),
            Usuario.apellidopaterno.desc() if desc_order else Usuario.apellidopaterno.asc()
        )

    result = await db.execute(query)
    rows = result.all()

    # Convertir rows a EstudianteGlobalStats objects
    # El progreso_total se calcula como el promedio de puntuación normalizado (0-100)
    estudiantes = []
    for row in rows:
        # Calcular progreso como porcentaje: si promedio_puntuacion es None, es 0
        progreso = float(row.promedio_puntuacion) if row.promedio_puntuacion else 0.0

        estudiante = EstudianteGlobalStats(
            idalumno=row.idalumno,
            idusuario=row.idusuario,
            nombre=row.nombre,
            apellidopaterno=row.apellidopaterno,
            apellidomaterno=row.apellidomaterno,
            email=row.email,
            matricula=row.matricula,
            nombresalon=row.nombresalon,
            total_interacciones=row.total_interacciones,
            promedio_puntuacion=row.promedio_puntuacion,
            mejor_puntuacion=row.mejor_puntuacion,
            total_intentos=row.total_intentos,
            escenarios_completados=row.escenarios_completados,
            tiempo_total_minutos=float(row.tiempo_total_minutos),
            progreso_total=progreso,
        )
        estudiantes.append(estudiante)

    return estudiantes


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
