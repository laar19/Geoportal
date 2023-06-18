import requests, json

from geo.Geoserver import Geoserver

geo = Geoserver("http://localhost:8080/geoserver", username="admin", password="geoserver")
#geo = Geoserver("http://localhost:8600/geoserver", username="admin", password="geoserver")

#print(help(geo))

workspace = "test_workspace"
print(geo.create_workspace(workspace=workspace))

datastore = "test_datastore"
#path      = r"/home/zurg/Desktop/code_testing/geoportal/sample_data/data/layers/Estados.shp"
#print(geo.create_datastore(name=datastore, path=path, workspace=workspace))
path      = r"/home/zurg/Desktop/code_testing/geoportal/sample_data/data/layers/Estados.zip"
print(geo.create_shp_datastore(path=path, store_name="test_datastore", workspace="test_workspace"))

"""
# get layer
layer = geo.get_layer(layer_name="Estados")
print(layer)

# get all the layers
layers = geo.get_layers()
print(layers)
"""


# create feature store and publish layer
#geo.create_featurestore(store_name="geo_data", workspace="demo", db="geoportal2", host="localhost", pg_user="postgres", pg_password="root")
#geo.publish_featurestore(store_name="geo_data", pg_table="layers.Estado")

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
