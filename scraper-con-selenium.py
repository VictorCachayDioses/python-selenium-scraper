from selenium import webdriver
from selenium.webdriver.common.by import By

# Configura el navegador
driver = webdriver.Chrome()  # Requiere el controlador de Chrome
driver.get('https://victor.tendencia.news')

# Captura una captura de pantalla de la parte específica del sitio web
element = driver.find_element('id', 'header')  # Usar 'id' como método de búsqueda

element.screenshot('captura.png')

# Cierra el navegador
driver.quit()
