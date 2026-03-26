from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

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

CORS_ORIGINS = [
    "http://localhost:3000",
    "https://parabolic-lab-frontend.vercel.app",
    "https://paraboliclab.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
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


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    schema["components"]["securitySchemes"] = {
        "StackAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "x-stack-access-token",
        }
    }
    for path in schema["paths"].values():
        for operation in path.values():
            operation["security"] = [{"StackAuth": []}]
    app.openapi_schema = schema
    return schema


app.openapi = custom_openapi


@app.get("/")
async def health_check():
    return {"status": "ok", "service": "parabolic-lab-backend"}