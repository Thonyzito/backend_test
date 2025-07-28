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
    3: (5, 4),
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
    i = 0
    reales = []
    alterna = True
    while i < len(texto):
        n = paso1 if alterna else paso2
        i += n  # saltar basura
        if i >= len(texto): break
        reales.append(texto[i])  # guardar caracter real
        i += 1  # saltar el real
        alterna = not alterna
    return ''.join(reales)[::-1]  # invertir al final


# Usuarios ofuscados
USUARIOS_OFUSCADOS = {
    #thony - 12345 - modo 1
    "7fkuhnynF8i9DkNIDWmzydFNwaQE4aVu":"3xAqhnbtalrXNSfjP5azNmljolwrNt0Oong14wbNh1voiJJszFiti9cGN81HVze76y4KF1VJOocWrgE5D0mbpX0",
    "OWnkaYmvleNLVaGQODOWMHJuxoaT4OrL": "dlA5GdKx49Jr3expG2us81XzdG",
}

class Credenciales(BaseModel):
    usuario: str
    clave: str


@app.post("/verificar")
def verificar_acceso(datos: Credenciales):
    # Combinaciones permitidas (usuario_modo, clave_modo)
    combos = [
        (1, 3),
        (2, 2),
        (3, 1)
    ]
    usuarios_posibles = []
    claves_posibles = []
    for user_obs, pass_obs in USUARIOS_OFUSCADOS.items():
        for usuario_modo, clave_modo in combos:
            usuario_real = desofuscar(user_obs, usuario_modo)
            clave_real = desofuscar(pass_obs, clave_modo)
            usuarios_posibles.append((usuario_real, usuario_modo))
            claves_posibles.append((clave_real, clave_modo))
            if datos.usuario == usuario_real and datos.clave == clave_real:
                return {
                    "acceso": "ok",
                    "usuario_elegido": usuario_real,
                    "clave_elegida": clave_real,
                    "modo_usuario": usuario_modo,
                    "modo_clave": clave_modo
                }
    return {
        "acceso": "denegado",
        "debug": {
            "usuarios": usuarios_posibles,
            "claves": claves_posibles,
            "modo_usuario": None,
            "modo_clave": None
        }
    }



@app.get("/codigo_us_of")
def enviar_codigo():
    with open("us_of.py", "r", encoding="utf-8") as f:
        codigo_us_of = f.read()
    return {"codigo": codigo_us_of}
    
@app.get("/codigo")
def enviar_codigo():
    with open("interfaz.py", "r", encoding="utf-8") as f:
        codigo = f.read()
    return {"codigo": codigo}

@app.get("/codigo2")
def enviar_codigo2():
    with open("interfaz_ADMIN.py", "r", encoding="utf-8") as f:
        codigo2 = f.read()
    return {"codigo": codigo2}
