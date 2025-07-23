# backend.py
from fastapi import FastAPI, Request
from pydantic import BaseModel

app = FastAPI()

# Datos de acceso válidos
USUARIOS = {
    "usuario1": "clave123",
    "test": "acceso2025"
}

class Credenciales(BaseModel):
    usuario: str
    clave: str

@app.post("/verificar")
def verificar_acceso(datos: Credenciales):
    if USUARIOS.get(datos.usuario) == datos.clave:
        return {"acceso": "ok"}
    else:
        return {"acceso": "denegado"}
