import requests, json

from geo.Geoserver import Geoserver

"""
# get layer
layer = geo.get_layer(layer_name="Estados")
print(layer)

# get all the layers
layers = geo.get_layers()
print(layers)
"""

"""
# CREATE WORKSPACE
geoserver_enpoint = "http://localhost:8600/geoserver/rest/workspaces"
user              = "admin"
password          = "geoserver"

data    = {"workspace": {"name": "test_workspace"}}

url     = f"{geoserver_enpoint}"
headers = {"Content-type": "application/json"}

response = requests.post(url, auth=(user, password), data=json.dumps(data), headers=headers)
print(response)
"""

"""
geoserver_enpoint = "http://localhost:8600/geoserver/rest/workspaces"
user              = "admin"
password          = "geoserver"

workspace  = "blah"
store      = "test-store"
data       = f"file://sample_data/data/layers/Estados.shp"
file_type  = "shp"
store_type = "datastores" if file_type == 'shp' else "coveragestores"

url     = f"{geoserver_enpoint}/rest/workspaces/{workspace}/{store_type}/{store}/external.{file_type}"
headers = {"Content-type": "text/plain"}

result = requests.put(url, auth=(user, password), data=data, headers=headers)
print(result)
"""

"""
# Upload shapefile

# Credentials
geo = Geoserver("http://localhost:8080/geoserver", username="admin", password="geoserver")

# Create workspace
workspace = "test_workspace"
print(geo.create_workspace(workspace=workspace))

# Create datastore
datastore = "test_datastore"
path      = r"/home/zurg/Desktop/code_testing/geoportal/sample_data/data/layers/Estados.zip"
print(geo.create_shp_datastore(path=path, store_name="test_datastore", workspace=workspace))

# create feature store and publish layer
#geo.create_featurestore(store_name="geo_data", workspace="demo", db="geoportal2", host="localhost", pg_user="postgres", pg_password="root")
#geo.publish_featurestore(store_name="geo_data", pg_table="layers.Estado")
"""

# Upload raster

# Credentials
geo = Geoserver("http://localhost:8600/geoserver", username="admin", password="admin")

# Create workspace
workspace = "custom_rasters"
print(geo.create_workspace(workspace=workspace))

# For uploading raster data to the geoserver
#path      = r"/home/zurg/Desktop/code_testing/geoportal/sample_data/data/satellite_images/test.tif"
path      = r"/home/zurg/Desktop/code_testing/geoportal/sample_data/geoserver/output2.tif"
geo.create_coveragestore(layer_name="output2", path=path, workspace=workspace)

path      = r"/home/zurg/Desktop/code_testing/geoportal/sample_data/geoserver/output3.tif"
geo.create_coveragestore(layer_name="output3", path=path, workspace=workspace)

path      = r"/home/zurg/Desktop/code_testing/geoportal/sample_data/geoserver/test.tif"
geo.create_coveragestore(layer_name="test", path=path, workspace=workspace)
