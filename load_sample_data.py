# Procesar archivos 2A para extraer informacion de metadata y crear .csv con datos
import os, zipfile, re, shutil, hashlib

import lxml.etree as ET

import pandas    as pd
import geopandas as gpd

from datetime import datetime as dtime

from osgeo import gdal, osr

from shapely.geometry.polygon import Polygon

from app.models.models import DatabaseConfig

# Leemos el shapefile de los estados de Venezuela    
#estados_venezuela = gpd.read_file("vzla_exterior.zip")

def create_folder(folder_name):
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)

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

    create_folder(carpeta)
    
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

    create_folder(carpeta)
    
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

# Funcion para crear geotiff a partir de thumbnail
def thumb_a_geothumb(ruta, upper_left_lon, upper_left_lat, output_name):
    
    # Abrimos el jpg segun la ruta
    jpg_file = gdal.Open(ruta)
    
    n_bands = jpg_file.RasterCount
    
    # Obtenemos las dimensiones de la imagen
    width = jpg_file.RasterXSize
    height = jpg_file.RasterYSize
    
    # Definimos la coordenada de la esquina superior izquierda
    # unica necesaria para la geotransform
    top_left = (upper_left_lon, upper_left_lat)
    
    # Definimos la proyeccion
    epsg_code = 4326
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(epsg_code)

    # Creamos el tiff a georeferenciar
    driver = gdal.GetDriverByName('GTiff')
    output_file = driver.Create(output_name, width, height, 3, gdal.GDT_Byte)
    
    if n_bands == 1:
        # Si es PAN
        pixel_size = 0.00110
    else:
        # Si en MSS
        pixel_size = 0.00110 # 0.00125 Original
        
    # Definimos la geotransform
    geotransform = (top_left[0], pixel_size, -0.00023, top_left[1], -0.00023, -pixel_size)
    output_file.SetGeoTransform(geotransform)

    # Se establece la proyeccion
    output_file.SetProjection(srs.ExportToWkt())
    
    # Se escriben los datos al tiff
    # Si es PAN
    if n_bands == 1:
        for i in range(3):
            band = jpg_file.GetRasterBand(1)
            data = band.ReadAsArray()
            output_file.GetRasterBand(i+1).WriteArray(data)
    else:
        # Si es MSS
        for i in range(3):
            band = jpg_file.GetRasterBand(i+1)
            data = band.ReadAsArray()
            output_file.GetRasterBand(i+1).WriteArray(data)
        
    # Se guarda el tiff y se cierran los archivos
    output_file.FlushCache()
    output_file = None
    jpg_file = None
    
# Aca comienza script
if __name__ == "__main__":
    """
    # En primer lugar, verifica si existe la carpeta "xml" y la crea si no existe
    if not os.path.exists("xml"):
        # Crea el directorio
        os.mkdir("xml")
        
    if not os.path.exists("thumbnails"):
        # Crea el directorio
        os.mkdir("thumbnails")
        
    if not os.path.exists("geothumbs"):
        # Crea el directorio
        os.mkdir("geothumbs")
    """
        
    # Lista los archivos comprimidos de imagenes presentes en la carpeta imagenes
    carpeta_imagenes = "sample_data"
    
    lista_de_archivos = []
    for (dirpath, dirnames, filenames) in os.walk(carpeta_imagenes):
        lista_de_archivos += [os.path.join(dirpath, file) for file in filenames]
        lista_de_archivos = sorted(lista_de_archivos)

    # Para cada uno de los archivos de imagenes, se extraen los xml
    lista_nombres_comprimidos = []
    lista_de_xml = []
    lista_de_thumb = []
    compressed_file_list = []
    for archivo in lista_de_archivos:
        #lista_nombres_comprimidos.append(archivo.split("\\")[1])
        lista_nombres_comprimidos.append(archivo.split("\\")[0])
        #lista_de_xml.append("xml/"+unpackXML(archivo, "xml"))
        lista_de_xml.append(archivo[:-9]+"/"+unpackXML(archivo, archivo[:-9]))
        #lista_de_thumb.append("thumbnails/"+unpackThumb(archivo, "thumbnails"))
        lista_de_thumb.append(archivo[:-9]+"/"+unpackThumb(archivo, archivo[:-9]))

        shutil.move(archivo, archivo[:-9]+"/"+os.path.basename(archivo))
        compressed_file_list.append(archivo[:-9]+"/"+os.path.basename(archivo))
        
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

        custom_id = hashlib.md5(str(dtime.now()).encode()).hexdigest()

        compressed_file_path = compressed_file_list[i]
        
        # Primero, extraemos el nombre de archivo comprimido original
        #nombre_comprimido = lista_de_archivos[i].split("\\")[1]
        compressed_name = lista_nombres_comprimidos[i]
        
        # Extraemos la ruta del thumbnail
        #ruta_thumb = "<img src='"+lista_de_thumb[i]+"' width='100'>"
        ruta_thumb = lista_de_thumb[i]
        
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
        capture_date = "{}-{}-{}".format(ano, mes, dia)
        
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

        image_coordinates = Polygon(
            [
                (tree.find("productUpperRightLong").text, tree.find("productUpperRightLat").text),
                (tree.find("productLowerRightLong").text, tree.find("productLowerRightLat").text),
                (tree.find("productLowerLeftLong").text, tree.find("productLowerLeftLat").text),
                (tree.find("productUpperLeftLong").text, tree.find("productUpperLeftLat").text)
            ]
        )

        cutted_image_shape = Polygon(
            [
                (tree.find("dataUpperRightLong").text, tree.find("dataUpperRightLat").text),
                (tree.find("dataLowerRightLong").text, tree.find("dataLowerRightLat").text),
                (tree.find("dataLowerLeftLong").text, tree.find("dataLowerLeftLat").text),
                (tree.find("dataUpperLeftLong").text, tree.find("dataUpperLeftLat").text),
            ]
        )
        
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
        
        # Para cada uno, genero el geothumb
        #thumb_a_geothumb(lista_de_thumb[i], data_ul_long, data_ul_lat, "geothumbs/"+lista_de_thumb[i].split("/")[2].split(".")[0]+".tif")
        
        #thumb_a_geothumb(lista_de_thumb[i], data_ul_long, data_ul_lat, lista_de_thumb[i].split("/")[2].split(".")[0]+".tif")
        thumb_a_geothumb(lista_de_thumb[i], data_ul_long, data_ul_lat, lista_de_thumb[i]+".tif")
        
        #ruta_geothumb = "geothumbs/"+lista_de_thumb[i].split("/")[2].split(".")[0]+".tif"
        ruta_geothumb = lista_de_thumb[i]+".tif"
        
        # Construimos un dataframe con estos datos
        """
        datos = [satelite, sensor, orbita, escena, ano, mes, dia, long_central, lat_central,
                 data_ul_long, data_ul_lat, data_ur_long, data_ur_lat, data_lr_long, data_lr_lat,
                 data_ll_long, data_ll_lat, elevacion_solar, azimuth_solar, porcentaje_nubes, irradiancia_solar,
                 K, B, altitud_satelite, angulo_zenit_satelite, angulo_azimuth_satelite, angulo_roll, nombre_comprimido,
                 rawdatafn, ruta_thumb, ruta_geothumb]
        """
                 
        datos = [
            custom_id, satelite, sensor, orbita, escena, capture_date, str(image_coordinates),
            str(cutted_image_shape), elevacion_solar, azimuth_solar, porcentaje_nubes,
            irradiancia_solar, K, B, altitud_satelite, angulo_zenit_satelite,
            angulo_azimuth_satelite, angulo_roll, compressed_name, rawdatafn,
            ruta_thumb, ruta_geothumb, compressed_file_path
        ]
        
        # Agregamos a la lista de registros
        registros.append(datos)
        
    # Convertimos la lista de listas a dataframe
    """
    columnas = ["satelite", "sensor", "orbita", "escena", "ano", "mes", "dia", "long_central",
                "lat_central", "data_ul_long", "data_ul_lat", "data_ur_long", "data_ur_lat", 
                "data_lr_long", "data_lr_lat", "data_ll_long", "data_ll_lat", "elevacion_solar", 
                "azimuth_solar", "porcentaje_nubes", "irradiancia_solar", "K", "B", "altitud_satelite",
                "angulo_zenit_satelite", "angulo_azimuth_satelite", "angulo_roll", "nombre_comprimido",
                "rawdata", "thumbnail", "geothumbnail"]
    """
    columns = [
        "custom_id", "satellite", "sensor", "orbit", "escene", "capture_date", "image_coordinates",
        "cutted_image_shape", "solar_elevation", "solar_azimuth", "cloud_percentage",
        "solar_irradiance", "k_val", "b_val", "satellite_altitude", "zenit_satellite_angle",
        "satellite_azimuth_angle", "roll_angle", "compressed_name", "rawdatafn",
        "thumb_path", "geothumb_path", "compressed_file_path"
    ]
    
    df = pd.DataFrame(registros, columns=columns)
    #df.to_csv("file1.csv")

    db = DatabaseConfig("config/db_credentials_geoportal.csv")
    conn, engine = db.connection()

    for index, row in df.iterrows():
        tmp_df = row.to_frame().T
        tmp_df.to_sql("satellite_images", con=engine, if_exists="append", index=False)
        

    """
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
    #joined = gpd.sjoin(estados_venezuela, gdf, how="right")

    # Eliminamos las columnas innecesarias
    joined = joined.drop(columns=["index_left", "ID", "geometry"])
    
    # Escribimos el dataframe como csv
    joined = joined.rename(columns={"ESTADO":"estado"})
    
    joined.to_csv("registros_VRSS.csv", index=False, encoding="utf-16")
    
    # Borramos la carpeta xml con su contenido
    shutil.rmtree("xml")
    """

    print("Procesamiento finalizado!")    
