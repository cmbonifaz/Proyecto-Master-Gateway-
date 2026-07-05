# -*- coding: utf-8 -*-
"""
internals.py — Endpoint privado para que otros microservicios validen tokens (Zero Trust).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import decode_token, verify_token_type
from app.services.user_service import UserService
from jose import JWTError
from pydantic import BaseModel

router = APIRouter()


class TokenValidationRequest(BaseModel):
    token: str


class TokenValidationResponse(BaseModel):
    valid: bool
    user_id: Optional[str] = None
    role_id: Optional[str] = None


from typing import Optional


@router.post(
    "/validate-token", 
    response_model=TokenValidationResponse,
    summary="Valida token JWT de forma síncrona para microservicios hijos"
)
async def validate_token(
    payload: TokenValidationRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint de uso interno (comunicación Master-Hijo).
    Permite a microservicios secundarios delegar la autenticación de una petición al Master.
    """
    try:
        # Validar tipo de token
        claims = verify_token_type(payload.token, "access_token")
        user_id = claims.get("sub")
        role_id = claims.get("role_id")
        
        # Validar que el usuario siga existiendo y esté ACTIVO
        user = await UserService.get_by_id(db, user_id)
        if not user:
            return TokenValidationResponse(valid=False)

        return TokenValidationResponse(
            valid=True,
            user_id=user_id,
            role_id=role_id
        )
    except JWTError:
        return TokenValidationResponse(valid=False)
