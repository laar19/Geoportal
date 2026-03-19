# Geoportal

## Catalog for satellite images

## Technical information
- Python 3.10.x
- Flask framework
- Leaflet
- Postgresql + Postgis
- Geoserver
- Distributed under the GNU Affero General Public License (AGPLv3)

## Deployment with Docker (recommended)

Follow these three steps to run the full stack: GeoServer, PostGIS, and the Geoportal web app.

### 1) Configure GeoServer env variables and run the containers

- Path: `geoserver/`
- Copy example env and edit it as needed (admin credentials and ports):

```sh
cp geoserver/dot_env_example.txt geoserver/.env
# edit geoserver/.env if you need to change ports or credentials
```

- Start the stack (PostGIS for GeoServer, GeoServer, and Nginx proxy):

```sh
docker compose -f geoserver/docker-compose.yml --env-file geoserver/.env up -d
```

- Default URLs:
  - GeoServer: http://localhost:8870/geoserver
  - Nginx (forwarding to GeoServer): http://localhost:8893/geoserver

### 2) Configure PostGIS env variables and run the containers

- Path: `postgis/`
- Copy example env and edit it as needed (db name, user, password, and ports):

```sh
cp postgis/dot_env_example.txt postgis/.env
# edit postgis/.env to adjust POSTGRES_DB_NAME, POSTGRES_DB_USER, POSTGRES_DB_PASSWORD, and ports
```

- Start the stack (PostGIS + optional pgAdmin + Adminer):

```sh
docker compose -f postgis/docker-compose.yml --env-file postgis/.env up -d
```

- Default URLs/ports:
  - PostGIS: localhost:8871
  - pgAdmin: http://localhost:8872
  - Adminer: http://localhost:8873

- Optionally initialize database objects for the app:

```sh
python geoportal_app/setup_db.py
```

### 3) Configure Geoportal env variables, build the image, and run the container

- Path: `geoportal_app/`
- Copy example env and edit it to point to your running services:

```sh
cp geoportal_app/dot_env_example.txt geoportal_app/.env
# edit geoportal_app/.env if your ports/hosts differ
# Key vars (defaults):
#   POSTGRES_DB_HOST=172.19.0.1
#   POSTGRES_DB_PORT=8871
#   GEOSERVER_HOST=http://localhost
#   GEOSERVER_PORT=8870
#   HTTP_PORT=8893
#   WEB_HOST_PORT=8874
#   WEB_CONTAINER_PORT=8874
```

- Build and start the web app:

```sh
docker compose -f geoportal_app/docker-compose.yml --env-file geoportal_app/.env up -d --build
```

- Health check (container): http://localhost:8874/health
- App URL: http://localhost:8874

> Note: If you changed any ports in the `.env` files, make sure they are consistent across `geoserver/`, `postgis/`, and `geoportal_app/`.

## Sample data (optional)

### Sample raster data
1. Copy `load_data/load_raster_to_db/sample_data/` to your user home directory
2. Load rasters to the database:

```sh
python -m load_data.load_raster_to_db.load_raster_to_db
```

### Sample vector data
1. Copy `load_data/load_vector_to_db/sample_data/` to your user home directory
2. Load vectors to database:

```sh
python -m load_data.load_vector_to_db.1_shp_to_postgis
```

3. Publish vectors from PostGIS to GeoServer:

```sh
python -m load_data.load_vector_to_db.2_publish_from_postgis_to_geoserver
```

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

