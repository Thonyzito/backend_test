import requests
import re

# Información embebida
TOKEN_GITHUB = "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"
USUARIO_REPO = "Thonyzito"
NOMBRE_REPO = "backend_test"

# Obtener backend.py desde GitHub
url = f"https://api.github.com/repos/{USUARIO_REPO}/{NOMBRE_REPO}/contents/backend.py"
headers = {
    "Authorization": f"token {TOKEN_GITHUB}",
    "Accept": "application/vnd.github.v3.raw"
}
response = requests.get(url, headers=headers)
if response.status_code != 200:
    raise Exception("No se pudo acceder al archivo backend.py")

# Extraer diccionario
texto = response.text
match = re.search(r"USUARIOS_OFUSCADOS\s*=\s*{.*?}", texto, re.DOTALL)
if not match:
    raise Exception("No se encontró el diccionario USUARIOS_OFUSCADOS")

# Ejecutar definición del diccionario
exec(match.group(), globals())
