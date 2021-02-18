<html>
    <head>
        <meta charset="utf-8">
        <title></title>

        <link rel="stylesheet" type="text/css" href="css/main.css">
        
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.6.0/dist/leaflet.css"/>
        
        <script src="https://unpkg.com/leaflet@1.6.0/dist/leaflet.js"></script>
    </head>
  
    <body>
        <?php include("php/consulta.php"); ?>
        <div id="mapa" class="mapa"></div>
    </body>

    <script> var coordenadas = <?php echo json_encode($coordenadas); ?>; </script>
    <script type="text/javascript" src="js/mapa.js"></script>
</html>
