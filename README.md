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
### Setup PostGis database first
> Edit deployment/postgis/docker-compose.yml to configure user, password and ports   
> docker compose up deployment/postgis/docker-compose.yml   
### Setup Geoserver
> Copy deployment/geoserver/dot_env_example.txt to .env
> Edit deployment/geoserver/.env to configure user, password and ports   
> docker compose up deployment/geoserver/docker-compose.yml   
### Setup anaconda environment
> conda env create -n geoportal -f environment.yml   
### Add credentials
> copy dot_env_example.txt to .env
> Edit .env to configure user, password and ports   
### Run
> python main.py   

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
