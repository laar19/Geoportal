import hashlib 

from os      import listdir
from os.path import isfile, join, abspath

from geo.Geoserver import Geoserver

# Open .tif files
path  = "data/"
files = [f for f in listdir(path) if isfile(join(path, f))]

tif_files = []
for i in files:
    if ".tif" in i:
        #path = r"/abspath/file.tif"
        tif_files.append(abspath("data/"+i))

# Geoserver credentials
geo = Geoserver("http://172.19.0.3:8080/geoserver", username="admin", password="admin")

# Create workspace
workspace = "satellite_images"
try:
    print(geo.create_workspace(workspace=workspace))
except Exception as e:
    if "already exist" in str(e):
        pass

# Uploading raster data to geoserver
for i in tif_files:
    layer_name = hashlib.md5(i.encode("utf-8")).hexdigest()
    geo.create_coveragestore(layer_name=layer_name, path=i, workspace=workspace)
    print("Raster saved")

# Load data to postgis
