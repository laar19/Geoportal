<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">

    <!-- CDN -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/openlayers/openlayers.github.io@master/en/v6.4.3/css/ol.css" type="text/css">
    <script src="https://cdn.jsdelivr.net/gh/openlayers/openlayers.github.io@master/en/v6.4.3/build/ol.js"></script>

    <!-- local -->
    <link rel="stylesheet" type="text/css" href="assets/css/main.css">

    <title>Geo Abae</title>
</head>
<body>
    <div class="super">
        <div id="map" class="map"></div>

        <div class="search-bar">
            <table>
                <tr>
                    <td><a>logo</a></td>
                    <td><input type="search" name="" value=""></td>
                    <td><button type="button" name="button">Buscar</button></td>
                </tr>
            </table>
        </div>

        <div class="left-controls">
            <div class="tools-1">
                <table>
                    <tr>
                        <td><a>tools1</a></td>
                    </tr>
                </table>
            </div>

            <div class="tools-2">
                <table>
                    <tr>
                        <td><a>tools2</a></td>
                    </tr>
                </table>
            </div>

            <div class="tools-3">
                <table>
                    <tr>
                        <td><a>tools3</a></td>
                    </tr>
                </table>
            </div>
        </div>

        <div class="right-controls">
            <a>CONTROLES Y OPCIONES</a>

            <div class="show">
                <label for="show_shp"><a>SHOW</a></label>
                <input type="checkbox" name="show_shp" id="show_shp">
            </div>

            <div class="mouse_control">
                <form>
                    <label><a>Projection</a></label>
                    <select id="projection">
                        <option value="EPSG:4326">EPSG:4326</option>
                        <option value="EPSG:3857">EPSG:3857</option>
                    </select>
                    <label><a>Precision</a></label>
                    <input id="precision" type="number" min="0" max="12" value="4"/>
                </form>

                <div id="mouse-position"><a></a></div>

                <div class="draw_and_modify_features">
                    <label for="enable_draw"><a>Enable</a></label>
                    <input type="checkbox" name="enable_draw" id="enable_draw">
                    <form class="form-inline">
                        <label><a>Geometry type</a> &nbsp;</label>
                        <select id="type">
                            <option value="Point">Point</option>
                            <option value="LineString">LineString</option>
                            <option value="Polygon">Polygon</option>
                            <option value="Circle">Circle</option>
                        </select>
                    </form>
                </div>
            </div>
        </div>
    </div>

    <script type="text/javascript" src="assets/js/main.js"></script>
    <script type="text/javascript" src="assets/js/map.js"></script>
    <script type="text/javascript" src="assets/js/controls/mouse_position_control.js"></script>
    <script type="text/javascript" src="assets/js/controls/draw_and_modify_features.js"></script>
    <script type="text/javascript" src="assets/js/wms/load_shp.js"></script>
</body>
</html>
