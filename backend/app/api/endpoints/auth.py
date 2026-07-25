# -*- coding: utf-8 -*-
"""
auth.py — Endpoints HTTP para el flujo de autenticación (Paso 1 y Paso 2).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.auth import LoginRequest, TempTokenResponse, RoleSelectRequest, TokenResponse, RefreshTokenRequest, LogoutRequest
from app.schemas.user import UserCreate
from app.services.auth_service import AuthService
from app.services.user_service import UserService

router = APIRouter()


@router.post(
    "/login", 
    response_model=TempTokenResponse,
    summary="Paso 1 de Login — Autenticación y obtención de roles"
)
async def login_step1(
    obj_in: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Recibe credenciales de usuario. Si son válidas, emite un TempToken
    de corta duración (5 min) junto con la lista de roles del usuario.
    
    Implementa seguridad Shift-Left: Mensaje de error genérico para evitar enumeración de usuarios.
    """
    res = await AuthService.login_step1(db, obj_in)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos"  # Mensaje genérico
        )
    return res


@router.post(
    "/select-role", 
    response_model=TokenResponse,
    summary="Paso 2 de Login — Selección de rol y generación de JWT"
)
async def select_role_step2(
    obj_in: RoleSelectRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Recibe el TempToken (Paso 1) y el UUID del rol seleccionado.
    Verifica la asignación del rol y emite los tokens definitivos:
    Access Token (JWT con claims del rol) y Refresh Token.
    """
    res = await AuthService.select_role_step2(db, obj_in.temp_token, obj_in.role_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token temporal inválido, expirado o rol no permitido"
        )
    return res


@router.post(
    "/refresh-token", 
    response_model=TokenResponse,
    summary="Renovación de Access Token mediante Refresh Token"
)
async def refresh_token(
    obj_in: RefreshTokenRequest,
    role_id: str,  # Se provee el rol activo actual para re-verificar autorización
    db: AsyncSession = Depends(get_db)
):
    """
    Valida el Refresh Token y re-verifica que la asignación del rol siga activa.
    Emite un nuevo par de tokens.
    """
    res = await AuthService.refresh_access_token(db, obj_in.refresh_token, role_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido, expirado o rol inhabilitado"
        )
    return res


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Cierre de sesión — Invalida los tokens activos del usuario"
)
async def logout(
    obj_in: LogoutRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Invalida el Refresh Token del usuario en la base de datos.
    Necesario para cortar la sesión de inmediato en caso de compromiso.
    El Access Token (JWT stateless) expirará por sí solo al alcanzar su TTL corto.
    """
    await AuthService.logout(db, obj_in.refresh_token)
    return {"detail": "Sesión cerrada correctamente"}


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Registro de un nuevo usuario (sin roles por defecto)"
)
async def register_user(
    obj_in: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Permite el autorregistro de un usuario nuevo.
    El usuario nace sin roles y requiere que un admin se los asigne después.
    """
    existing = await UserService.get_by_email(db, obj_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="El correo electrónico ya está registrado")
    
    await UserService.create(db, obj_in, creator_id=None)
    return {"detail": "Registro exitoso. Espera a que un administrador te asigne un rol."}

