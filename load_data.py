import os, zipfile, re, shutil, hashlib

import rasterio
from rasterio.transform import GroundControlPoint

import lxml.etree as ET

import pandas as pd

from dotenv import load_dotenv
load_dotenv()

from osgeo import gdal, osr

from shapely.geometry.polygon import Polygon

from geo.Geoserver import Geoserver

from sqlalchemy import insert

from app.models.satellite_images_table import *

from app.models.models import DatabaseConfig

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
                #print("Extrayendo archivo {}".format(name))
                #zip.extract(name, './'+carpeta)
                zip.extract(name, carpeta)
                #print("Extraccion de archivo finalizada!\n")
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
                #print("Extrayendo archivo {}".format(name))
                #zip.extract(name, './'+carpeta)
                zip.extract(name, carpeta)
                #print("Extraccion de archivo finalizada!\n")
                return name

# Create geotif from thumbnail
def thumb_to_geothumb(input_path, dataUpperLeftLong, dataUpperLeftLat,
    dataLowerLeftLong, dataLowerLeftLat, dataUpperRightLong, dataUpperRightLat,
    dataLowerRightLong, dataLowerRightLat, output_path):
        
    with rasterio.open(input_path) as src_ds:

        gcps = [
            #GroundControlPoint(row=0, col=0, x=-67.431863, y=9.880736),
            #GroundControlPoint(row=src_ds.height, col=0, x=-67.495767, y=9.582391),
            #GroundControlPoint(row=0, col=src_ds.width, x=-67.101699, y=9.81232),
            #GroundControlPoint(row=src_ds.height, col=src_ds.width, x=-67.165838, y=9.514058)

            # Topleft
            GroundControlPoint(
                row=0, col=0, x=dataUpperLeftLong, y=dataUpperLeftLat
            ),
            # Bottomleft
            GroundControlPoint(
                row=src_ds.height, col=0, x=dataLowerLeftLong, y=dataLowerLeftLat
            ),
            # Topright
            GroundControlPoint(
                row=0, col=src_ds.width, x=dataUpperRightLong, y=dataUpperRightLat
            ),
            # Bottomright
            GroundControlPoint(
                row=src_ds.height, col=src_ds.width, x=dataLowerRightLong, y=dataLowerRightLat
            )
        ]
        transform = rasterio.transform.from_gcps(gcps)
        
        with rasterio.open(
            output_path,
            "w",
            driver = "GTiff",
            height = src_ds.height,
            width  = src_ds.width,
            count  = src_ds.count,
            dtype  = src_ds.read().dtype,
        ) as dst:
            crs     = rasterio.crs.CRS({"init": "epsg:4326"})
            dst.crs = crs
            dst.transform = transform
            dst.write(src_ds.read())

# Funcion para crear geotiff a partir de thumbnail
"""
def thumb_to_geothumb(input_path, dataUpperLeftLong, dataUpperLeftLat,
    dataLowerLeftLong, dataLowerLeftLat, dataUpperRightLong, dataUpperRightLat,
    dataLowerRightLong, dataLowerRightLat, output_path):

        src_ds = rasterio.open(input_path)

        options = "-of GTiff\
            -gcp {} {} {} {}\
            -gcp {} {} {} {}\
            -gcp {} {} {} {}\
            -gcp {} {} {} {}\
            gdalwarp -r near -a_srs EPSG:4326".format(
            #gdalwarp -r near -co EPSG:4326".format(
                0, 0, dataUpperLeftLong, dataUpperLeftLat,                         # Topleft
                0, src_ds.height, dataLowerLeftLong, dataLowerLeftLat,             # Bottomleft
                src_ds.width, 0, dataUpperRightLong, dataUpperRightLat,            # Topright
                src_ds.width, src_ds.height, dataLowerRightLong, dataLowerRightLat # Bottomright
            )

        ds = gdal.Translate(output_path, input_path, options=options)
"""
"""
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
"""
    
# Aca comienza script
if __name__ == "__main__":
    # Lista los archivos comprimidos de imagenes presentes en la carpeta imagenes
    source_dir_      = "/load_data"
    carpeta_imagenes = os.path.expanduser("~") + source_dir_

    target_dir_ = "/data"
    target_dir  = os.path.expanduser("~") + target_dir_
    
    lista_de_archivos = []
    for (dirpath, dirnames, filenames) in os.walk(carpeta_imagenes):
        lista_de_archivos += [os.path.join(dirpath, file) for file in filenames]
        lista_de_archivos = sorted(lista_de_archivos)

    # Para cada uno de los archivos de imagenes, se extraen los xml
    lista_nombres_comprimidos = []
    lista_de_xml              = []
    lista_de_thumb            = []
    compressed_file_list      = []
    folder_names              = []
    for archivo in lista_de_archivos:
        print("Procesing {}".format(archivo))
        folder_name = hashlib.md5(str(os.path.basename(archivo[:-9])).encode()).hexdigest()
        folder_names.append(folder_name)
        
        lista_nombres_comprimidos.append(archivo.split("\\")[0])

        print("Extracting .xml")
        lista_de_xml.append(carpeta_imagenes+"/"+folder_name+"/"+unpackXML(archivo, carpeta_imagenes+"/"+folder_name))

        print("Extracting .jpg")
        lista_de_thumb.append(carpeta_imagenes+"/"+folder_name+"/"+unpackThumb(archivo, carpeta_imagenes+"/"+folder_name))

        # Move the compressed file to the new folder
        shutil.move(archivo, carpeta_imagenes+"/"+folder_name+"/"+os.path.basename(archivo))
        
        compressed_file_list.append(carpeta_imagenes+"/"+folder_name+"/"+os.path.basename(archivo))
        print("Done\n")
        
    # Para cada xml, hay que extraer los datos de interes
    registros = []
    for i in range(len(lista_de_xml)):
        print(f"Procesando archivo {i+1} de {len(lista_de_xml)}")

        custom_id = folder_names[i]

        compressed_file_path_ = compressed_file_list[i]
        compressed_file_path  = compressed_file_path_.replace(source_dir_, target_dir_)
        
        # Primero, extraemos el nombre de archivo comprimido original
        #compressed_name = lista_nombres_comprimidos[i]
        
        # Extraemos la ruta del thumbnail
        ruta_thumb = lista_de_thumb[i]
        
        # Luego, extraemos del parse del xml cada campo de interes
        tree = ET.parse(lista_de_xml[i])    
        root = tree.getroot()   
        
        rawdatafn = tree.find("RawdataFileName").text.split("/")[5]
        satelite  = tree.find("satelliteId").text
        sensor    = tree.find("sensorId").text
        escena    = int(tree.find("sceneId").text)
        orbita    = int(tree.find("orbitId").text)
        
        fecha_captura = tree.find("Scene_imagingStartTime").text
        ano           = int(fecha_captura.split(" ")[0])
        mes           = int(fecha_captura.split(" ")[1])
        dia           = int(fecha_captura.split(" ")[2])
        capture_date  = "{}-{}-{}".format(ano, mes, dia)
        
        lat_central  = float(tree.find("sceneCenterLat").text)
        long_central = float(tree.find("sceneCenterLong").text)
        data_ul_lat  = float(tree.find("dataUpperLeftLat").text)
        data_ul_long = float(tree.find("dataUpperLeftLong").text)
        data_ur_lat  = float(tree.find("dataUpperRightLat").text)
        data_ur_long = float(tree.find("dataUpperRightLong").text)
        data_ll_lat  = float(tree.find("dataLowerLeftLat").text)
        data_ll_long = float(tree.find("dataLowerLeftLong").text)
        data_lr_lat  = float(tree.find("dataLowerRightLat").text)
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
        
        elevacion_solar   = float(tree.find("sunElevation").text)
        azimuth_solar     = float(tree.find("sunAzimuth").text)  
        porcentaje_nubes  = int(tree.find("cloudCoverage").text)
        irradiancia_solar = float(tree.find("SolarIrradiance").text)
        
        K = float(float(root[93][0].text)) # Ojo, esto sale de la posicion en el archivo xml
        B = float(float(root[93][1].text)) # Ojo, esto sale de la posicion en el archivo xml
        
        altitud_satelite        = float(tree.find("Satellite_Altitude").text)
        angulo_zenit_satelite   = float(tree.find("satZenithAngle").text)
        angulo_azimuth_satelite = float(tree.find("satAzimuthAngle").text)
        angulo_roll             = float(tree.find("satOffNadir").text)
        
        # Para cada uno, genero el geothumb
        print("Creating .tif")
        #thumb_a_geothumb(lista_de_thumb[i], data_ul_long, data_ul_lat, lista_de_thumb[i]+".tif")
        thumb_to_geothumb(
            lista_de_thumb[i],
            float(tree.find("dataUpperLeftLong").text), float(tree.find("dataUpperLeftLat").text),
            float(tree.find("dataLowerLeftLong").text), float(tree.find("dataLowerLeftLat").text),
            float(tree.find("dataUpperRightLong").text), float(tree.find("dataUpperRightLat").text),
            float(tree.find("dataLowerRightLong").text), float(tree.find("dataLowerRightLat").text),
            lista_de_thumb[i]+".tif"
        )
        
        #ruta_geothumb = "geothumbs/"+lista_de_thumb[i].split("/")[2].split(".")[0]+".tif"
        ruta_geothumb = lista_de_thumb[i]+".tif"

        metadata_xml = str(open(lista_de_xml[i], "r").read())
        
        # Construimos un dataframe con estos datos
        datos = [
            custom_id, satelite, sensor, orbita, escena, capture_date,
            str(image_coordinates), str(cutted_image_shape), elevacion_solar,
            azimuth_solar, porcentaje_nubes, irradiancia_solar, K, B,
            altitud_satelite, angulo_zenit_satelite, angulo_azimuth_satelite,
            angulo_roll, rawdatafn, ruta_thumb, ruta_geothumb, compressed_file_path,
            metadata_xml
        ]
        
        # Agregamos a la lista de registros
        registros.append(datos)
        
    # Convertimos la lista de listas a dataframe
    columns = [
        "custom_id", "satellite", "sensor", "orbit", "scene", "capture_date",
        "image_coordinates", "cutted_image_shape", "solar_elevation",
        "solar_azimuth", "cloud_percentage", "solar_irradiance", "k_val",
        "b_val", "satellite_altitude", "zenit_satellite_angle",
        "satellite_azimuth_angle", "roll_angle", "rawdatafn", "thumb_path",
        "geothumb_path", "compressed_file_path", "metadata_xml"
    ]
    
    df = pd.DataFrame(registros, columns=columns)

    DB          = os.getenv("DB")
    DB_HOST     = os.getenv("DB_HOST")
    DB_NAME     = os.getenv("DB_NAME")
    DB_USER     = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_PORT     = os.getenv("DB_PORT")
    
    DbConn       = DatabaseConfig(DB, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)
    conn, engine = DbConn.connection()

    for index, row in df.iterrows():
        # Upload to database
        tmp_df = row.to_frame().T
        tmp_df = tmp_df.reset_index(drop=True)
        #tmp_df.to_sql("satellite_images", con=engine, if_exists="append", index=False)

        stmt = insert(SatelliteImages).values(
            custom_id               = tmp_df["custom_id"][0],
            satellite               = tmp_df["satellite"][0],
            sensor                  = tmp_df["sensor"][0],
            orbit                   = tmp_df["orbit"][0],
            scene                   = tmp_df["scene"][0],
            capture_date            = tmp_df["capture_date"][0],
            image_coordinates       = tmp_df["image_coordinates"][0],
            cutted_image_shape      = tmp_df["cutted_image_shape"][0],
            solar_elevation         = tmp_df["solar_elevation"][0],
            solar_azimuth           = tmp_df["solar_azimuth"][0],
            cloud_percentage        = tmp_df["cloud_percentage"][0],
            solar_irradiance        = tmp_df["solar_irradiance"][0],
            k_val                   = tmp_df["k_val"][0],
            b_val                   = tmp_df["b_val"][0],
            satellite_altitude      = tmp_df["satellite_altitude"][0],
            zenit_satellite_angle   = tmp_df["zenit_satellite_angle"][0],
            satellite_azimuth_angle = tmp_df["satellite_azimuth_angle"][0],
            roll_angle              = tmp_df["roll_angle"][0],
            #compressed_name         = tmp_df["compressed_name"][0],
            rawdatafn               = tmp_df["rawdatafn"][0],
            thumb_path              = tmp_df["thumb_path"][0],
            geothumb_path           = tmp_df["geothumb_path"][0],
            compressed_file_path    = tmp_df["compressed_file_path"][0],
            metadata_xml            = tmp_df["metadata_xml"][0],
        )
        try:
            result = conn.execute(stmt)
            conn.commit()
        except Exception as e:
            print("\n\nOmitting error on database\n\n")

        # Upload to geoserver
        GEOSERVER_URL      = os.getenv("GEOSERVER_URL")
        GEOSERVER_USER     = os.getenv("GEOSERVER_USER")
        GEOSERVER_PASSWORD = os.getenv("GEOSERVER_PASSWORD")
        
        geo = Geoserver(
            str(GEOSERVER_URL),
            username = str(GEOSERVER_USER),
            password = str(GEOSERVER_PASSWORD)
        )

        try:
            # Create workspace
            workspace = "satellite_images"
            tmp       = geo.create_workspace(workspace=workspace)
        except Exception as e:
            if "409" in str(e):
                print("Workspace already exist")
                print("Continue...")
        finally:
            # For uploading raster data to the geoserver
            #path      = r"/home/zurg/Desktop/code_testing/geoportal/sample_data/data/satellite_images/test.tif"
            path       = tmp_df["geothumb_path"][0]
            layer_name = tmp_df["custom_id"][0]

            geo.create_coveragestore(layer_name=layer_name, path=path, workspace=workspace)
    conn.close()

    file_names = os.listdir(carpeta_imagenes)
    for file_name in file_names:
        try:
            shutil.move(os.path.join(carpeta_imagenes, file_name), target_dir)
        except Exception as e:
            print("\n\nOmitting error on filesystem\n\n")

    print("\n\nProcesamiento finalizado!")
