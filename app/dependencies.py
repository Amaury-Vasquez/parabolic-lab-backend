from collections.abc import AsyncGenerator

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth.stack_auth import verify_access_token
from app.database import async_session
from app.models.usuario import Usuario


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


async def get_current_user(
    x_stack_access_token: str = Header(..., alias="x-stack-access-token"),
    db: AsyncSession = Depends(get_db),
) -> Usuario:
    payload = verify_access_token(x_stack_access_token)
    auth_id = payload.get("sub")
    if not auth_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido: sin identificador de usuario",
        )
    result = await db.execute(
        select(Usuario)
        .where(Usuario.authid == auth_id)
        .options(selectinload(Usuario.docente), selectinload(Usuario.alumno))
    )
    usuario = result.scalar_one_or_none()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado en la base de datos",
        )
    return usuario
