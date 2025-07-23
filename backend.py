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
    alterna = True
    for c in texto:
        n1 = paso1 if alterna else paso2
        n2 = paso2 if alterna else paso1
        basura_inicio = ''.join(random.choices(string.ascii_letters + string.digits, k=n1))
        basura_final = ''.join(random.choices(string.ascii_letters + string.digits, k=n2))
        salida += basura_inicio + c + basura_final
        alterna = not alterna
    return salida

def desofuscar(ofuscado: str) -> list:
    posibles = []
    for paso1, paso2 in PATRONES.values():
        texto = ""
        i = 0
        alterna = True
        while i < len(ofuscado):
            n1 = paso1 if alterna else paso2
            n2 = paso2 if alterna else paso1
            i += n1
            if i >= len(ofuscado):
                break
            texto += ofuscado[i]
            i += 1 + n2
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
