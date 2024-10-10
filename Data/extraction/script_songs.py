import requests
import sys
import os
import xml.etree.ElementTree as ET
from urllib.parse import quote 

sys.stdout.reconfigure(encoding='utf-8')

if not os.path.exists('letras'):
    os.makedirs('letras')

def obtener_canciones(archivo):
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            canciones = [linea.strip().split(',') for linea in f if linea.strip()]
        return canciones
    except FileNotFoundError:
        print(f"Error: El archivo {archivo} no fue encontrado.")
        return []

# Obtener letra de la canción con timeout
def obtener_letra_cancion(titulo_cancion, artista):
    # Usar quote para reemplazar espacios y caracteres especiales
    titulo_cancion = quote(titulo_cancion)
    artista = quote(artista)
    
    url = f"https://api.lyrics.ovh/v1/{artista}/{titulo_cancion}"
    try:
        respuesta = requests.get(url, timeout=5)  # Timeout de 5 segundos
        if respuesta.status_code == 200:
            letra = respuesta.json().get('lyrics', 'Letra no disponible')
            return letra
        else:
            return None
    except requests.RequestException as e:
        return None

# Guardar la letra en un archivo
def guardar_letra_cancion(titulo, artista):
    letra = obtener_letra_cancion(titulo, artista)
    # print (letra)
    if letra:
        if letra != 'Letra no disponible':  
            with open(f'letras/{titulo} - {artista}.txt', 'w', encoding='utf-8') as f:
                f.write(letra)
        else:
            print ("Letra no disponible de la canción" + titulo)
            guardar_no_encontradas(titulo, artista)
    else :
        print ("No fue posible encontrar la letra de la canción: " + titulo)
        guardar_no_encontradas(titulo, artista)


# Guardar la canción en el archivo No Encontradas.txt
def guardar_no_encontradas(titulo, artista):
    with open('No Encontradas.txt', 'a', encoding='utf-8') as f:
        f.write(f"{titulo} - {artista}\n")

# Procesar las canciones del archivo csv y guardar las letras
def procesar_canciones(archivo):
    canciones = obtener_canciones(archivo)
    print (canciones)
    if not canciones:
        return
    else :
        for cancion in canciones:
            titulo, artista = cancion
            guardar_letra_cancion(titulo, artista)

# Función para obtener la letra de una canción usando ChartLyrics API
def obtener_letra_chartlyrics(artista, titulo_cancion):
    # URL de la API de ChartLyrics
    url = f"http://api.chartlyrics.com/apiv1.asmx/SearchLyricDirect?artist={artista}&song={titulo_cancion}"
    
    # Realizar la solicitud
    respuesta = requests.get(url)

    if respuesta.status_code == 200:
        # Parsear el XML de la respuesta
        root = ET.fromstring(respuesta.content)

        # Obtener el elemento que contiene la letra
        letra = root.find(".//{http://api.chartlyrics.com/}Lyric").text

        if letra:
            return letra
        else:
            return "Letra no disponible o no encontrada en la base de datos."
    else:
        return "Error al conectarse a la API."

# Función para procesar las canciones que no se encontraron anteriormente (basado en el formato "Titulo - Artista")
def procesar_canciones_no_encontradas(archivo):
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            canciones = f.readlines()
    except FileNotFoundError:
        print(f"Error: El archivo {archivo} no fue encontrado.")
        return
    
    for cancion in canciones:
        # Separar el título y el artista por el guion
        try:
            titulo, artista = cancion.split(' - ')
            titulo = titulo.strip()
            artista = artista.strip()
            
            # Obtener la letra de la canción
            letra = obtener_letra_chartlyrics(artista, titulo)
            
            if letra and letra != "Letra no disponible o no encontrada en la base de datos.":
                # Guardar la letra en un archivo
                with open(f'letras/{titulo} - {artista}.txt', 'w', encoding='utf-8') as f:
                    f.write(letra)
            else:
                print(f"No se pudo obtener la letra de la canción {titulo} - {artista}")
        except ValueError:
            print(f"Formato incorrecto en la línea: {cancion.strip()}")


# Llamar a la función procesar_canciones con el archivo de canciones
# procesar_canciones('canciones80.csv')
procesar_canciones_no_encontradas('No Encontradas.txt')