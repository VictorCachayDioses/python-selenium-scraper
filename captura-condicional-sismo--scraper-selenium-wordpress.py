from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
from requests.auth import HTTPBasicAuth
import base64
import time

def capturar_imagen_condicional(url_pagina, clase_elemento, nombre_archivo, id_elemento_magnitud):
    driver = webdriver.Chrome()
    driver.get(url_pagina)

    try:
        time.sleep(5)  # Espera a que el elemento esté cargado
        # Encuentra el elemento que tiene la magnitud del sismo
        magnitud_element = driver.find_element(By.ID, id_elemento_magnitud)
        magnitud = float(magnitud_element.text)

        # Verifica si la magnitud es 4.0 o superior
        if magnitud >= 4.0:
            # Encuentra el primer elemento con la clase 'card' y captura la pantalla
            card_element = driver.find_element(By.CLASS_NAME, clase_elemento)
            # Define el path completo donde se guardará la captura de pantalla
            path_completo = "D:/2023/Scraper/" + nombre_archivo
            # Guarda la captura de pantalla del elemento
            card_element.screenshot(path_completo)
            return path_completo  # Retorna el path completo de la imagen guardada
        else:
            print(f"Magnitud no crítica: {magnitud}")
            return None
    finally:
        # Cierra el navegador
        driver.quit()

# Uso de la función
url_pagina = 'https://ultimosismo.igp.gob.pe/ultimo-sismo'
id_elemento_magnitud = 'data-magnitud'  # ID del elemento que contiene la magnitud
clase_elemento = 'col-lg-9'  # Clase del elemento que quieres capturar
nombre_archivo = 'captura_condicional.png'  # Nombre del archivo donde se guardará la captura

# Función para subir la imagen a WordPress
def subir_imagen_wp(nombre_archivo, usuario, password, url_wp_api):
    try:
        url = url_wp_api + '/media'
        img = open(nombre_archivo, 'rb')
        archivo = {'file': img}
        headers = {
            'Content-Disposition': 'attachment; filename=' + nombre_archivo,
            'Authorization': 'Basic ' + base64.b64encode(f"{usuario}:{password}".encode()).decode()
        }
        respuesta = requests.post(url, headers=headers, files=archivo, auth=HTTPBasicAuth(usuario, password))
        img.close()  # Cierra el archivo después de la petición
        if respuesta.status_code == 201:
            data = respuesta.json()
             # Como no hay tamaños adicionales, usa la URL original de la imagen subida
            url_imagen = data['source_url']
            print("Imagen subida con éxito. URL:", url_imagen)
            return url_imagen
        else:
            print("Error al subir la imagen:", respuesta.status_code, respuesta.text)
            return None
    except IOError as e:
        print("Error al abrir el archivo:", e)
        return None

# Función para crear un nuevo post en WordPress
def crear_post_wp(titulo, url_imagen, usuario, password, url_wp_api):
    url = url_wp_api + '/posts'

    # Cuerpo del post
    datos = {
        'title': titulo,
        'content': f'<img src="{url_imagen}" alt="Descripción" />',
        'status': 'publish'
    }

    headers = {
        'Authorization': 'Basic ' + base64.b64encode(f"{usuario}:{password}".encode()).decode()
    }

    # Realiza la petición para crear el post
    respuesta = requests.post(url, headers=headers, json=datos, auth=HTTPBasicAuth(usuario, password))
    if respuesta.status_code == 201:
        return respuesta.json().get('link')  # Retorna solo la URL del post
    else:
        print("Error al crear el post:", respuesta.status_code, respuesta.text)
        return None

# Configuración
# Esta línea llama las credenciales a WP que se encuentran en config.py y que están en este formato: # config.py
#WP_USER = 'usuario'
#WP_PASSWORD = 'clave'
from config import WP_USER, WP_PASSWORD

url_pagina = 'https://ultimosismo.igp.gob.pe/ultimo-sismo'
id_elemento_magnitud = 'data-magnitud'  # Asegúrate de que este es el ID correcto
nombre_archivo = 'captura-condicional.png'
usuario_wp = WP_USER
password_wp = WP_PASSWORD
url_wp_api = 'https://imagia.academy/wp-json/wp/v2'

# Proceso
# Llama a la función con los parámetros necesarios
captura_realizada = capturar_imagen_condicional(url_pagina, clase_elemento, nombre_archivo, id_elemento_magnitud)

if captura_realizada:
    print(f"Captura realizada con éxito, imagen guardada en: {captura_realizada}")

    # Continúa con el flujo de trabajo, subiendo la imagen a WordPress y creando un post
    url_imagen = subir_imagen_wp(captura_realizada, usuario_wp, password_wp, url_wp_api)
    if url_imagen:
        url_post = crear_post_wp('Nuevo Post con Imagen -Jueves', url_imagen, usuario_wp, password_wp, url_wp_api)
        if url_post:
            print("Post creado:", url_post)
        else:
            print("No se pudo crear el post")
else:
    print("No se pudo obtener la URL de la imagen")
