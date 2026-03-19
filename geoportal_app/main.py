import os, shutil, pdb
import requests
import json
import geopandas as gpd
from sqlalchemy import text
import psycopg2
from psycopg2 import OperationalError

from pathlib import Path

from dotenv import load_dotenv

from flask          import Flask, render_template, jsonify, request
from flask          import flash, redirect, url_for, render_template_string
from flask_wtf      import CSRFProtect
from flask_paginate import Pagination, get_page_parameter

from shapely.geometry import Polygon

from sqlalchemy.orm   import sessionmaker

#from flask_sessionstore import Session 
#from flask_session_captcha import FlaskSessionCaptcha

from app.models.models    import DatabaseConfig
from app.models.functions import *
from app.functions        import *
from app.config           import *
from login_keycloak       import *

################################## Initialization ##################################
app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY
csrf = CSRFProtect(app)

# Enables server session 
#Session(app) 
# Initialize FlaskSessionCaptcha 
#captcha = FlaskSessionCaptcha(app)

################## Register ################
# Register Keycloak auth blueprint so routes like 'auth.login' are available
app.register_blueprint(auth_bp)
# Authentication removed; no user DB or login manager initialization

test_config = None

if test_config is None:
    # load the instance config, if it exists, when not testing
    app.config.from_pyfile("config.py", silent=True)
else:
    # load the test config if passed in
    app.config.update(test_config)

# ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

# Load environment variables
# Specify the path to .env file
env_paths = [
    Path(".env"), # Is the same as load_dotenv()
    Path("deployment/postgis/.env")
]
# Load the environment variables from the specified files
for i in env_paths:
    load_dotenv(dotenv_path=i)

# Default map config
MAP_ZOOM_LEVEL      = os.getenv("MAP_ZOOM_LEVEL")
MAP_LAT             = os.getenv("MAP_LAT")
MAP_LONG            = os.getenv("MAP_LONG")
map_config          = get_map_config(MAP_ZOOM_LEVEL, MAP_LAT, MAP_LONG)
DATA_GOOGLE_SITEKEY = os.getenv("DATA_GOOGLE_SITEKEY")

LEAFLET_TILE_URL    = os.getenv("LEAFLET_TILE_URL", "https://tile.openstreetmap.org/{z}/{x}/{y}.png")
LEAFLET_ATTRIBUTION = os.getenv("LEAFLET_ATTRIBUTION", '<a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>')
LEAFLET_MIN_ZOOM    = os.getenv("LEAFLET_MIN_ZOOM")
LEAFLET_ESRI_URL         = os.getenv("LEAFLET_ESRI_URL", "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{x}/{y}")
LEAFLET_ESRI_ATTRIBUTION = os.getenv(
    "LEAFLET_ESRI_ATTRIBUTION",
    "Tiles © Esri — Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community"
)
LEAFLET_TERRAIN_URL         = os.getenv("LEAFLET_TERRAIN_URL", "https://stamen-tiles.a.ssl.fastly.net/terrain/{z}/{x}/{y}.jpg")
LEAFLET_TERRAIN_ATTRIBUTION = os.getenv(
    "LEAFLET_TERRAIN_ATTRIBUTION",
    "Map tiles by Stamen Design, under CC BY 3.0 — Data © OpenStreetMap contributors"
)
LEAFLET_DARK_URL           = os.getenv("LEAFLET_DARK_URL", "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png")
LEAFLET_DARK_ATTRIBUTION   = os.getenv("LEAFLET_DARK_ATTRIBUTION", "© OpenStreetMap contributors © CARTO")
LEAFLET_DARK_SUBDOMAINS    = os.getenv("LEAFLET_DARK_SUBDOMAINS", "abcd")

# --- Connectivity checks ---
def check_db_connection() -> bool:
    """Check DB using the same SQLAlchemy path the app uses elsewhere."""
    try:
        POSTGRES_DB_TYPE     = os.getenv("POSTGRES_DB_TYPE")
        POSTGRES_DB_HOST     = os.getenv("POSTGRES_DB_HOST")
        POSTGRES_DB_NAME     = os.getenv("POSTGRES_DB_NAME")
        POSTGRES_DB_USER     = os.getenv("POSTGRES_DB_USER")
        POSTGRES_DB_PASSWORD = os.getenv("POSTGRES_DB_PASSWORD")
        POSTGRES_DB_PORT     = os.getenv("POSTGRES_DB_PORT")

        # First try via SQLAlchemy (same as the rest of the app)
        try:
            DbConn = DatabaseConfig(
                POSTGRES_DB_TYPE,
                POSTGRES_DB_USER,
                POSTGRES_DB_PASSWORD,
                POSTGRES_DB_HOST,
                POSTGRES_DB_PORT,
                POSTGRES_DB_NAME
            )
            conn, engine = DbConn.connection()
            conn.execute(text("SELECT 1"))
            conn.close()
            return True
        except Exception:
            # Fallback: try direct psycopg2 with a short timeout
            try:
                port = int(POSTGRES_DB_PORT or 5432)
                conn = psycopg2.connect(host=POSTGRES_DB_HOST, dbname=POSTGRES_DB_NAME, user=POSTGRES_DB_USER, password=POSTGRES_DB_PASSWORD, port=port, connect_timeout=2)
                cur = conn.cursor()
                cur.execute("SELECT 1")
                cur.close()
                conn.close()
                return True
            except Exception:
                return False
    except Exception:
        return False

def strtobool_env(val: str) -> bool:
    if val is None:
        return False
    return str(val).lower() in ("1", "true", "yes", "y", "t")

def check_geoserver_connection() -> bool:
    try:
        host = os.getenv("GEOSERVER_HOST", "http://localhost")
        port = os.getenv("GEOSERVER_PORT", "8080")
        public_url = os.getenv("GEOSERVER_PUBLIC_URL")
        timeout = (0.5, float(os.getenv("HTTP_TIMEOUT", "1.5")))
        verify = not strtobool_env(os.getenv("DISABLE_SSL_VERIFY"))

        candidates = []
        if public_url:
            pu = public_url[:-1] if public_url.endswith('/') else public_url
            candidates.append(pu)
        # fallback to host:port and host-only
        base_host_port = f"{host}:{port}" if ":" not in host.split('//')[-1] else host
        candidates.append(base_host_port)
        candidates.append(host)

        # For each base, try common WMS/OWS paths and the web UI
        test_paths = [
            "/wms?service=WMS&request=GetCapabilities",
            "/ows?service=WMS&request=GetCapabilities",
            "/geoserver/wms?service=WMS&request=GetCapabilities",
            "/geoserver/ows?service=WMS&request=GetCapabilities",
            "/geoserver/web/",
        ]
        for base in candidates:
            for path in test_paths:
                url = f"{base}{path}"
                try:
                    r = requests.get(url, timeout=timeout, verify=verify)
                    if r.status_code < 500:
                        return True
                except Exception:
                    continue
        return False
    except Exception:
        return False

@app.route("/health/geoserver")
def health_geoserver():
    try:
        ok = check_geoserver_connection()
        return jsonify({"ok": bool(ok)}), 200
    except Exception:
        return jsonify({"ok": False}), 200

@app.route("/")
@app.route("/index")
@login_required
def index_leaflet():
    # Render immediately; do not block on GeoServer health
    DB_OK = check_db_connection()
    GEOSERVER_OK = None  # unknown at render time; will be checked client-side
    return render_template(
        "index.html",
        geoserver_config    = False,
        layers              = False,
        result              = False,
        map_config          = map_config,
        pagination          = False,
        error_              = False,
        DATA_GOOGLE_SITEKEY = DATA_GOOGLE_SITEKEY,
        LEAFLET_TILE_URL    = LEAFLET_TILE_URL,
        LEAFLET_ATTRIBUTION = LEAFLET_ATTRIBUTION,
        LEAFLET_MIN_ZOOM    = LEAFLET_MIN_ZOOM,
        LEAFLET_ESRI_URL         = LEAFLET_ESRI_URL,
        LEAFLET_ESRI_ATTRIBUTION = LEAFLET_ESRI_ATTRIBUTION,
        LEAFLET_TERRAIN_URL         = LEAFLET_TERRAIN_URL,
        LEAFLET_TERRAIN_ATTRIBUTION = LEAFLET_TERRAIN_ATTRIBUTION,
        LEAFLET_DARK_URL           = LEAFLET_DARK_URL,
        LEAFLET_DARK_ATTRIBUTION   = LEAFLET_DARK_ATTRIBUTION,
        LEAFLET_DARK_SUBDOMAINS    = LEAFLET_DARK_SUBDOMAINS,
        DB_OK = DB_OK,
        GEOSERVER_OK = GEOSERVER_OK,
        GEOSERVER_PUBLIC_URL = os.getenv("GEOSERVER_PUBLIC_URL")
    )

@app.route("/search", methods=["GET"])
@login_required
def search():
    search   = True
    page     = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 5
    offset   = (page - 1) * per_page
        
    if request.method == "GET":
        POSTGRES_DB_TYPE     = os.getenv("POSTGRES_DB_TYPE")
        POSTGRES_DB_HOST     = os.getenv("POSTGRES_DB_HOST")
        POSTGRES_DB_NAME     = os.getenv("POSTGRES_DB_NAME")
        POSTGRES_DB_USER     = os.getenv("POSTGRES_DB_USER")
        POSTGRES_DB_PASSWORD = os.getenv("POSTGRES_DB_PASSWORD")
        POSTGRES_DB_PORT     = os.getenv("POSTGRES_DB_PORT")
        
        DbConn = DatabaseConfig(
            POSTGRES_DB_TYPE,
            POSTGRES_DB_USER,
            POSTGRES_DB_PASSWORD,
            POSTGRES_DB_HOST,
            POSTGRES_DB_PORT,
            POSTGRES_DB_NAME
        )
        conn, engine = DbConn.connection()
        Session      = sessionmaker(bind=engine)
        db_session   = Session()

        previous_map_config = {
            "zoom_level"   : request.args.get("zoom_level"),
            "center"       : request.args.get("center"),
            "search_status": bool(request.args.get("search_status"))
        }

        # If there is an image search
        if previous_map_config["search_status"]:
            map_config = previous_map_config
            
            # Coordinates are received as string, so they are splited by comma
            # and converted into list of tuples wich contains coordinate pairs
            # The list of tuples is converted then into list of lists
            coord_from_user =  request.args.get("coordinates").split(",")
            formatted_coord_from_user1 = [i for i in zip(coord_from_user[::2], coord_from_user[1::2])]
            formatted_coord_from_user2 = []
            for i in formatted_coord_from_user1:
                formatted_coord_from_user2.append(list(i))

            try:
                formatted_coord_from_user3 = Polygon(formatted_coord_from_user2)
            except Exception as e:
                formatted_coord_from_user3 = False

            geoserver_config = {}
            geoserver_config["return"]        = False
            geoserver_config["geoserver_url"] = None
            geoserver_config["workspace"]     = None
            geoserver_config["service"]       = None
            geoserver_config["format"]        = None
            geoserver_config["transparent"]   = None

            filters = {}

            filters["coordinates"] = formatted_coord_from_user3

            vectors_result = intersect(db_session, filters, engine)

            if vectors_result:
                result_render  = vectors_result.limit(per_page).offset(offset)

                layers = {}
                
                GEOSERVER_WORKSPACE   = None
                GEOSERVER_SERVICE     = None
                GEOERVER_FORMAT       = None
                GEOSERVER_TRANSPARENT = None

                for i in vectors_result.all():
                    layers[i.name] = {
                        "layer_type"           : "vector",
                        "custom_id"            : i.name,
                        "name"                 : i.name,
                        "geoserver_workspace"  : i.geoserver_workspace,
                        "geoserver_service"    : i.geoserver_service,
                        "geoserver_format"     : i.geoserver_format,
                        "geoserver_transparent": i.geoserver_transparent,
                    }

                    GEOSERVER_WORKSPACE   = i.geoserver_workspace
                    GEOSERVER_SERVICE     = i.geoserver_service
                    GEOERVER_FORMAT       = i.geoserver_format
                    GEOSERVER_TRANSPARENT = i.geoserver_transparent

                geoserver_config_ = get_geoserver_config(db_session)
                
                if geoserver_config["return"] == False:
                    geoserver_config["return"] = True
                    
                if geoserver_config["geoserver_url"] == None:
                    geoserver_config["geoserver_url"] = os.getenv("GEOSERVER_PUBLIC_URL") or geoserver_config_[0].url
                    
                if geoserver_config["workspace"] == None:
                    geoserver_config["workspace"] = GEOSERVER_WORKSPACE
                    
                if geoserver_config["service"] == None:
                    geoserver_config["service"] = GEOSERVER_SERVICE

                if geoserver_config["format"] == None:
                    geoserver_config["format"] = GEOERVER_FORMAT

                if geoserver_config["transparent"] == None:
                    geoserver_config["transparent"] = GEOSERVER_TRANSPARENT
                
                pagination = Pagination(
                    vectors_result.count(),
                    page          = page,
                    per_page      = per_page,
                    offset        = offset,
                    total         = vectors_result.count(),
                    search        = True,
                    record_name   = "Rasters",
                    css_framework = "bootstrap",
                    bs_version    = 5
                )
            else:
                # Added flash message for when no vectors are found
                flash("No results found for your search criteria.", "warning")
                return redirect(url_for("index_leaflet"))

    error_ = False
    
    if geoserver_config["return"] == False:
        geoserver_config = False
        layers           = False
        error_           = False

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        pagination_html = render_template_string("{{ pagination.links|safe }}", pagination=pagination)
        # If GeoServer is down, avoid rendering thumbnails that hit GeoServer
        ajax_gs_ok = check_geoserver_connection()
        if not ajax_gs_ok:
            results_html = '<div class="alert alert-warning" role="alert">GeoServer is unavailable. Layer previews are disabled.</div>'
        else:
            results_html = render_template("results.html", result=result_render, geoserver_config=geoserver_config)
        
        return jsonify({
            "pagination": pagination_html,
            "results"   : results_html
        })
    
    # Render search page immediately as well; do not block on GeoServer health
    DB_OK = check_db_connection()
    GEOSERVER_OK = None
    return render_template(
        "index.html",
        geoserver_config    = geoserver_config,
        layers              = layers,
        result              = result_render,
        map_config          = map_config,
        pagination          = pagination,
        error_              = error_,
        DATA_GOOGLE_SITEKEY = DATA_GOOGLE_SITEKEY,
        LEAFLET_TILE_URL    = LEAFLET_TILE_URL,
        LEAFLET_ATTRIBUTION = LEAFLET_ATTRIBUTION,
        LEAFLET_MIN_ZOOM    = LEAFLET_MIN_ZOOM,
        LEAFLET_ESRI_URL         = LEAFLET_ESRI_URL,
        LEAFLET_ESRI_ATTRIBUTION = LEAFLET_ESRI_ATTRIBUTION,
        LEAFLET_TERRAIN_URL         = LEAFLET_TERRAIN_URL,
        LEAFLET_TERRAIN_ATTRIBUTION = LEAFLET_TERRAIN_ATTRIBUTION,
        LEAFLET_DARK_URL           = LEAFLET_DARK_URL,
        LEAFLET_DARK_ATTRIBUTION   = LEAFLET_DARK_ATTRIBUTION,
        LEAFLET_DARK_SUBDOMAINS    = LEAFLET_DARK_SUBDOMAINS,
        DB_OK = DB_OK,
        GEOSERVER_OK = GEOSERVER_OK,
        GEOSERVER_PUBLIC_URL = os.getenv("GEOSERVER_PUBLIC_URL")
    )

# app name
@app.errorhandler(404)
def not_found(e):
    return render_template(
        "404.html",
        geoserver_config = False,
        layers           = False,
        result           = False,
        map_config       = map_config,
        pagination       = False,
        error_           = False
    )

@app.route('/upload', methods=['POST'])
def upload_files():
    # Configuration
    UPLOAD_FOLDER = 'uploads'
    GEOJSON_FOLDER = 'geojson_outputs'
    ALLOWED_EXTENSIONS = {'shp', 'dbf', 'shx', 'prj'}  # Shapefile components

    # Create necessary directories
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(GEOJSON_FOLDER, exist_ok=True)

    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['GEOJSON_FOLDER'] = GEOJSON_FOLDER

    # Increase maximum content length to 500MB (adjust based on your needs)
    app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    # Check if the post request has files
    if 'files[]' not in request.files:
        flash('No files selected')
        return redirect(url_for("index_leaflet"))
    
    files = request.files.getlist('files[]')
    
    # If user submits without selecting files
    if not files or files[0].filename == '':
        flash('No files selected')
        return redirect(url_for("index_leaflet"))
    
    # Clear upload folder for fresh start
    shutil.rmtree(app.config['UPLOAD_FOLDER'])
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Process uploaded files, preserving directory structure
    for file in files:
        if file and allowed_file(file.filename):
            file_path = file.filename.replace('\\', '/')  # Normalize path separators
            dir_path = os.path.dirname(file_path)
            
            # Create directory structure in upload folder
            if dir_path:
                upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], dir_path)
                os.makedirs(upload_dir, exist_ok=True)
            else:
                upload_dir = app.config['UPLOAD_FOLDER']
            
            # Save file preserving path
            filename = os.path.basename(file_path)
            filepath = os.path.join(upload_dir, filename)
            file.save(filepath)
    
    # Process each shapefile in the uploaded directory structure
    converted_count = process_uploaded_shapefiles(app, None)
    
    if converted_count > 0:
        flash(f'Successfully converted {converted_count} shapefile(s) to GeoJSON')
    else:
        flash('No valid shapefiles were found in the upload')
    
    return redirect(url_for("index_leaflet"))

@app.route('/download_layer/<layer_name>')
@login_required
def download_layer(layer_name):
    try:
        # Validate layer_name to prevent SQL injection or path traversal
        if not layer_name or not layer_name.isalnum() and not '_' in layer_name:
             flash("Invalid layer name", "error")
             return redirect(url_for("index_leaflet"))

        # Setup DB connection
        POSTGRES_DB_TYPE     = os.getenv("POSTGRES_DB_TYPE")
        POSTGRES_DB_HOST     = os.getenv("POSTGRES_DB_HOST")
        POSTGRES_DB_NAME     = os.getenv("POSTGRES_DB_NAME")
        POSTGRES_DB_USER     = os.getenv("POSTGRES_DB_USER")
        POSTGRES_DB_PASSWORD = os.getenv("POSTGRES_DB_PASSWORD")
        POSTGRES_DB_PORT     = os.getenv("POSTGRES_DB_PORT")
        
        db_url = f"{POSTGRES_DB_TYPE}://{POSTGRES_DB_USER}:{POSTGRES_DB_PASSWORD}@{POSTGRES_DB_HOST}:{POSTGRES_DB_PORT}/{POSTGRES_DB_NAME}"
        con = create_engine(db_url)
        
        # Check if table exists (in 'vectors' schema)
        sql = f"SELECT * FROM vectors.{layer_name}"
        
        # Read PostGIS layer -> GeoDataFrame
        gdf = gpd.read_postgis(sql, con, geom_col='geometry')
        
        # Drop internal columns if present
        cols_to_drop = ['id', 'user_id', 'geoserver_workspace', 'geoserver_service', 'geoserver_format', 'geoserver_transparent']
        for col in cols_to_drop:
            if col in gdf.columns:
                gdf = gdf.drop(columns=[col])
                
        # Return as JSON
        response = jsonify(json.loads(gdf.to_json()))
        response.headers["Content-Disposition"] = f"attachment; filename={layer_name}.json"
        return response

    except Exception as e:
        print(f"Error downloading layer {layer_name}: {e}")
        flash(f"Error downloading layer: {e}", "error")
        return redirect(url_for("index_leaflet"))

@app.after_request
def add_security_headers(response):
    # Remove any existing CSP headers
    for header in ['Content-Security-Policy', 'Content-Security-Policy-Report-Only']:
        if header in response.headers:
            del response.headers[header]
    
    return response

if __name__ == "__main__":
    csrf.init_app(app)

    FLASK_HOST  = os.getenv("FLASK_HOST")
    WEB_HOST_PORT  = os.getenv("WEB_HOST_PORT")
    FLASK_DEBUG = os.getenv("FLASK_DEBUG")
    app.run(host=FLASK_HOST, port=WEB_HOST_PORT, debug=FLASK_DEBUG)
