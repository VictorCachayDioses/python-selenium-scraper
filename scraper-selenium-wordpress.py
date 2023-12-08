from selenium import webdriver
import requests
from requests.auth import HTTPBasicAuth
import base64
import time

# Configuración de Selenium para capturar la imagen
def capturar_imagen(url_pagina, id_elemento, nombre_archivo):
    # Configura el navegador (Asegúrate de tener Chromedriver instalado y en tu PATH)
    driver = webdriver.Chrome()
    driver.get(url_pagina)

    # Espera a que el elemento esté cargado (ajusta el tiempo según sea necesario)
    time.sleep(5)  # Espera 5 segundos

    # Encuentra el elemento y captura la pantalla
    from selenium.webdriver.common.by import By
    element = driver.find_element(By.ID, id_elemento)
    element.screenshot(nombre_archivo)

    # Cierra el navegador
    driver.quit()

# Función para subir la imagen a WordPress
def subir_imagen_wp(nombre_archivo, usuario, password, url_wp_api):
    try:
        url = url_wp_api + '/media'

        # Abre la imagen
        with open(nombre_archivo, 'rb') as img:
            archivo = {'file': img}

            # Cabeceras necesarias para la API de WordPress
            headers = {
                'Content-Disposition': 'attachment; filename=' + nombre_archivo,
                'Authorization': 'Basic ' + base64.b64encode(f"{usuario}:{password}".encode()).decode()
            }

            # Realiza la petición para subir la imagen
            respuesta = requests.post(url, headers=headers, files=archivo, auth=HTTPBasicAuth(usuario, password))
            return respuesta.json()

    except IOError as e:
        print("Error al abrir el archivo:", e)
# ... código existente ...
    respuesta = requests.post(url, headers=headers, files=archivo, auth=HTTPBasicAuth(usuario, password))
 # Agrega manejo de errores y obtención de la URL de la imagen
    if respuesta.status_code == 201:
        data = respuesta.json()
        return data['guid']['rendered']  # La URL de la imagen se encuentra en 'guid'
    else:
        print("Error al subir la imagen:", respuesta.status_code, respuesta.text)
        return None


# Función para crear un nuevo post en WordPress
def crear_post_wp(titulo, url_imagen, usuario, password, url_wp_api):
    url = url_wp_api + '/posts'

    # Cuerpo del post
    datos = {
        'title': titulo,
        'content': f'<img src="{url_imagen}"/>',
        'status': 'publish'
    }

    headers = {
        'Authorization': 'Basic ' + base64.b64encode(f"{usuario}:{password}".encode()).decode()
    }

    # Realiza la petición para crear el post
    respuesta = requests.post(url, headers=headers, json=datos, auth=HTTPBasicAuth(usuario, password))
    return respuesta.json()

# Configuración
url_pagina = 'https://victor.tendencia.news'
id_elemento = 'header'
nombre_archivo = 'captura.png'
usuario_wp = ''
password_wp = ''
url_wp_api = 'https://imagia.academy/wp-json/wp/v2'

# Proceso
capturar_imagen(url_pagina, id_elemento, nombre_archivo)
# Sube la imagen una vez y obtiene la URL
url_imagen = subir_imagen_wp(nombre_archivo, usuario_wp, password_wp, url_wp_api)
if url_imagen:
    # Crear el post con la URL de la imagen
    respuesta_post = crear_post_wp('Nuevo Post con Imagen', url_imagen, usuario_wp, password_wp, url_wp_api)
    print("Post creado:", respuesta_post['link'])
else:
    print("No se pudo obtener la URL de la imagen")
