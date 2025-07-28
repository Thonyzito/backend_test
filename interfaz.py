import subprocess
subprocess.run(["pip", "install", "icrawler"])
subprocess.run(["apt-get", "install", "-y", "fonts-dejavu-core"])
#@title 2
from logging import disable
import os, shutil, cv2, textwrap, re
from PIL import Image, ImageDraw, ImageFont
from icrawler.builtin import BingImageCrawler
from IPython.display import display, clear_output, HTML
import ipywidgets as widgets
import threading
import time
import logging
from google.colab import files
import os


# Silencia todos los logs de icrawler y sus módulos internos
logging.getLogger().setLevel(logging.CRITICAL)
logging.getLogger('icrawler').setLevel(logging.CRITICAL)
logging.getLogger('icrawler.downloader').setLevel(logging.CRITICAL)
logging.getLogger('icrawler.image_downloader').setLevel(logging.CRITICAL)


# 📁 Configuración
carpeta_base = "imagenes_bing"
max_imgs = 5
font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# Variables globales
busquedas = []
guiones = []
imagenes = []
indice_imagen = 0
indice_busqueda = 0

subida_realizada = False


# Widgets
textbox_guiones = widgets.Textarea(placeholder="1. Título: Ejemplo de línea 1 con título y texto\nEjemplo de línea 2 solo con texto", layout=widgets.Layout(width='100%', height='100px'))
textbox_busquedas = widgets.Textarea(placeholder="Buscar imagen para la línea 1\nBuscar imagen para la línea 2", layout=widgets.Layout(width='100%', height='100px'))
boton_generar_carrusel = widgets.Button(description="🖼️Generar carrusel")

boton_busqueda_ant = widgets.Button(description="◀◀", disabled=True)
textbox_busqueda_individual = widgets.Text(placeholder="Cambiar imagen...", layout=widgets.Layout(width='300px'))
boton_busqueda_sig = widgets.Button(description="▶▶", disabled=True)

boton_izq = widgets.Button(description="◀", disabled=True)
textbox_guion_individual = widgets.Text(placeholder="Cambiar Texto...", layout=widgets.Layout(width='300px'))
boton_der = widgets.Button(description="▶", disabled=True)
boton_actualizar = widgets.Button(description="🔁 Actualizar", disabled=True)

seleccionadas = {}  # clave: índice de búsqueda, valor: índice de imagen
boton_seleccionar_imagen = widgets.Button(description="❌", disabled=True)

uploader_widget = widgets.FileUpload(accept='image/*', multiple=False, layout=widgets.Layout(width='0px', height='0px'))
boton_reemplazar = widgets.Button(description="📁 Reemplazar Imagen", disabled=True)
boton_descargar_imagenes = widgets.Button(description="⬇ Descargar", disabled=True)



imagen_widget = widgets.Output()
contador = widgets.Label()

# Funciones

# Inyectar CSS al notebook con tema neón
display(HTML("""
<style>
    /* Textoarea de etiquetas en verde neón */
    .etiquetas-color-verde textarea {
        color: #39ff14 !important;  /* verde neón */
        background-color: #000000 !important;
        font-weight: bold;
        border: 4px solid #39ff14 !important;
    }

    /* Textoarea en azul neón */
    .etiquetas-color-azul textarea {
        color: #00ffff !important;  /* cian neón */
        background-color: #000000 !important;
        font-weight: bold;
        border: 4px solid #00ffff !important;
    }

    .etiquetas-color-verde input {
        color: #39ff14 !important;
        background-color: #000000 !important;
        font-weight: bold;
        border: 4px solid #39ff14 !important;
    }

    .etiquetas-color-azul input {
        color: #00ffff !important;
        background-color: #000000 !important;
        font-weight: bold;
        border: 4px solid #00ffff !important;
    }

    /* Entradas tipo input y select con fondo oscuro y bordes neón */
    .modo-oscuro .widget-select,
    .modo-oscuro input,
    select {
        background-color: #000000 !important;
        color: #ffffff !important;
        border: 2px solid #ffffff !important; /* rosa neón */
        font-weight: bold;
    }

    /* Botón tipo A: cyan neón */
    .boton-cyan {
        background-color: #00ffff !important;
        color: #ffffff !important;
        border: 4px solid #00ffff !important;
        font-weight: bold;
    }

    /* Botón tipo B: verde neón */
    .boton-verde {
        background-color: #000000 !important;
        color: #39ff14 !important;
        border: 4px solid #39ff14 !important;
        font-weight: bold;
    }

    /* Botón tipo B.1: verde neón */
    .boton-verde-puro {
        background-color: #39ff14 !important;
        color: #ffffff !important;
        border: 4px solid #39ff14 !important;
        font-weight: bold;
    }

    /* Botón tipo C: rojo neón */
    .boton-rojo {
        background-color: #000000 !important;
        color: #ff3333 !important;
        border: 4px solid #ff3333 !important;
        font-weight: bold;
    }

    /* Botón tipo D: amarillo neón */
    .boton-amarillo {
        background-color: #000000 !important;
        color: #ffff00 !important;
        border: 4px solid #ffff00 !important;
        font-weight: bold;
    }

    /* Botón tipo E: blanco neón */
    .boton-blanco {
        background-color: #000000 !important;
        color: #ffffff !important;
        border: 4px solid #ffffff !important;
        font-weight: bold;
    }

    /* Fondo general del notebook */
    body, .notebook-container {
        background-color: #000000 !important;
        color: #ffffff !important;
    }
    .widget-label {
        color: #bbbbbb !important;  /* rosa neón */
        font-weight: bold;
        font-size: 14px;
        font-family: 'Arial', monospace;
    }

</style>
"""))

def recortar_centro_cuadrado(img):
    h, w = img.shape[:2]
    lado = min(h, w)
    x = (w - lado) // 2
    y = (h - lado) // 2
    return img[y:y+lado, x:x+lado]

def descargar_imagenes(query, carpeta):
    if os.path.exists(carpeta):
        shutil.rmtree(carpeta)
    os.makedirs(carpeta, exist_ok=True)
    crawler = BingImageCrawler(storage={'root_dir': carpeta})
    crawler.crawl(keyword=query, max_num=max_imgs)
    for i, filename in enumerate(sorted(os.listdir(carpeta))):
        origen = os.path.join(carpeta, filename)
        destino = os.path.join(carpeta, f"img{i}.jpg")
        os.rename(origen, destino)

def cargar_imagenes(busq_idx):
    global imagenes, indice_imagen
    carpeta = os.path.join(carpeta_base, f"busqueda_{busq_idx}")
    imagenes = sorted([os.path.join(carpeta, f) for f in os.listdir(carpeta) if f.endswith(".jpg")])
    indice_imagen = 0
    actualizar_imagen()

def actualizar_imagen():
    with imagen_widget:
        clear_output(wait=True)
        if imagenes:
            modificada = f"imagen_{indice_busqueda}_{indice_imagen}.jpg"
            if os.path.exists(modificada):
                display(widgets.Image(value=open(modificada, 'rb').read(), format='jpg', width=480))
            else:
                display(widgets.Image(value=open(imagenes[indice_imagen], 'rb').read(), format='jpg', width=480))

            contador.value = f"Búsqueda {indice_busqueda+1}/{len(busquedas)} · Imagen {indice_imagen+1}/{len(imagenes)}"
            if len(guiones) > indice_busqueda:
                textbox_guion_individual.value = guiones[indice_busqueda]

        else:
            contador.value = "❌ Sin imágenes"

    actualizar_boton_seleccion()



def generar_carrusel_desde_guiones(guiones=None, carpeta=None, busq_idx=None):
    #print("🖼 Generando carrusel de imágenes con sombra, fondo y ajuste automático...")

    if guiones is None:
        guiones = [line.strip() for line in textbox_guiones.value.strip().splitlines() if line.strip()]

    if carpeta and busq_idx is not None:
        guiones = [guiones[0]]  # Solo 1 guion para esa búsqueda

    for i, texto in enumerate(guiones):
        idx = busq_idx if busq_idx is not None else i
        carpeta_img = carpeta if carpeta else os.path.join(carpeta_base, f"busqueda_{idx}")

        for j in range(max_imgs):
            img_path = os.path.join(carpeta_img, f"img{j}.jpg")
            if not os.path.exists(img_path): continue

            img_cv = cv2.imread(img_path)
            img_cv = recortar_centro_cuadrado(img_cv)
            img_cv = cv2.resize(img_cv, (1080, 1080))
            img_pil = Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)).convert("RGBA")
            draw = ImageDraw.Draw(img_pil, "RGBA")

            match = re.match(r"^\d+\.\s*(.+?):\s*(.+)", texto.strip())
            if match:
                titulo = match.group(1).strip()
                contenido = match.group(2).strip()
            else:
                titulo = ""
                contenido = texto.strip()

            font_size = 72
            try:
                font = ImageFont.truetype(font_path, font_size)
            except:
                font = ImageFont.load_default()

            max_width = 1000
            max_height = 800

            if titulo:
                wrapped_title = textwrap.wrap(titulo, width=20)
                while (any(draw.textlength(line, font=font) > max_width for line in wrapped_title) or
                       (len(wrapped_title) * (font_size + 20)) > max_height // 3) and font_size > 30:
                    font_size -= 2
                    font = ImageFont.truetype(font_path, font_size)
                    wrapped_title = textwrap.wrap(titulo, width=25)
                title_font = font
                title_line_height = font_size + 20
            else:
                wrapped_title = []
                title_line_height = 0
                title_font = None

            if titulo:
                max_width = 950
                font_size = 54
                wrapped_content = textwrap.wrap(contenido, width=40)
            else:
                max_width = 1000
                font_size = 72
                wrapped_content = textwrap.wrap(contenido, width=20)

            font = ImageFont.truetype(font_path, font_size)
            while (any(draw.textlength(line, font=font) > max_width for line in wrapped_content) or
                   (len(wrapped_content) * (font_size + 20)) > (max_height - (title_line_height * len(wrapped_title)))) and font_size > 30:
                font_size -= 2
                font = ImageFont.truetype(font_path, font_size)
                wrapped_content = textwrap.wrap(contenido, width=25)
            content_font = font
            content_line_height = font_size + 20

            espacio_entre = 30
            total_height = (len(wrapped_title) * title_line_height) + espacio_entre + (len(wrapped_content) * content_line_height)
            y_inicio = (1080 - total_height) // 2

            overlay = Image.new("RGBA", img_pil.size, (0, 0, 0, 0))
            draw_overlay = ImageDraw.Draw(overlay)
            ancho_title = max([draw.textlength(l, font=title_font) for l in wrapped_title]) if wrapped_title else 0
            ancho_content = max([draw.textlength(l, font=content_font) for l in wrapped_content]) if wrapped_content else 0
            ancho_max = max(ancho_title, ancho_content)
            x_fondo = (1080 - ancho_max) // 2 - 40
            y_fondo = y_inicio - 30
            w_fondo = ancho_max + 80
            h_fondo = total_height + 60

            draw_overlay.rounded_rectangle([(x_fondo, y_fondo), (x_fondo + w_fondo, y_fondo + h_fondo)],
                                           radius=40, fill=(0, 0, 0, 80))
            img_pil = Image.alpha_composite(img_pil, overlay)
            draw = ImageDraw.Draw(img_pil)

            y = y_inicio
            for linea in wrapped_title:
                w = draw.textlength(linea, font=title_font)
                x = (1080 - w) // 2
                for dx in [-2, -1, 0, 1, 2]:
                    for dy in [-2, -1, 0, 1, 2]:
                        if dx != 0 or dy != 0:
                            draw.text((x+dx, y+dy), linea, font=title_font, fill=(0,0,0,255))
                draw.text((x, y), linea, font=title_font, fill=(255,255,255,255))
                y += title_line_height

            y += espacio_entre
            for linea in wrapped_content:
                w = draw.textlength(linea, font=content_font)
                x = (1080 - w) // 2
                for dx in [-2, -1, 0, 1, 2]:
                    for dy in [-2, -1, 0, 1, 2]:
                        if dx != 0 or dy != 0:
                            draw.text((x+dx, y+dy), linea, font=content_font, fill=(0,0,0,255))
                draw.text((x, y), linea, font=content_font, fill=(255,255,255,255))
                y += content_line_height

            output = f"imagen_{idx}_{j}.jpg"
            img_pil.convert("RGB").save(output)
            #print(f"✅ Imagen generada: {output}")

# Callbacks
def generar_carrusel(b):
    global busquedas, guiones
    busquedas = [line.strip() for line in textbox_busquedas.value.strip().splitlines() if line.strip()]
    guiones = [line.strip() for line in textbox_guiones.value.strip().splitlines() if line.strip()]
    for i, query in enumerate(busquedas):
        carpeta = os.path.join(carpeta_base, f"busqueda_{i}")
        descargar_imagenes(query, carpeta)
    cargar_imagenes(0)
    generar_carrusel_desde_guiones()
    textbox_busqueda_individual.value = busquedas[0] if busquedas else ""
    boton_actualizar.disabled = False
    boton_reemplazar.disabled = False
    boton_busqueda_ant.disabled = False
    boton_busqueda_sig.disabled = False
    boton_izq.disabled = False
    boton_der.disabled = False
    actualizar_imagen()


def busqueda_anterior(b):
    global indice_busqueda
    if busquedas:
        indice_busqueda = (indice_busqueda - 1) % len(busquedas)
        textbox_busqueda_individual.value = busquedas[indice_busqueda]
        cargar_imagenes(indice_busqueda)

def busqueda_siguiente(b):
    global indice_busqueda
    if busquedas:
        indice_busqueda = (indice_busqueda + 1) % len(busquedas)
        textbox_busqueda_individual.value = busquedas[indice_busqueda]
        cargar_imagenes(indice_busqueda)

def anterior_imagen(b):
    global indice_imagen
    if imagenes:
        indice_imagen = (indice_imagen - 1) % len(imagenes)
        actualizar_imagen()

def siguiente_imagen(b):
    global indice_imagen
    if imagenes:
        indice_imagen = (indice_imagen + 1) % len(imagenes)
        actualizar_imagen()

def actualizar_busqueda_y_guion(b):
    query = textbox_busqueda_individual.value.strip()
    nuevo_guion = textbox_guion_individual.value.strip()

    if not query:
        return

    valor_actual = busquedas[indice_busqueda] if indice_busqueda < len(busquedas) else ""
    guion_actual = guiones[indice_busqueda] if indice_busqueda < len(guiones) else ""

    carpeta = os.path.join(carpeta_base, f"busqueda_{indice_busqueda}")

    if query != valor_actual:
        if indice_busqueda < len(busquedas):
            busquedas[indice_busqueda] = query
        else:
            busquedas.append(query)

        if query != "Imagen Personalizada":
            descargar_imagenes(query, carpeta)

    if nuevo_guion != guion_actual:
        if indice_busqueda < len(guiones):
            guiones[indice_busqueda] = nuevo_guion
        else:
            guiones.append(nuevo_guion)

    # ✅ Generar carrusel si cambió algo
    if query != valor_actual or nuevo_guion != guion_actual:
        generar_carrusel_desde_guiones([guiones[indice_busqueda]], carpeta=carpeta, busq_idx=indice_busqueda)

    cargar_imagenes(indice_busqueda)
    textbox_busquedas.value = "\n".join(busquedas)
    textbox_guiones.value = "\n".join(guiones)



def actualizar_boton_seleccion():
    sel = seleccionadas.get(indice_busqueda)

    if sel is None:
        # Nada seleccionado aún en esta búsqueda
        boton_seleccionar_imagen.description = "👉"
        boton_seleccionar_imagen.disabled = False
    elif sel == indice_imagen:
        # Esta imagen está seleccionada
        boton_seleccionar_imagen.description = "✅"
        boton_seleccionar_imagen.disabled = False
    else:
        # Otra imagen está seleccionada
        boton_seleccionar_imagen.description = "❌"
        boton_seleccionar_imagen.disabled = True


def marcar_imagen_con_boton(b):
    sel = seleccionadas.get(indice_busqueda)

    if sel == indice_imagen:
        # Deseleccionar
        del seleccionadas[indice_busqueda]
    else:
        # Seleccionar esta imagen
        seleccionadas[indice_busqueda] = indice_imagen

    actualizar_boton_seleccion()
    actualizar_boton_descargar()

def actualizar_boton_descargar():
    boton_descargar_imagenes.disabled = len(seleccionadas) == 0

def reemplazar_imagen_manual(b):

    if not uploader_widget.value:
        print("❌ No se ha subido ninguna imagen.")
        return


    info = next(iter(uploader_widget.value.values()))
    contenido = info['content']
    nombre = info['metadata']['name']

    # Guardar archivo temporal
    ruta_origen = f"temp_{nombre}"
    with open(ruta_origen, "wb") as f:
        f.write(contenido)

    carpeta = os.path.join(carpeta_base, f"busqueda_{indice_busqueda}")
    if not os.path.exists(carpeta):
        os.makedirs(carpeta, exist_ok=True)

    img_cv = cv2.imread(ruta_origen)
    if img_cv is None:
        print("❌ Error: Imagen no válida.")
        return

    img_cv = recortar_centro_cuadrado(img_cv)
    img_cv = cv2.resize(img_cv, (1080, 1080))
    cv2.imwrite(ruta_origen, img_cv)

    for i in range(max_imgs):
        destino = os.path.join(carpeta, f"img{i}.jpg")
        shutil.copy2(ruta_origen, destino)

        nombre_generada = f"imagen_{indice_busqueda}_{i}.jpg"
        shutil.copy2(ruta_origen, nombre_generada)

    textbox_busqueda_individual.value = "Imagen Personalizada"
    actualizar_busqueda_y_guion(None)

    boton_reemplazar.disabled = False
    uploader_widget.layout = widgets.Layout(width='0px', height='0px')
    boton_reemplazar.layout = widgets.Layout(width='auto', height='auto')
    uploader_widget.value.clear()
    uploader_widget._counter = 0

    #print(f"✅ Imagen personalizada cambiada para búsqueda {indice_busqueda+1}")



def lanzar_file_selector(b):
    boton_reemplazar.disabled = True
    uploader_widget.layout = widgets.Layout(width='auto', height='auto')
    boton_reemplazar.layout = widgets.Layout(width='0px', height='0px')

    time.sleep(5)
    boton_reemplazar.disabled = False
    uploader_widget.layout = widgets.Layout(width='0px', height='0px')
    boton_reemplazar.layout = widgets.Layout(width='auto', height='auto')
    uploader_widget.value.clear()
    uploader_widget._counter = 0




def descargar_imagenes_terminadas(b):
    for busq_idx, img_idx in seleccionadas.items():
        ruta = f"imagen_{busq_idx}_{img_idx}.jpg"
        if os.path.exists(ruta):
            files.download(ruta)


# Conectar eventos
boton_generar_carrusel.on_click(generar_carrusel)
boton_busqueda_ant.on_click(busqueda_anterior)
boton_busqueda_sig.on_click(busqueda_siguiente)
boton_izq.on_click(anterior_imagen)
boton_der.on_click(siguiente_imagen)
boton_actualizar.on_click(actualizar_busqueda_y_guion)
boton_seleccionar_imagen.on_click(marcar_imagen_con_boton)
uploader_widget.observe(reemplazar_imagen_manual, names='value')
boton_reemplazar.on_click(lanzar_file_selector)
boton_descargar_imagenes.on_click(descargar_imagenes_terminadas)

textbox_guiones.add_class("etiquetas-color-verde")
textbox_busquedas.add_class("etiquetas-color-azul")
textbox_guion_individual.add_class("etiquetas-color-verde")
textbox_busqueda_individual.add_class("etiquetas-color-azul")
boton_generar_carrusel.add_class("boton-amarillo")
boton_busqueda_ant.add_class("boton-verde-puro")
boton_busqueda_sig.add_class("boton-verde-puro")
boton_izq.add_class("boton-cyan")
boton_der.add_class("boton-cyan")
boton_actualizar.add_class("boton-amarillo")
boton_reemplazar.add_class("boton-blanco")
boton_seleccionar_imagen.add_class("boton-blanco")
boton_descargar_imagenes.add_class("boton-blanco")

# Mostrar interfaz
display(textbox_guiones)
display(textbox_busquedas)
display(boton_generar_carrusel)
display(widgets.HBox([boton_busqueda_ant, textbox_guion_individual, boton_busqueda_sig]))
display(widgets.HBox([boton_izq, textbox_busqueda_individual, boton_der]))
display(widgets.HBox([boton_actualizar, boton_reemplazar, uploader_widget]))
display(widgets.HBox([boton_seleccionar_imagen, boton_descargar_imagenes, contador]))
display(imagen_widget)
