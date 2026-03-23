from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes import (
    actividades_alumno,
    actividades_interactivas,
    admins,
    alumnos,
    alumnos_en_salon,
    auth,
    docentes,
    escenarios,
    escenarios_en_actividad,
    instituciones,
    interacciones_escenario,
    salones,
    usuarios,
)

app = FastAPI(
    title="Parabolic Lab API",
    description="API para la plataforma educativa de tiro parabolico",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_PREFIX = "/api/v1"

app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(instituciones.router, prefix=API_PREFIX)
app.include_router(usuarios.router, prefix=API_PREFIX)
app.include_router(alumnos.router, prefix=API_PREFIX)
app.include_router(admins.router, prefix=API_PREFIX)
app.include_router(docentes.router, prefix=API_PREFIX)
app.include_router(salones.router, prefix=API_PREFIX)
app.include_router(alumnos_en_salon.router, prefix=API_PREFIX)
app.include_router(escenarios.router, prefix=API_PREFIX)
app.include_router(actividades_interactivas.router, prefix=API_PREFIX)
app.include_router(actividades_alumno.router, prefix=API_PREFIX)
app.include_router(interacciones_escenario.router, prefix=API_PREFIX)
app.include_router(escenarios_en_actividad.router, prefix=API_PREFIX)


@app.get("/")
async def health_check():
    return {"status": "ok", "service": "parabolic-lab-backend"}
