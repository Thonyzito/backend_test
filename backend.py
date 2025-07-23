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

# Función de ofuscación
def ofuscar(texto: str, modo: int) -> str:
    texto = texto[::-1]  # Invertir
    print(texto)
    paso1, paso2 = PATRONES[modo]
    salida = ""
    alterna = True
    i = len(texto)
    for c in texto:
        n1 = paso1 if alterna else paso2
        n2 = paso2 if alterna else paso1
        basura_inicio = ''.join(random.choices(string.ascii_letters + string.digits, k=n1))
        basura_final = ''.join(random.choices(string.ascii_letters + string.digits, k=n2))
        salida += basura_inicio + c
        alterna = not alterna
        i -= 1
        if i == 0:
            salida += basura_final

    return salida
def desofuscar(texto: str, modo: int) -> str:
    paso1, paso2 = PATRONES[modo]
    salida = ""
    i = 0
    alterna = True
    while i < len(texto):
        n = paso1 if alterna else paso2
        i += n  # saltar basura inicial
        if i >= len(texto):
            break
        salida += texto[i]  # capturar carácter real
        i += 1  # avanzar 1 posición
        n = paso2 if alterna else paso1
        i += n  # saltar basura final
        alterna = not alterna
    return salida[::-1]  # invertir para recuperar original



# Usuarios ofuscados
USUARIOS_OFUSCADOS = {
    #thony - 12345
    "PlGynvqRnG0vofB40hYq0tKYMI": "woByG5ONRo4voL3N3cfGO2rBXNj1mrDb",  # test
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
