import httpx
import jwt
from fastapi import HTTPException, status
from jwt import PyJWKClient

from app.config import settings

STACK_AUTH_BASE = "https://api.stack-auth.com/api/v1"

_jwks_client = PyJWKClient(f"{STACK_AUTH_BASE}/projects/{settings.STACK_AUTH_PROJECT_ID}/.well-known/jwks.json")

_server_headers = {
    "x-stack-access-type": "server",
    "x-stack-project-id": settings.STACK_AUTH_PROJECT_ID,
    "x-stack-secret-server-key": settings.STACK_AUTH_SECRET_SERVER_KEY,
    "Content-Type": "application/json",
}


def verify_access_token(access_token: str) -> dict:
    try:
        signing_key = _jwks_client.get_signing_key_from_jwt(access_token)
        payload = jwt.decode(
            access_token,
            signing_key.key,
            algorithms=["ES256"],
            audience=settings.STACK_AUTH_PROJECT_ID,
        )
        return payload
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de acceso invalido o expirado",
        )


async def sign_up(email: str, password: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{STACK_AUTH_BASE}/auth/password/sign-up",
            headers=_server_headers,
            json={"email": email, "password": password},
        )
    if response.status_code != 200:
        detail = response.json() if response.status_code < 500 else "Error en Stack Auth"
        raise HTTPException(status_code=response.status_code, detail=detail)
    return response.json()


async def sign_in(email: str, password: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{STACK_AUTH_BASE}/auth/password/sign-in",
            headers=_server_headers,
            json={"email": email, "password": password},
        )
    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales invalidas",
        )
    return response.json()


async def get_stack_user(user_id: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{STACK_AUTH_BASE}/users/{user_id}",
            headers=_server_headers,
        )
    if response.status_code != 200:
        raise HTTPException(status_code=404, detail="Usuario no encontrado en Stack Auth")
    return response.json()


async def update_stack_user(user_id: str, data: dict) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{STACK_AUTH_BASE}/users/{user_id}",
            headers=_server_headers,
            json=data,
        )
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error al actualizar usuario")
    return response.json()


async def refresh_session(refresh_token: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{STACK_AUTH_BASE}/auth/sessions/current/refresh",
            headers={
                **_server_headers,
                "x-stack-refresh-token": refresh_token,
            },
        )
    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo renovar la sesión",
        )
    return response.json()


async def delete_stack_user(user_id: str) -> None:
    async with httpx.AsyncClient() as client:
        response = await client.request(
            "DELETE",
            f"{STACK_AUTH_BASE}/users/{user_id}",
            headers=_server_headers,
            content="{}",
        )
    if response.status_code not in (200, 204):
        raise HTTPException(status_code=response.status_code, detail="Error al eliminar usuario")
