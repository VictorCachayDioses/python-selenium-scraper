from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
from requests.auth import HTTPBasicAuth
import base64
import time

# Configuración de Selenium para capturar la imagen
def capturar_imagen(url_pagina, id_elemento, nombre_archivo):
    driver = webdriver.Chrome()
    driver.get(url_pagina)
    time.sleep(5)  # Espera a que el elemento esté cargado
    element = driver.find_element(By.ID, id_elemento)
    element.screenshot(nombre_archivo)
    driver.quit()

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
            url_imagen = data['media_details']['sizes']['full']['source_url']
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

url_pagina = 'https://victor.tendencia.news'
id_elemento = 'header'
nombre_archivo = 'captura.png'
usuario_wp = WP_USER
password_wp = WP_PASSWORD
url_wp_api = 'https://imagia.academy/wp-json/wp/v2'

# Proceso
capturar_imagen(url_pagina, id_elemento, nombre_archivo)
url_imagen = subir_imagen_wp(nombre_archivo, usuario_wp, password_wp, url_wp_api)
if url_imagen:
    # Crear el post con la URL de la imagen
    url_post = crear_post_wp('Nuevo Post con Imagen -Jueves', url_imagen, usuario_wp, password_wp, url_wp_api)
    if url_post:
        print("Post creado:", url_post)  # Imprime solo la URL del post
    else:
        print("No se pudo crear el post")
else:
    print("No se pudo obtener la URL de la imagen")
