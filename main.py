from flask import Flask

from folium import plugins
import folium

from draw import Draw

app = Flask(__name__)

@app.route('/')
def index():    
    start_coords = (10.469, -66.80)
    folium_map = folium.Map(
        location=start_coords,
        zoom_start=12, control_scale=True, position='relative'
    )

    minimap = plugins.MiniMap(toggle_display=True) # Define minimap
    folium_map.add_child(minimap)                  # Add minimap
    plugins.ScrollZoomToggler().add_to(folium_map) # Add zoom scroll
    plugins.Fullscreen(position='topright').add_to(folium_map) # Add fullscreen buttons

    Draw(
        export=True,
        filename='my_data.geojson',
        position='topleft',
        draw_options={'polyline': {'allowIntersection': False}},
        edit_options={'poly': {'allowIntersection': False}}
    ).add_to(folium_map)

    return folium_map._repr_html_()

if __name__ == '__main__':
    app.run(debug=True)
