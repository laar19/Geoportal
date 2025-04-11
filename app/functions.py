import os

import geopandas as gpd

from flask import flash

def process_uploaded_shapefiles(app, user_id):
    """Process all shapefiles in the uploads folder, preserving directory structure"""
    converted_count = 0
    
    # Walk through all directories in upload folder
    for root, _, files in os.walk(app.config['UPLOAD_FOLDER']):
        # Get shp files in this directory
        shp_files = [f for f in files if f.endswith('.shp')]
        
        if not shp_files:
            continue
            
        # Get relative path to maintain directory structure
        rel_path = os.path.relpath(root, app.config['UPLOAD_FOLDER'])
        
        # Create the same directory structure in output folder
        if rel_path != '.':
            output_dir = os.path.join(app.config['GEOJSON_FOLDER'], rel_path)
            os.makedirs(output_dir, exist_ok=True)
        else:
            output_dir = app.config['GEOJSON_FOLDER']
        
        # Convert each shapefile in this directory
        for shp_file in shp_files:
            try:
                # Full path to the shapefile
                shp_path = os.path.join(root, shp_file)
                
                # Read the shapefile using geopandas
                gdf = gpd.read_file(shp_path)
                
                # Add a new column called "test" with value "test" to the GeoDataFrame
                gdf["user_id"] = user_id
                
                # Get base name without extension for output filename
                base_name = os.path.splitext(shp_file)[0]
                output_filename = f"{base_name}.geojson"
                output_path = os.path.join(output_dir, output_filename)
                
                # Save as GeoJSON
                gdf.to_file(output_path, driver='GeoJSON')
                converted_count += 1
                
            except Exception as e:
                flash(f"Error converting {shp_file}: {str(e)}")
                
    return converted_count