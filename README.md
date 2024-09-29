# Geoportal

## Catalog for satellite images

## Technical information
- Python 3.10.x
- Flask framework
- Leaflet
- Postgresql + Postgis
- Geoserver
- Distributed under the GNU Affero General Public License (AGPLv3)

## Setup
### Setup anaconda environment
> ```sh
> conda env create -n geoportal -f environment.yml
> ```
### Setup global environment variables
> 1. Copy ***dot_env_example.txt*** to ***.env***   
> 2. Edit ***.env*** to to setup environment variables   
### Setup Geoserver
> 1. Copy ***deployment/geoserver/dot_env_example.txt*** to ***deployment/geoserver/.env***   
> 2. Edit ***deployment/geoserver/.env*** to configure ***user, password*** and ***ports***   
> 3. In ***deployment/geoserver/*** folder run:   
> ```sh
> docker compose up
> ```    
### Setup PostGis database
> 1. Copy ***deployment/postgis/dot_env_example.txt*** to ***deployment/postgis/.env***   
> 2. Edit ***deployment/postgis/.env*** to configure ***user, password*** and ***ports***   
> 3. In ***deployment/postgis/*** folder run:   
> ```sh
> docker compose up
> ```    
> 4. Check and setup database and tables:   
> ```sh
> python setup_db.py
> ```
### Setup sample data
#### Setup sample raster data
> 1. Copy ***load_data/load_raster_to_db/sample_data*** folder  to user ***home*** directory   
> 2. Load rasters to database:   
> ```sh
> python -m load_data.load_raster_to_db.load_raster_to_db
> ```    
#### Setup sample vector data
> 1. Copy ***load_data/load_vector_to_db/sample_data*** folder  to user ***home*** directory   
> 2. Load vectors to database:   
> ```sh
> python -m load_data.load_vector_to_db.1_shp_to_postgis
> ```   
> 3. Load vectors from database to geoserver:   
> ```sh
> python -m load_data.load_vector_to_db.2_publish_from_postgis_to_geoserver
> ```
### Run app
> ```sh
> python main.py
> ```

## Credits
- [Luis Acevedo](mailto:laar@pm.me), [Linkedin](https://www.linkedin.com/in/luis-acevedo-662535260/)
- [Enmanuel Duque](mailto:duquenmanuel@gmail.com), [Linkedin](https://ve.linkedin.com/in/enmanuel-e-duque-c-80111939/en)
- [Ronald Delgado](https://github.com/RDelgado1980)
- [Jesús Cardiel](mailto:jesus.cardielg@gmail.com), [Linkedin](https://ve.linkedin.com/in/enmanuel-e-duque-c-80111939/en)

## Third party
- [Jackie Ng](https://github.com/jumpinjackie),[repository](https://github.com/jumpinjackie/bootstrap-viewer-template)
- [Tobias Bieniek](https://github.com/Turbo87), [repository](https://github.com/Turbo87/sidebar-v2)
- [Matt Walker](https://github.com/walkermatt), [repository](https://github.com/walkermatt/ol-layerswitcher)
- [David Shea](https://github.com/dashea), [repository](https://github.com/dashea/requests-file)
- https://github.com/tsparticles/404-templates
- https://github.com/jumpinjackie/bootstrap-viewer-template
- https://jumpinjackie.github.io/bootstrap-viewer-template/3-column/index.html
- https://github.com/Turbo87/sidebar-v2
- https://turbo87.github.io/sidebar-v2/examples/index.html
- https://turbo87.github.io/sidebar-v2/examples/ol3.html
- https://github.com/walkermatt/ol-layerswitcher
- https://raw.githack.com/walkermatt/ol-layerswitcher/master/examples/sidebar.html
- https://raw.githack.com/walkermatt/ol-layerswitcher/master/examples/layerswitcher.html
- https://openlayers.org/workshop/en/
- https://openlayersbook.github.io/ch08-interacting-with-your-map/example-11.html
- https://geojsonlint.com/
- https://geojson.io/#map=1/74/-35
- https://gist.github.com/marcopompili/f5e071ce646c5cf3d600828ace734ce7
- https://openlayers.org/en/latest/examples/image-vector-layer.html
- https://azouaoui-med.github.io/ostora-ol-reqjs/#
