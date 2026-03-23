from uuid import UUID

from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    nombre: str
    apellidopaterno: str
    apellidomaterno: str | None = None
    idinstitucion: UUID
    tipousuario: str  # 'alumno' | 'docente' | 'admin'
    # Campos opcionales segun tipo de usuario
    matricula: str | None = None  # requerido si tipousuario == 'alumno'
    gradoacademico: str | None = None  # opcional si tipousuario == 'docente'


class RegisterInstitucionAdmin(BaseModel):
    # Datos de la institucion
    clavect: str | None = None
    nombre_institucion: str
    direccion: str | None = None
    colonia: str | None = None
    municipio: str | None = None
    estado: str | None = None
    codigopostal: str | None = None
    email_institucion: EmailStr
    telefono: str
    # Datos del admin
    nombre: str
    email: EmailStr
    password: str
    apellidopaterno: str
    apellidomaterno: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    user_id: str
    idusuario: UUID
    tipousuario: str


class UserProfile(BaseModel):
    idusuario: UUID
    authid: str
    email: str
    nombre: str
    apellidopaterno: str
    apellidomaterno: str | None = None
    tipousuario: str
    idinstitucion: UUID
    activo: bool | None = None

    model_config = {"from_attributes": True}


class UpdateProfileRequest(BaseModel):
    nombre: str | None = None
    apellidopaterno: str | None = None
    apellidomaterno: str | None = None
    email: str | None = None
    password: str | None = None


class VerifyResponse(BaseModel):
    valid: bool
    access_token: str | None = None
