# backend.py
from fastapi import FastAPI, Request
from pydantic import BaseModel
import random
import string

app = FastAPI()

# Ofuscadores posibles
PATRONES = {
    1: (3, 4),
    2: (7, 2),
    3: (4, 5),
}

def ofuscar(texto: str, modo: int) -> str:
    texto = texto[::-1]  # Invertir
    paso1, paso2 = PATRONES[modo]
    salida = ""
    i = 0
    alterna = True
    while i < len(texto):
        n = paso1 if alterna else paso2
        salida += ''.join(random.choices(string.ascii_letters + string.digits, k=n))
        salida += texto[i]
        i += 1
        alterna = not alterna
    return salida

def desofuscar(ofuscado: str) -> list:
    posibles = []
    for paso1, paso2 in PATRONES.values():
        texto = ""
        i = 0
        alterna = True
        while i < len(ofuscado):
            n = paso1 if alterna else paso2
            i += n
            if i >= len(ofuscado):
                break
            texto += ofuscado[i]
            i += 1
            alterna = not alterna
        posibles.append(texto[::-1])
    return posibles

# Usuarios ofuscados
USUARIOS_OFUSCADOS = {
    "bbbr1xxxoobbbiiaaarruuaass": "yyyb9lllaaavvveee111",
    "qqq2xxxtttssseeeaaattt": "zzzcccaaccceesssoo222"
}

class Credenciales(BaseModel):
    usuario: str
    clave: str

@app.post("/verificar")
def verificar_acceso(datos: Credenciales):
    for user_obs, pass_obs in USUARIOS_OFUSCADOS.items():
        posibles_usuarios = desofuscar(user_obs)
        if datos.usuario in posibles_usuarios:
            posibles_claves = desofuscar(pass_obs)
            if datos.clave in posibles_claves:
                return {"acceso": "ok"}
    return {"acceso": "denegado"}

@app.get("/codigo")
def enviar_codigo():
    return {"codigo": "print(\"¡Bienvenido, tienes acceso!\")"}
