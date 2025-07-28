# us_of.py (esto es lo que debe venir en codigo_us_of)

import requests
import re

def o_d_o(token_github, usuario_repo, nombre_repo):
    url = f"https://api.github.com/repos/{usuario_repo}/{nombre_repo}/contents/backend.py"
    headers = {
        "Authorization": f"token {token_github}",
        "Accept": "application/vnd.github.v3.raw"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception("No se pudo acceder al archivo backend.py")

    texto = response.text
    match = re.search(r"US_OF\s*=\s*{.*?}", texto, re.DOTALL)
    if not match:
        raise Exception("No se encontró el diccionario US_OF")

    exec(match.group(), globals())
    globals()["US_OF"] = US_OF
