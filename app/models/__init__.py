from app.models.actividad_alumno import ActividadAlumno
from app.models.actividad_interactiva import ActividadInteractiva
from app.models.admin import Admin
from app.models.alumno import Alumno
from app.models.alumno_en_salon import AlumnoEnSalon
from app.models.docente import Docente
from app.models.escenario import Escenario
from app.models.escenario_en_actividad import EscenarioEnActividad
from app.models.institucion import Institucion
from app.models.interaccion_escenario import InteraccionEscenario
from app.models.salon import Salon
from app.models.usuario import Usuario

__all__ = [
    "Institucion",
    "Usuario",
    "Alumno",
    "Admin",
    "Docente",
    "Salon",
    "AlumnoEnSalon",
    "Escenario",
    "ActividadInteractiva",
    "ActividadAlumno",
    "InteraccionEscenario",
    "EscenarioEnActividad",
]
