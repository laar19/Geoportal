# Script para procesar imagenes Nivel 2A VRSS-2 para generar dataset de geoaplicacion
# Incorpora lectura de las imagenes en carpeta, generacion de archivo .csv y carga
# a la base de datos, ademas de extraer los thumbnails

# Desarrollado por Ronald Delgado y Eduardo Guillen - ABAE 2023.

# Las imagenes a catalogar deben estar copiadas en una carpeta llamada /imagenes
# Los thumbnails de las mismas se generaran en una carpeta llamada /thumbnails

import lxml.etree as ET
import os
import zipfile
import re
import pandas as pd
import geopandas as gpd
import shutil
from shapely.geometry import Polygon
#from sqlalchemy import *
from sqlalchemy import create_engine, Table, MetaData
from configparser import ConfigParser

# Leemos el shapefile de los estados de Venezuela
# Este shapefile se usa para comparar ubicacion del centro de la imagen con
# estado y asignar ubicacion por Estado   
estados_venezuela = gpd.read_file("vzla_exterior.zip")

# De cada archivo, descomprime en la carpeta xml solo los xml presentes que terminan en .xml
def unpackXML(filename, carpeta):
    '''
    Funcion para descromprimir el archivo .tar.gz original que contiene las 
    imagenes / bandas.
    Entradas:
        filename = nombre del archivo comprimido
        carpeta = nombre de la carpeta donde descomprimir las imagenes / bandas
    Salidas:
        archivo de metadatos .xml
    '''
    # Abre el zipfile en modo lectura
    with zipfile.ZipFile(filename, 'r') as zip: 
        # Obtenemos una lista de los nombres de archivo
        file_names = zip.namelist()    
        # Iteramos a lo largo de los archivos
        for name in file_names:
            # Extraemos solo el archivo de metadatos principal
            if re.search('\d.xml$', name):
                print("Extrayendo archivo {}".format(name))
                zip.extract(name, './'+carpeta)
                print("Extraccion de archivo finalizada!\n")
                return name
        
# De cada archivo, descomprime solo el thumbnail que acompaña cada imagen
def unpackThumb(filename, carpeta):
    '''
    Funcion para descromprimir el archivo .tar.gz original que contiene las 
    imagenes / bandas.
    Entradas:
        filename = nombre del archivo comprimido
        carpeta = nombre de la carpeta donde descomprimir las imagenes / bandas
    Salidas:
        archivo de metadatos .xml
    '''
    # Abre el zipfile en modo lectura
    with zipfile.ZipFile(filename, 'r') as zip: 
        # Obtenemos una lista de los nombres de archivo
        file_names = zip.namelist()    
        # Iteramos a lo largo de los archivos
        for name in file_names:
            # Extraemos solo el archivo de metadatos principal
            if re.search('_THUMB.jpg', name):
                print("Extrayendo archivo {}".format(name))
                zip.extract(name, './'+carpeta)
                print("Extraccion de archivo finalizada!\n")
                return name
            
# Funcion para leer archivo de credenciales de la base de datos a partir de 
# archivo .ini
def config(filename='database.ini', section='postgresql'):
    '''
    Funcion para parsear datos de configuracion de la base de datos
    Entradas:
        filename = archivo de configuracion database.ini
        section = seccion de donde va a leer datos de postgresql
        Es posible agregar otras secciones para cargar otros datos de manera
        que no sean hardcoded. Por ejemplo, nombres de tablas o rutas
    Salidas:
        devuelve diccionario con parametros de configuracion de DB
    '''
    # Crea un parser
    parser = ConfigParser()
    # Lee el archivo de configuracion
    parser.read(filename)

    # Toma la seccion, default a postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception(f'Seccion {section} no encontrada en archivo {filename}')

    return db
                                 
def connection(db_address, db_port, db_user, db_password, db_name):
    '''
    Funcion para conectarse a la base de datos en donde se almacenan las tablas
    de las imagenes procesadas
    Entradas:
        db_address = direccion IP de la DB
        db_port = puerto de la DB
        db_user = usuario de la DB
        db_password = password de la DB
        db_name = nombre de la DB
    '''
    postgres_str = (f'postgresql://{db_user}:{db_password}@{db_address}:{db_port}/{db_name}')
    conn_1 = create_engine(postgres_str)
    if conn_1:
        print("###Conexion Engine a DB "+ db_name +" exitosa###")
        return conn_1
    else:
        return print("###Conexion Engine a DB "+ db_name +" FALLIDA###")

# Main del script          
if __name__ == "__main__":
    
    # En primer lugar, verifica si existe la carpeta "xml" y la crea si no existe
    if not os.path.exists("xml"):
        # Crea el directorio
        os.mkdir("xml")
        
    if not os.path.exists("thumbnails"):
        # Crea el directorio
        os.mkdir("thumbnails")
        
    # Lista los archivos comprimidos de imagenes presentes en la carpeta imagenes
    carpeta_imagenes = "imagenes"
    
    lista_de_archivos = []
    for (dirpath, dirnames, filenames) in os.walk(carpeta_imagenes):
        lista_de_archivos += [os.path.join(dirpath, file) for file in filenames]
        lista_de_archivos = sorted(lista_de_archivos)    
        
    # Para cada uno de los archivos de imagenes, se extraen los xml
    lista_nombres_comprimidos = []
    lista_de_xml = []
    lista_de_thumb = []
    for archivo in lista_de_archivos:
        lista_nombres_comprimidos.append(archivo.split("\\")[1])
        lista_de_xml.append("xml/"+unpackXML(archivo, "xml"))
        lista_de_thumb.append("thumbnails/"+unpackThumb(archivo, "thumbnails"))
        
    # Ahora, listamos los archivos presentes en la carpeta xml
    #lista_de_xml = []
    #for (dirpath, dirnames, filenames) in os.walk("xml"):
    #    lista_de_xml += [os.path.join(dirpath, file) for file in filenames]
    #    lista_de_xml = sorted(lista_de_xml)
        
    # Listamos los archivos presentes en thumbnails
    #lista_de_thumb = []
    #for (dirpath, dirnames, filenames) in os.walk("thumbnails"):
    #    lista_de_thumb += [os.path.join(dirpath, file) for file in filenames]
    #    lista_de_thumb = sorted(lista_de_thumb)
        
    # Para cada xml, hay que extraer los datos de interes
    registros = []
    for i in range(len(lista_de_xml)):
        
        print(f"Procesando archivo {i+1} de {len(lista_de_xml)}")
        # Primero, extraemos el nombre de archivo comprimido original
        #nombre_comprimido = lista_de_archivos[i].split("\\")[1]
        nombre_comprimido = lista_nombres_comprimidos[i]
        
        # Extraemos la ruta del thumbnail
        ruta_thumb = "<img src='"+lista_de_thumb[i]+"' width='100'>"
        
        # Luego, extraemos del parse del xml cada campo de interes
        tree = ET.parse(lista_de_xml[i])    
        root = tree.getroot()   
        
        rawdatafn = tree.find("RawdataFileName").text.split("/")[5]
        satelite = tree.find("satelliteId").text
        sensor = tree.find("sensorId").text
        escena = int(tree.find("sceneId").text)
        orbita = int(tree.find("orbitId").text)
        fecha_captura = tree.find("Scene_imagingStartTime").text
        ano = int(fecha_captura.split(" ")[0])
        mes = int(fecha_captura.split(" ")[1])
        dia = int(fecha_captura.split(" ")[2])
        lat_central = float(tree.find("sceneCenterLat").text)
        long_central = float(tree.find("sceneCenterLong").text)
        data_ul_lat = float(tree.find("dataUpperLeftLat").text)
        data_ul_long = float(tree.find("dataUpperLeftLong").text)
        data_ur_lat = float(tree.find("dataUpperRightLat").text)
        data_ur_long = float(tree.find("dataUpperRightLong").text)
        data_ll_lat = float(tree.find("dataLowerLeftLat").text)
        data_ll_long = float(tree.find("dataLowerLeftLong").text)
        data_lr_lat = float(tree.find("dataLowerRightLat").text)
        data_lr_long = float(tree.find("dataLowerRightLong").text)
        elevacion_solar = float(tree.find("sunElevation").text)
        azimuth_solar = float(tree.find("sunAzimuth").text)  
        porcentaje_nubes = int(tree.find("cloudCoverage").text)
        irradiancia_solar = float(tree.find("SolarIrradiance").text)
        K = float(float(root[93][0].text)) # Ojo, esto sale de la posicion en el archivo xml
        B = float(float(root[93][1].text)) # Ojo, esto sale de la posicion en el archivo xml 
        altitud_satelite = float(tree.find("Satellite_Altitude").text)
        angulo_zenit_satelite = float(tree.find("satZenithAngle").text)
        angulo_azimuth_satelite = float(tree.find("satAzimuthAngle").text)
        angulo_roll = float(tree.find("satOffNadir").text)  
        
        # Construimos un dataframe con estos datos
        datos = [satelite, sensor, orbita, escena, ano, mes, dia, long_central, lat_central,
                 data_ul_long, data_ul_lat, data_ur_long, data_ur_lat, data_lr_long, data_lr_lat,
                 data_ll_long, data_ll_lat, elevacion_solar, azimuth_solar, porcentaje_nubes, irradiancia_solar,
                 K, B, altitud_satelite, angulo_zenit_satelite, angulo_azimuth_satelite, angulo_roll, nombre_comprimido,
                 rawdatafn, ruta_thumb]
        
        # Agregamos a la lista de registros
        registros.append(datos)
        
    # Convertimos la lista de listas a dataframe
    columnas = ["satelite", "sensor", "orbita", "escena", "ano", "mes", "dia", "long_central",
                "lat_central", "data_ul_long", "data_ul_lat", "data_ur_long", "data_ur_lat", 
                "data_lr_long", "data_lr_lat", "data_ll_long", "data_ll_lat", "elevacion_solar", 
                "azimuth_solar", "porcentaje_nubes", "irradiancia_solar", "K", "B", "altitud_satelite",
                "angulo_zenit_satelite", "angulo_azimuth_satelite", "angulo_roll", "nombre_comprimido",
                "rawdata", "thumbnail"]
    
    df = pd.DataFrame(registros, columns=columnas)
    
    # Vamos a agregar la fecha como columna YYYY-MM-DD
    df["year"] = df["ano"]
    df["month"] = df["mes"]
    df["day"] = df["dia"]
    serie_fecha = pd.to_datetime(df[["year", "month", "day"]])
    df["fecha"] = serie_fecha.dt.strftime('%Y-%m-%d')
    # Movemos la fecha a la 7ma columna y la borramos del final
    df.insert(7, "fecha", df.pop("fecha"))
    df.pop("year")
    df.pop("month")
    df.pop("day")

    # Vamos a incorporar la informacion de los estados que coinciden con la coord central de la imagen
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.long_central, df.lat_central))
    gdf.crs = "EPSG:4326"
    
    # Se hace el join con el shapefile
    joined = gpd.sjoin(estados_venezuela, gdf, how="right")

    # Eliminamos las columnas innecesarias
    joined = joined.drop(columns=["index_left", "ID", "geometry"])
    
    # Escribimos el dataframe como csv
    joined = joined.rename(columns={"ESTADO":"estado"})
    
    joined.to_csv("registros_VRSS.csv", index=False, encoding="utf-16")
    
    # Borramos la carpeta xml con su contenido
    shutil.rmtree("xml")

    print("Procesamiento de imagenes finalizado!")
    
    # Ahora vamos a hacer el push a la DB
    
    # Cargamos los parametros de configuracion de la BD
    # Por defecto, el nombre es database.ini
    try:
        params = config()
        mensaje_bd = "Credenciales de BD cargadas correctamente!"
        print(mensaje_bd)
        # Si las credenciales se cargaron correctamente, True
        credentials = True
    except:
        mensaje_bd = "No puede cargar Credenciales de BD!"
        print(mensaje_bd)
        # Si las credenciales no se cargaron correctamente, False
        credentials = False
        
    # Va a cargar el archivo de registros previamente procesado y es el que va
    # a incorporar el poligono final para luego subir a la base de datos
    orbitas_csv = "registros_VRSS.csv"
    orbitas_final = "orbitas_procesadas.csv"
    
    print("###Cargando orbitas csv###")
    gdf = pd.read_csv(orbitas_csv,encoding='utf-16')
    
    print("###Creando Geodataframe###")
    gdf['centroide'] = gpd.points_from_xy(gdf.long_central, gdf.lat_central)
    gdf['ul'] = gpd.points_from_xy(gdf.data_ul_long, gdf.data_ul_lat)
    gdf['ur'] = gpd.points_from_xy(gdf.data_ur_long, gdf.data_ur_lat)
    gdf['lr'] = gpd.points_from_xy(gdf.data_lr_long, gdf.data_lr_lat)
    gdf['ll'] = gpd.points_from_xy(gdf.data_ll_long, gdf.data_ll_lat)
    gdf['footprint'] = 0
    gdf = gpd.GeoDataFrame(gdf, geometry='centroide', crs="EPSG:4326")
    
    print("###Cargando huellas a Geodataframe###")
    for i, g in gdf.iterrows():
        gdf.footprint[i] = Polygon([gdf.ul[i], gdf.ur[i], gdf.lr[i], gdf.ll[i]])
    
    print("###Limpiando Geodataframe###")
    gdf.drop(columns=["centroide", "ul", "ur", "lr", "ll" ], inplace=True)
    
    print("###Convirtiendo a utf16 ###")
    gdf.to_csv(orbitas_final,  encoding='utf-16', index=False)
    gdf = pd.read_csv(orbitas_final, encoding='utf-16')
    gdf = gpd.GeoDataFrame(gdf, geometry=gpd.points_from_xy(gdf.long_central, gdf.lat_central))
    
    print("###Guardando formatos CSV utf16 SHP GEOJSON ###")
    # Ojo que los nombres estan hardcoded, y se guardan en la raiz
    gdf.to_file(f"orbitas_final.shp", driver='ESRI Shapefile') # Ojo con la f
    gdf.to_file("orbitas_final.geojson", driver="GeoJSON") 
    gdf.to_csv(orbitas_final, header=False, index=False)
    
    print("###Exportando a Postgres Database###")
    # Los parametros de la conexion estan en la variable params
    # Ojo que el nombre de la tabla esta hardcoded
    dtb = Table('vrss2', MetaData(),schema='public').drop(connection(params['host'],
                                                                     params['port'],
                                                                     params['user'],
                                                                     params['password'],
                                                                     params['database'])) 
    gdf.to_postgis("vrss2", connection(params['host'],
                                       params['port'],
                                       params['user'],
                                       params['password'],
                                       params['database']))
    
    print("###Exito###")
    print("Proceso completo finalizado!")
    