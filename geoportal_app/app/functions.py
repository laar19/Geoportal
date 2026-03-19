import os

import geopandas as gpd

from pathlib import Path

from flask import flash, current_app

from sqlalchemy     import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv

from geo.Geoserver import Geoserver

from app.models.functions import get_geoserver_config

def process_uploaded_shapefiles(app, user_id):
    """
    Process all shapefiles in the uploads folder, store them in PostGIS database,
    and publish them to GeoServer
    """
    converted_count = 0
    
    # Load environment variables for database and geoserver connection
    env_paths = [
        Path(".env"),
        Path("deployment/geoserver/.env"),
        Path("deployment/postgis/.env")
    ]
    for i in env_paths:
        load_dotenv(dotenv_path=i)
    
    # DB connection setup
    POSTGRES_DB_TYPE       = os.getenv("POSTGRES_DB_TYPE")
    POSTGRES_DB_HOST       = os.getenv("POSTGRES_DB_HOST")
    POSTGRES_DB_NAME       = os.getenv("POSTGRES_DB_NAME")
    POSTGRES_DB_USER       = os.getenv("POSTGRES_DB_USER")
    POSTGRES_DB_PASSWORD   = os.getenv("POSTGRES_DB_PASSWORD")
    POSTGRES_DB_PORT       = os.getenv("POSTGRES_DB_PORT")
    
    # Create database connection
    engine = create_engine(
        f"{POSTGRES_DB_TYPE}://{POSTGRES_DB_USER}:{POSTGRES_DB_PASSWORD}@{POSTGRES_DB_HOST}:{POSTGRES_DB_PORT}/{POSTGRES_DB_NAME}"
    )
    
    # Create session
    Session    = sessionmaker(bind=engine)
    db_session = Session()
    
    # Create vectors schema if it doesn't exist
    schema_name = "vectors"
    try:
        with engine.connect() as conn:
            # Check if schema exists
            result = conn.execute(
                text("SELECT schema_name FROM information_schema.schemata WHERE schema_name = :schema_name"),
                {"schema_name": schema_name}
            )
            exists = result.fetchone()
            
            if not exists:
                # Create schema if it does not exist
                conn.execute(text(f"CREATE SCHEMA {schema_name}"))
                conn.commit()
                print(f"Schema '{schema_name}' created.")
    except Exception as e:
        flash(f"Error creating schema: {str(e)}", "error")
        return 0
    
    # List to store processed table names
    processed_tables = []
    
    # Walk through all directories in upload folder
    for root, _, files in os.walk(app.config['UPLOAD_FOLDER']):
        # Get shp files in this directory
        shp_files = [f for f in files if f.endswith('.shp')]
        
        if not shp_files:
            continue
        
        # Process each shapefile in this directory
        for shp_file in shp_files:
            try:
                # Full path to the shapefile
                shp_path = os.path.join(root, shp_file)
                
                # Get filename without extension for table name
                base_name = os.path.splitext(shp_file)[0].lower()
                table_name = base_name.replace(" ", "_").replace("-", "_")
                
                # Read the shapefile using geopandas
                gdf = gpd.read_file(shp_path)
                
                # Transform CRS to EPSG:4326 (WGS84)
                gdf = gdf.to_crs(epsg=4326)
                
                # Add required columns
                gdf["user_id"]               = user_id
                gdf["custom_id"]             = table_name
                gdf["name"]                  = table_name
                gdf["geoserver_workspace"]   = table_name
                gdf["geoserver_service"]     = "wms"
                gdf["geoserver_format"]      = "image/png"
                gdf["geoserver_transparent"] = "true"
                
                # Save to PostGIS
                gdf.to_postgis(
                    table_name,
                    engine,
                    schema      = schema_name,
                    index       = True,
                    index_label = "Index",
                    if_exists   = "replace"  # Options: fail, replace, append
                )
                
                # Also save as GeoJSON for compatibility
                if app.config.get('GEOJSON_FOLDER'):
                    # Get relative path to maintain directory structure
                    rel_path = os.path.relpath(root, app.config['UPLOAD_FOLDER'])
                    
                    # Create the same directory structure in output folder
                    if rel_path != '.':
                        output_dir = os.path.join(app.config['GEOJSON_FOLDER'], rel_path)
                        os.makedirs(output_dir, exist_ok=True)
                    else:
                        output_dir = app.config['GEOJSON_FOLDER']
                    
                    output_filename = f"{base_name}.geojson"
                    output_path     = os.path.join(output_dir, output_filename)
                    gdf.to_file(output_path, driver='GeoJSON')
                
                # Add table to processed list
                processed_tables.append(table_name)
                
                converted_count += 1
                flash(f"Successfully uploaded {table_name} to database", "success")
                
            except Exception as e:
                flash(f"Error processing {shp_file}: {str(e)}", "error")
    
    # Publish to GeoServer if any tables were processed
    if processed_tables:
        try:
            # Get GeoServer configuration for internal Docker communication
            # Use GEOSERVER_HOST and GEOSERVER_PORT for backend-to-backend calls
            # (GEOSERVER_PUBLIC_URL is for browser access only)
            geoserver_host = os.getenv("GEOSERVER_HOST", "http://geoportal-geoserver")
            geoserver_port = os.getenv("GEOSERVER_PORT", "8080")
            geoserver_url = f"{geoserver_host}:{geoserver_port}/geoserver"
            # Normalize: remove trailing slash
            if geoserver_url.endswith('/'):
                geoserver_url = geoserver_url[:-1]
            GEOSERVER_ADMIN_USER     = os.getenv("GEOSERVER_ADMIN_USER")
            GEOSERVER_ADMIN_PASSWORD = os.getenv("GEOSERVER_ADMIN_PASSWORD")
            
            # Initialize GeoServer connection
            geo = Geoserver(
                geoserver_url,
                username = GEOSERVER_ADMIN_USER,
                password = GEOSERVER_ADMIN_PASSWORD
            )
            
            # Publish each table to GeoServer
            for table_name in processed_tables:
                try:
                    # Create workspace (will catch and continue if already exists)
                    try:
                        geo.create_workspace(workspace=table_name)
                    except Exception as e:
                        if "409" in str(e):
                            print(f"Workspace {table_name} already exists. Continuing...")
                    
                    # Create feature store and publish
                    geo.create_featurestore(
                        store_name  = table_name,
                        workspace   = table_name,
                        db          = POSTGRES_DB_NAME,
                        host        = POSTGRES_DB_HOST,
                        port        = POSTGRES_DB_PORT,
                        schema      = schema_name,
                        pg_user     = POSTGRES_DB_USER,
                        pg_password = POSTGRES_DB_PASSWORD
                    )
                    
                    geo.publish_featurestore(
                        workspace  = table_name,
                        store_name = table_name,
                        pg_table   = table_name
                    )
                    
                    flash(f"Successfully published {table_name} to GeoServer", "success")
                except Exception as e:
                    flash(f"Error publishing {table_name} to GeoServer: {str(e)}", "warning")
                    # Continue with other tables even if one fails
        
        except Exception as e:
            flash(f"Error connecting to GeoServer: {str(e)}", "error")
    
    return converted_count