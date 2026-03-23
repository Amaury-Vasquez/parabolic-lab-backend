import json
from datetime import datetime

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import stack_auth
from app.dependencies import get_current_user, get_db
from app.models.admin import Admin
from app.models.alumno import Alumno
from app.models.docente import Docente
from app.models.institucion import Institucion
from app.models.usuario import Usuario
from app.schemas.auth import (
    AuthResponse,
    LoginRequest,
    RegisterInstitucionAdmin,
    RegisterRequest,
    UpdateProfileRequest,
    UserProfile,
    VerifyResponse,
)

router = APIRouter(prefix="/auth", tags=["Autenticacion"])


async def _sync_user_to_neon_auth(db: AsyncSession, auth_id: str) -> None:
    """Obtiene el usuario de Stack Auth e inserta su JSON en neon_auth.users_sync.

    La tabla users_sync tiene columnas generadas (id, name, email, created_at)
    derivadas del campo raw_json, que espera el formato de usuario de Stack Auth.
    """
    user_data = await stack_auth.get_stack_user(auth_id)
    await db.execute(
        text(
            "INSERT INTO neon_auth.users_sync (raw_json) VALUES (:raw_json) "
            "ON CONFLICT (id) DO UPDATE SET raw_json = EXCLUDED.raw_json"
        ),
        {"raw_json": json.dumps(user_data)},
    )


@router.post("/register/institucion", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register_institucion_admin(data: RegisterInstitucionAdmin, db: AsyncSession = Depends(get_db)):
    """Crea una institucion junto con su usuario admin de forma atomica."""
    # 1. Crear usuario en Stack Auth
    auth_result = await stack_auth.sign_up(data.email, data.password)
    auth_id = auth_result["user_id"]

    try:
        # 2. Sincronizar usuario de Stack Auth a neon_auth.users_sync
        await _sync_user_to_neon_auth(db, auth_id)

        # 3. Crear la institucion
        institucion = Institucion(
            clavect=data.clavect,
            nombre=data.nombre_institucion,
            direccion=data.direccion,
            colonia=data.colonia,
            municipio=data.municipio,
            estado=data.estado,
            codigopostal=data.codigopostal,
            email=data.email_institucion,
            telefono=data.telefono,
        )
        db.add(institucion)
        await db.flush()

        # 3. Crear el usuario admin
        usuario = Usuario(
            authid=auth_id,
            email=data.email,
            nombre=data.nombre,
            idinstitucion=institucion.idinstitucion,
            apellidopaterno=data.apellidopaterno,
            apellidomaterno=data.apellidomaterno,
            tipousuario="admin",
        )
        db.add(usuario)
        await db.flush()

        # 4. Crear registro de admin
        admin = Admin(idusuario=usuario.idusuario)
        db.add(admin)

        await db.commit()
        await db.refresh(usuario)
    except Exception as e:
        await db.rollback()
        try:
            await stack_auth.delete_stack_user(auth_id)
        except Exception:
            pass
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear la institucion y el usuario admin: {e}",
        )

    return AuthResponse(
        access_token=auth_result["access_token"],
        refresh_token=auth_result["refresh_token"],
        user_id=auth_id,
        idusuario=usuario.idusuario,
        tipousuario=usuario.tipousuario,
    )


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    if data.tipousuario not in ("alumno", "docente", "admin"):
        raise HTTPException(status_code=400, detail="tipousuario debe ser 'alumno', 'docente' o 'admin'")

    if data.tipousuario == "alumno" and not data.matricula:
        raise HTTPException(status_code=400, detail="matricula es requerida para alumnos")

    # 1. Crear usuario en Stack Auth
    auth_result = await stack_auth.sign_up(data.email, data.password)
    auth_id = auth_result["user_id"]

    try:
        # 2. Sincronizar usuario de Stack Auth a neon_auth.users_sync
        await _sync_user_to_neon_auth(db, auth_id)

        # 3. Crear registro en tabla usuario
        usuario = Usuario(
            authid=auth_id,
            email=data.email,
            nombre=data.nombre,
            idinstitucion=data.idinstitucion,
            apellidopaterno=data.apellidopaterno,
            apellidomaterno=data.apellidomaterno,
            tipousuario=data.tipousuario,
        )
        db.add(usuario)
        await db.flush()

        # 3. Crear registro de rol segun tipo
        if data.tipousuario == "alumno":
            alumno = Alumno(
                idusuario=usuario.idusuario,
                matricula=data.matricula,
            )
            db.add(alumno)
        elif data.tipousuario == "docente":
            docente = Docente(
                idusuario=usuario.idusuario,
                gradoacademico=data.gradoacademico,
            )
            db.add(docente)
        elif data.tipousuario == "admin":
            admin = Admin(idusuario=usuario.idusuario)
            db.add(admin)

        await db.commit()
        await db.refresh(usuario)
    except Exception as e:
        await db.rollback()
        try:
            await stack_auth.delete_stack_user(auth_id)
        except Exception:
            pass
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear el usuario en la base de datos: {e}",
        )

    return AuthResponse(
        access_token=auth_result["access_token"],
        refresh_token=auth_result["refresh_token"],
        user_id=auth_id,
        idusuario=usuario.idusuario,
        tipousuario=usuario.tipousuario,
    )


@router.post("/login", response_model=AuthResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    auth_result = await stack_auth.sign_in(data.email, data.password)
    auth_id = auth_result["user_id"]

    result = await db.execute(select(Usuario).where(Usuario.authid == auth_id))
    usuario = result.scalar_one_or_none()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado en la base de datos")

    # Actualizar ultimo acceso
    usuario.ultimoacceso = datetime.utcnow()
    await db.commit()

    return AuthResponse(
        access_token=auth_result["access_token"],
        refresh_token=auth_result["refresh_token"],
        user_id=auth_id,
        idusuario=usuario.idusuario,
        tipousuario=usuario.tipousuario,
    )


@router.post("/verify", response_model=VerifyResponse)
async def verify_token(
    x_stack_access_token: str = Header(..., alias="x-stack-access-token"),
    x_stack_refresh_token: str | None = Header(None, alias="x-stack-refresh-token"),
):
    """Verifica el token de acceso localmente (JWT decode, sin DB).

    Si el token es invalido o expirado y se proporciona un refresh token,
    intenta renovar la sesión con Stack Auth.
    """
    try:
        stack_auth.verify_access_token(x_stack_access_token)
        return VerifyResponse(valid=True)
    except HTTPException:
        if not x_stack_refresh_token:
            raise
        new_tokens = await stack_auth.refresh_session(x_stack_refresh_token)
        return VerifyResponse(valid=True, access_token=new_tokens["access_token"])


@router.get("/me", response_model=UserProfile)
async def get_me(current_user: Usuario = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserProfile)
async def update_me(
    data: UpdateProfileRequest,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Actualizar campos en Stack Auth si email o password cambian
    stack_update: dict = {}
    if data.email is not None:
        stack_update["primary_email"] = data.email
        current_user.email = data.email
    if data.password is not None:
        stack_update["password"] = data.password
    if stack_update:
        await stack_auth.update_stack_user(current_user.authid, stack_update)

    # Actualizar campos locales
    if data.nombre is not None:
        current_user.nombre = data.nombre
    if data.apellidopaterno is not None:
        current_user.apellidopaterno = data.apellidopaterno
    if data.apellidomaterno is not None:
        current_user.apellidomaterno = data.apellidomaterno

    current_user.fechamodificacion = datetime.utcnow()
    await db.commit()
    await db.refresh(current_user)

    return current_user


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_me(
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    auth_id = current_user.authid
    # Eliminar de Stack Auth
    await stack_auth.delete_stack_user(auth_id)
    # Eliminar de neon_auth.users_sync (ON DELETE CASCADE elimina el usuario local)
    await db.execute(
        text("DELETE FROM neon_auth.users_sync WHERE id = :id"),
        {"id": auth_id},
    )
    await db.commit()
