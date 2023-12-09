from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from requests.auth import HTTPBasicAuth
import os
from config import WP_USER, WP_PASSWORD

def esperar_y_obtener_elemento(driver, tipo, valor):
    espera = WebDriverWait(driver, 10)
    return espera.until(EC.presence_of_element_located((tipo, valor)))

def capturar_imagen_condicional(url_pagina, clase_elemento, nombre_archivo, id_elemento_magnitud):
    with webdriver.Chrome() as driver:
        driver.get(url_pagina)
        try:
            magnitud_element = esperar_y_obtener_elemento(driver, By.ID, id_elemento_magnitud)
            magnitud = float(magnitud_element.text)
            if magnitud >= 4.0:
                card_element = esperar_y_obtener_elemento(driver, By.CLASS_NAME, clase_elemento)
                path_completo = os.path.join("D:/2023/Scraper", nombre_archivo)
                card_element.screenshot(path_completo)
                return path_completo
            else:
                print(f"Magnitud no crítica: {magnitud}")
                return None
        except Exception as e:
            print(f"Error durante la captura: {e}")
            return None

def subir_imagen_wp(nombre_archivo, usuario, password, url_wp_api):
    try:
        with open(nombre_archivo, 'rb') as img:
            url = f'{url_wp_api}/media'
            headers = {'Content-Disposition': f'attachment; filename={nombre_archivo}'}
            respuesta = requests.post(url, headers=headers, files={'file': img}, auth=HTTPBasicAuth(usuario, password))
            if respuesta.status_code == 201:
                return respuesta.json()['source_url']
            else:
                print(f"Error al subir la imagen: {respuesta.status_code} {respuesta.text}")
                return None
    except IOError as e:
        print(f"Error al abrir el archivo: {e}")
        return None

def crear_post_wp(titulo, url_imagen, usuario, password, url_wp_api):
    url = f'{url_wp_api}/posts'
    datos = {'title': titulo, 'content': f'<img src="{url_imagen}" alt="Descripción" />', 'status': 'publish'}
    respuesta = requests.post(url, json=datos, auth=HTTPBasicAuth(usuario, password))
    if respuesta.status_code == 201:
        return respuesta.json().get('link')
    else:
        print(f"Error al crear el post: {respuesta.status_code} {respuesta.text}")
        return None

usuario_wp = WP_USER
password_wp = WP_PASSWORD
url_wp_api = 'https://imagia.academy/wp-json/wp/v2'

captura_realizada = capturar_imagen_condicional('https://ultimosismo.igp.gob.pe/ultimo-sismo', 'col-lg-9', 'captura_condicional.png', 'data-magnitud')

if captura_realizada:
    print(f"Captura realizada con éxito, imagen guardada en: {captura_realizada}")
    url_imagen = subir_imagen_wp(captura_realizada, usuario_wp, password_wp, url_wp_api)
    if url_imagen:
        url_post = crear_post_wp('Nuevo Post con Imagen -sábado', url_imagen, usuario_wp, password_wp, url_wp_api)
        if url_post:
            print("Post creado:", url_post)
        else:
            print("No se pudo crear el post")
else:
    print("No se pudo obtener la URL de la imagen")
