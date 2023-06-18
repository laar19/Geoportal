# Geoportal

## Catalog for satellite images

## Luis Acevedo  <laar@pm.me>

## Technical information:
Python 3.9   
Flask framework as backend.   
Openlayers 6 as mapping library.   
Postgresql + Postgis as database.   
Distributed under the GNU Affero General Public License (AGPLv3).

## Setup
### Setup PostGis database first
> add the credentials to /config/db_credentials.csv   
### Setup anaconda environment
> conda env create -n geoportal -f environment.yml   
### Run
> python main.py

## Credits:
- [Ronald Delgado](https://github.com/RDelgado1980)
- [Jackie Ng](https://github.com/jumpinjackie),[repository](https://github.com/jumpinjackie/bootstrap-viewer-template)
- [Tobias Bieniek](https://github.com/Turbo87), [repository](https://github.com/Turbo87/sidebar-v2) 
- [Matt Walker](https://github.com/walkermatt), [repository](https://github.com/walkermatt/ol-layerswitcher) 
- [David Shea](https://github.com/dashea), [repository](https://github.com/dashea/requests-file) 

## Reference templates:
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
