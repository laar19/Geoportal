<?php
    include("conexion.php");

    $sql = "SELECT nombre, region, latitud, longitud FROM torres";
        
    $result = mysqli_query($conn, $sql);
        
    $coordenadas = array();
    while($row = mysqli_fetch_array($result)){
        array_push($coordenadas, array("nombre" => $row["nombre"],
                                    "region"    => $row["region"],
                                    "latitud"   => $row["latitud"],
                                    "longitud"  => $row["longitud"]));
    }

    $conn->close();
?>