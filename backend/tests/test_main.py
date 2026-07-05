import pytest
from fastapi.testclient import TestClient
from app.main import app

# Instanciamos el cliente de pruebas de FastAPI
client = TestClient(app)

def test_listar_eventos_exitoso():
    """
    Prueba el flujo normal de listar eventos. 
    Se espera un HTTP 200 OK y una lista con eventos.
    """
    response = client.get("/eventos")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0


def test_crear_reserva_exitosa():
    """
    Prueba el flujo de negocio correcto creando una reserva válida.
    Se espera un HTTP 201 Created.
    """
    payload = {
        "evento_id": 1,
        "email_usuario": "cliente.feliz@liveseat.com",
        "cantidad_asientos": 2,
        "metodo_pago": "tarjeta"
    }
    response = client.post("/reservas", json=payload)
    assert response.status_code == 201
    assert response.json()["mensaje"] == "Reserva confirmada exitosamente"


def test_seguridad_pydantic_rechaza_inyeccion_metodo_pago():
    """
    Prueba de Seguridad (Negative Testing): 
    Valida que Pydantic rechaza strings con caracteres maliciosos o formatos 
    inesperados simulando un intento de inyección o payload malformado.
    Se espera un HTTP 422 Unprocessable Entity.
    """
    payload = {
        "evento_id": 1,
        "email_usuario": "hacker@example.com",
        "cantidad_asientos": 1,
        # Intento de Inyección (SQLi / XSS payload)
        "metodo_pago": "tarjeta'; DROP TABLE usuarios;--"
    }
    response = client.post("/reservas", json=payload)
    
    assert response.status_code == 422
    assert "String should match pattern" in response.text


def test_seguridad_pydantic_rechaza_abuso_de_limites():
    """
    Prueba de Seguridad (Business Logic Flaw Defense):
    Valida que no se puedan reservar más asientos de los permitidos por transacción (ej. limitando a 10),
    previniendo ataques de agotamiento de inventario (Inventory Exhaustion).
    Se espera un HTTP 422 Unprocessable Entity.
    """
    payload = {
        "evento_id": 1,
        "email_usuario": "abuso@example.com",
        "cantidad_asientos": 500, # El límite configurado en Pydantic es de 10
        "metodo_pago": "paypal"
    }
    response = client.post("/reservas", json=payload)
    
    assert response.status_code == 422
    assert "Input should be less than or equal to 10" in response.text

def test_seguridad_bloquea_xss():
    """
    Prueba de Seguridad (Sanitización y Validación):
    Valida que los esquemas de validación o sanitización bloqueen inyecciones XSS.
    En este caso, la regex restrictiva de Pydantic bloquea los caracteres `<` y `>`
    antes siquiera de llegar a la lógica de negocio o a bleach.
    Se espera un HTTP 422 Unprocessable Entity.
    """
    payload = {
        "nombre": "Concierto <script>alert('XSS')</script> VIP",
        "asientos_disponibles": 100
    }
    response = client.post("/eventos/", json=payload)
    
    assert response.status_code == 422
    assert "String should match pattern" in response.text
