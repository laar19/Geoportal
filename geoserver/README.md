# GeoServer - Despliegue Manual (sin Docker)

Este directorio contiene scripts y documentación para el despliegue manual de GeoServer en entornos de producción/calidad donde no se usan contenedores Docker.

## 📋 Requisitos del Sistema

- **Sistema operativo:** Linux (Ubuntu 20.04+, CentOS 7+, RHEL 8+)
- **Java:** OpenJDK 17 o 21 (el script instala OpenJDK 17 automáticamente)
- **Memoria RAM:** Mínimo 4 GB (recomendado 8+ GB para producción)
- **Espacio disco:** 2 GB para instalación + espacio para datos
- **Privilegios:** Ejecución como `root` o con `sudo`

## 🚀 Despliegue Rápido

### Opción 1: Script Automático (Recomendado)

```bash
# Descargar script
cd /tmp
wget https://raw.githubusercontent.com/laar19/Geoportal/main/geoserver/deploy_geoserver.sh

# Hacer ejecutable y ejecutar
chmod +x deploy_geoserver.sh
sudo ./deploy_geoserver.sh
```

### Opción 2: Desde el Repositorio Clonado

```bash
# Si ya tienes el repositorio clonado
cd geoportal/geoserver
sudo ./deploy_geoserver.sh
```

## ⚙️ Configuración

### Variables de Entorno (Editar ANTES de ejecutar)

Crea un archivo `.env.geoserver` en el directorio actual o edita las variables directamente en el script:

```bash
# Puerto de GeoServer
GEOSERVER_PORT="8080"

# Directorio de datos
GEOSERVER_DATA_DIR="/var/lib/geoserver/data_dir"

# Contraseña administrador (CAMBIAR después del primer login)
GEOSERVER_ADMIN_PASSWORD="geoserver"

# PostgreSQL REMOTO (configurar con valores reales)
GEOSERVER_DB_HOST="postgres.remoto.com"
GEOSERVER_DB_PORT="5432"
GEOSERVER_DB_NAME="geoserver_db"
GEOSERVER_DB_USER="geoserver_user"
GEOSERVER_DB_PASSWORD="tu_password_seguro"

# Opciones Java (memoria)
JAVA_OPTS="-Xmx2G -Xms512M -XX:+UseG1GC"
```

### Ejecutar con Variables Personalizadas

```bash
# Exportar variables antes de ejecutar
export GEOSERVER_PORT="8888"
export GEOSERVER_DB_HOST="mi.postgres.remoto"
export GEOSERVER_DB_PASSWORD="password_real"
sudo ./deploy_geoserver.sh
```

## 📁 Estructura de Directorios Creada

El script crea la siguiente estructura:

```
/opt/geoserver/                    # Instalación principal
├── bin/                           # Scripts de inicio
├── lib/                           # Bibliotecas Java
├── webapps/geoserver/             # Aplicación web
├── start.sh                       # Script de inicio personalizado
└── start.jar                      # Jetty application server

/var/lib/geoserver/                # Datos persistentes
└── data_dir/                      # GeoServer data directory
    ├── workspaces/                # Workspaces configurados
    ├── styles/                    # Estilos SLD
    ├── data/                      # Datos raster/vectoriales
    └── logging.xml                # Configuración de logs

/var/log/geoserver/                # Logs de aplicación
└── geoserver.log                  # Log principal

/etc/geoserver/                    # Configuración del sistema
└── environment.conf               # Variables de entorno

/etc/systemd/system/               # Servicios systemd
└── geoserver.service              # Servicio para GeoServer
```

## 🔧 Comandos de Administración

### Servicio Systemd

```bash
# Estado del servicio
sudo systemctl status geoserver

# Iniciar/Detener/Reiniciar
sudo systemctl start geoserver
sudo systemctl stop geoserver
sudo systemctl restart geoserver

# Habilitar/Deshabilitar inicio automático
sudo systemctl enable geoserver
sudo systemctl disable geoserver

# Ver logs en tiempo real
sudo journalctl -u geoserver -f
```

### Logs y Monitoreo

```bash
# Logs principales
tail -f /var/log/geoserver/geoserver.log

# Logs de sistema (journalctl)
sudo journalctl -u geoserver --since "1 hour ago"

# Ver uso de memoria
ps aux | grep java | grep geoserver
```

### Configuración PostgreSQL

1. **Crear base de datos en PostgreSQL remoto:**
```sql
CREATE DATABASE geoserver_db;
CREATE USER geoserver_user WITH PASSWORD 'tu_password';
GRANT ALL PRIVILEGES ON DATABASE geoserver_db TO geoserver_user;
```

2. **Configurar en GeoServer:**
   - Acceder a `http://localhost:8080/geoserver`
   - Login: `admin` / `geoserver`
   - Ir a `Stores` → `Add new Store` → `PostGIS`
   - Configurar conexión con credenciales anteriores

## 🛠️ Solución de Problemas

### Problema: Servicio no inicia
```bash
# Ver logs detallados
sudo journalctl -u geoserver -xe

# Verificar Java
java -version

# Verificar puerto
sudo netstat -tlnp | grep :8080

# Verificar permisos
ls -la /var/lib/geoserver/
ls -la /var/log/geoserver/
```

### Problema: No se conecta a PostgreSQL
```bash
# Verificar conectividad
nc -zv postgres.remoto.com 5432

# Verificar driver JDBC
ls -la /opt/geoserver/webapps/geoserver/WEB-INF/lib/postgresql*.jar

# Probar conexión manual
psql -h postgres.remoto.com -U geoserver_user -d geoserver_db
```

### Problema: Memoria insuficiente
Editar `/etc/geoserver/environment.conf`:
```bash
# Aumentar memoria Java
JAVA_OPTS="-Xmx4G -Xms1G -XX:+UseG1GC"
```
Luego reiniciar: `sudo systemctl restart geoserver`

## 🔄 Actualización

### Actualizar GeoServer a nueva versión

1. **Detener servicio:**
```bash
sudo systemctl stop geoserver
```

2. **Backup data directory:**
```bash
cp -r /var/lib/geoserver/data_dir /var/lib/geoserver/data_dir_backup_$(date +%Y%m%d)
```

3. **Ejecutar script de nuevo** con nueva versión (editar `GEOSERVER_VERSION` en script)

4. **Restaurar configuración:**
```bash
cp -r /var/lib/geoserver/data_dir_backup_$(date +%Y%m%d)/* /var/lib/geoserver/data_dir/
```

5. **Iniciar servicio:**
```bash
sudo systemctl start geoserver
```

## 📊 Monitoreo y Mantenimiento

### Health Check
```bash
# Verificar que GeoServer responde
curl -s http://localhost:8080/geoserver/rest/about/status.json | jq .

# Verificar versión
curl -s http://localhost:8080/geoserver/rest/about/version.json | jq .
```

### Limpieza de Logs
```bash
# Rotar logs manualmente
sudo logrotate -f /etc/logrotate.d/geoserver  # Si configurado

# Limpiar logs antiguos
find /var/log/geoserver -name "*.log.*" -mtime +30 -delete
```

### Backup Automático (Cron)
Agregar a crontab (`crontab -e`):
```bash
# Backup diario a las 2 AM
0 2 * * * tar -czf /backup/geoserver_data_$(date +\%Y\%m\%d).tar.gz /var/lib/geoserver/data_dir
```

## 🔗 Integración con Aplicación Flask

La aplicación Flask del geoportal se conecta a GeoServer via:

```python
# Configuración en aplicación
GEOSERVER_URL = "http://localhost:8080/geoserver"
GEOSERVER_USER = "admin"
GEOSERVER_PASSWORD = "tu_password_cambiado"
```

Verificar conexión:
```bash
curl -u admin:password http://localhost:8080/geoserver/rest/workspaces.json
```

## 📝 Notas Importantes

1. **Seguridad:**
   - Cambiar contraseña `admin` después del primer login
   - Configurar HTTPS en producción
   - Restringir acceso por firewall
   - Usar PostgreSQL con SSL habilitado

2. **Rendimiento:**
   - Ajustar `JAVA_OPTS` según memoria disponible
   - Configurar cache en `GEOSERVER_DATA_DIR/gwc/`
   - Usar almacenamiento rápido para data directory

3. **Producción:**
   - Configurar monitoreo (Prometheus, Grafana)
   - Implementar backup automático
   - Configurar alta disponibilidad si es necesario

## 📞 Soporte

- **Documentación oficial:** https://docs.geoserver.org
- **Foros comunitarios:** https://geoserver.org/comm/
- **Issues del proyecto:** https://github.com/laar19/Geoportal/issues

---

**Última actualización:** $(date +%Y-%m-%d)  
**Versión GeoServer:** 2.28.2  
**Script version:** 1.0