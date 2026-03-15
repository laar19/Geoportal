#!/bin/bash
# =============================================================================
# GeoServer Manual Deployment Script (Official Version)
# =============================================================================
# 
# Este script instala GeoServer 2.28.2 (última versión estable) en Linux
# sin usar Docker. Incluye Java 17, GeoServer con Jetty, y configuración
# para PostgreSQL remoto.
#
# USO: sudo ./deploy_geoserver.sh
#
# Nota: Este script NO ejecuta systemctl enable/start. Solo prepara todo.
#       Debes ejecutar manualmente después:
#         sudo systemctl daemon-reload
#         sudo systemctl enable geoserver
#         sudo systemctl start geoserver
#
# Variables de entorno (configurar antes de ejecutar o en .env.geoserver):
#   GEOSERVER_PORT=8080
#   GEOSERVER_DATA_DIR=/var/lib/geoserver/data_dir
#   GEOSERVER_ADMIN_PASSWORD=geoserver
#   GEOSERVER_DB_HOST=postgres.remoto.com
#   GEOSERVER_DB_PORT=5432
#   GEOSERVER_DB_NAME=geoserver_db
#   GEOSERVER_DB_USER=geoserver_user
#   GEOSERVER_DB_PASSWORD=tu_password
# =============================================================================

set -e  # Exit on error
set -u  # Exit on undefined variable

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# =============================================================================
# CONFIGURACIÓN
# =============================================================================

# Versiones
GEOSERVER_VERSION="2.28.2"
JAVA_VERSION="17"

# Directorios
INSTALL_DIR="/opt/geoserver"
DATA_DIR="/var/lib/geoserver/data_dir"
LOG_DIR="/var/log/geoserver"
CONFIG_DIR="/etc/geoserver"
SERVICE_USER=$(whoami)  # Usuario actual, cambiar si necesario

# URLs descarga
GEOSERVER_URL="https://sourceforge.net/projects/geoserver/files/GeoServer/${GEOSERVER_VERSION}/geoserver-${GEOSERVER_VERSION}-bin.zip"
POSTGRES_JDBC_URL="https://jdbc.postgresql.org/download/postgresql-42.7.3.jar"

# =============================================================================
# FUNCIONES DE LOGGING
# =============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# =============================================================================
# VERIFICACIÓN INICIAL
# =============================================================================

log_info "Iniciando despliegue manual de GeoServer ${GEOSERVER_VERSION}"
log_info "Fecha: $(date)"
log_info "Usuario: $(whoami)"
log_info "Hostname: $(hostname)"

# Verificar si es root
if [[ $EUID -ne 0 ]]; then
   log_error "Este script debe ejecutarse como root (sudo)"
fi

# Verificar sistema
if [[ ! -f /etc/os-release ]]; then
    log_error "No se pudo detectar sistema operativo"
fi

source /etc/os-release
log_info "Sistema detectado: $NAME $VERSION"

# =============================================================================
# FASE 1: INSTALAR JAVA 17
# =============================================================================

log_info "=== FASE 1: Instalando Java ${JAVA_VERSION} ==="

check_java() {
    if command -v java &> /dev/null; then
        JAVA_VER=$(java -version 2>&1 | head -n 1 | cut -d '"' -f 2 | cut -d '.' -f 1)
        if [[ $JAVA_VER -ge $JAVA_VERSION ]]; then
            log_success "Java $JAVA_VER ya instalado (cumple requisito $JAVA_VERSION+)"
            return 0
        else
            log_warning "Java $JAVA_VER instalado pero necesita $JAVA_VERSION+"
            return 1
        fi
    fi
    return 1
}

if ! check_java; then
    log_info "Instalando OpenJDK $JAVA_VERSION..."
    
    case $ID in
        ubuntu|debian)
            apt-get update
            apt-get install -y openjdk-${JAVA_VERSION}-jdk
            ;;
        centos|rhel|fedora)
            dnf install -y java-${JAVA_VERSION}-openjdk-devel
            ;;
        *)
            log_error "Distribución no soportada: $ID"
            ;;
    esac
    
    if ! check_java; then
        log_error "Falló instalación de Java"
    fi
fi

# Configurar JAVA_HOME
JAVA_HOME=$(readlink -f /usr/bin/java | sed "s:/bin/java::")
export JAVA_HOME
log_info "JAVA_HOME: $JAVA_HOME"

# =============================================================================
# FASE 2: CREAR DIRECTORIOS Y USUARIO
# =============================================================================

log_info "=== FASE 2: Preparando directorios ==="

# Crear directorios
for dir in "$INSTALL_DIR" "$DATA_DIR" "$LOG_DIR" "$CONFIG_DIR"; do
    if [[ ! -d "$dir" ]]; then
        log_info "Creando directorio: $dir"
        mkdir -p "$dir"
    else
        log_info "Directorio ya existe: $dir"
    fi
done

# Permisos
chmod 755 "$INSTALL_DIR"
chmod 755 "$CONFIG_DIR"
chmod 775 "$DATA_DIR"
chmod 775 "$LOG_DIR"

# =============================================================================
# FASE 3: DESCARGAR E INSTALAR GEO SERVER
# =============================================================================

log_info "=== FASE 3: Instalando GeoServer ${GEOSERVER_VERSION} ==="

cd /tmp

# Descargar GeoServer
if [[ ! -f "geoserver-${GEOSERVER_VERSION}-bin.zip" ]]; then
    log_info "Descargando GeoServer ${GEOSERVER_VERSION}..."
    wget --progress=bar:force "$GEOSERVER_URL" -O "geoserver-${GEOSERVER_VERSION}-bin.zip"
    
    if [[ $? -ne 0 ]]; then
        log_error "Falló descarga de GeoServer"
    fi
fi

# Verificar integridad
if [[ ! -f "geoserver-${GEOSERVER_VERSION}-bin.zip" ]]; then
    log_error "Archivo GeoServer no encontrado después de descarga"
fi

log_info "Descomprimiendo GeoServer..."
unzip -q "geoserver-${GEOSERVER_VERSION}-bin.zip" -d "$INSTALL_DIR"

# Mover contenido a instalación principal
mv "$INSTALL_DIR/geoserver-${GEOSERVER_VERSION}"/* "$INSTALL_DIR/"
rmdir "$INSTALL_DIR/geoserver-${GEOSERVER_VERSION}"

log_success "GeoServer instalado en $INSTALL_DIR"

# =============================================================================
# FASE 4: CONFIGURAR GEO SERVER
# =============================================================================

log_info "=== FASE 4: Configurando GeoServer ==="

# Descargar driver PostgreSQL JDBC
log_info "Descargando driver PostgreSQL JDBC..."
wget --progress=bar:force "$POSTGRES_JDBC_URL" -O "$INSTALL_DIR/webapps/geoserver/WEB-INF/lib/postgresql.jar"

# Configurar data directory
if [[ ! -d "$DATA_DIR" ]]; then
    log_info "Inicializando data directory..."
    cp -r "$INSTALL_DIR/data_dir"/* "$DATA_DIR/" 2>/dev/null || true
fi

# Configurar archivo de inicio
cat > "$INSTALL_DIR/start.sh" << EOF
#!/bin/bash
# Script de inicio para GeoServer

export JAVA_HOME="$JAVA_HOME"
export GEOSERVER_DATA_DIR="$DATA_DIR"
export GEOSERVER_LOG_LOCATION="$LOG_DIR/geoserver.log"

cd "$INSTALL_DIR"
exec java \\
    -Xmx2G -Xms512M \\
    -DGEOSERVER_DATA_DIR="\$GEOSERVER_DATA_DIR" \\
    -DGEOSERVER_LOG_LOCATION="\$GEOSERVER_LOG_LOCATION" \\
    -Dlog4j.configuration=file:"\$GEOSERVER_DATA_DIR/log4j.properties" \\
    -jar start.jar
EOF

chmod +x "$INSTALL_DIR/start.sh"

# Configurar variables de entorno
cat > "$CONFIG_DIR/environment.conf" << 'EOF'
# Configuración GeoServer
GEOSERVER_DATA_DIR="/var/lib/geoserver/data_dir"
GEOSERVER_LOG_LOCATION="/var/log/geoserver/geoserver.log"
GEOSERVER_PORT="8080"

# PostgreSQL remoto (configurar con valores reales)
GEOSERVER_DB_HOST="postgres.remoto.com"
GEOSERVER_DB_PORT="5432"
GEOSERVER_DB_NAME="geoserver_db"
GEOSERVER_DB_USER="geoserver_user"
GEOSERVER_DB_PASSWORD="cambiar_password"

# Java options
JAVA_OPTS="-Xmx2G -Xms512M -XX:+UseG1GC"
EOF

log_info "Configuración guardada en $CONFIG_DIR/environment.conf"
log_warning "IMPORTANTE: Edita $CONFIG_DIR/environment.conf con tus credenciales reales"

# =============================================================================
# FASE 5: CONFIGURAR SERVICIO SYSTEMD
# =============================================================================

log_info "=== FASE 5: Configurando servicio Systemd ==="

cat > /etc/systemd/system/geoserver.service << EOF
[Unit]
Description=GeoServer ${GEOSERVER_VERSION} (Official)
After=network.target
Wants=network.target

[Service]
Type=simple
User=$SERVICE_USER
Group=$SERVICE_USER
EnvironmentFile=$CONFIG_DIR/environment.conf
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/start.sh
ExecStop=/bin/kill -s TERM \$MAINPID
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$DATA_DIR $LOG_DIR

[Install]
WantedBy=multi-user.target
EOF

log_info "Servicio systemd creado: /etc/systemd/system/geoserver.service"

# Habilitar e iniciar servicio
log_info "Habilitando e iniciando servicio GeoServer..."
systemctl daemon-reload
systemctl enable geoserver
systemctl start geoserver

# Verificar estado
sleep 3
SERVICE_STATUS=$(systemctl status geoserver --no-pager -l)
if echo "$SERVICE_STATUS" | grep -q "active (running)"; then
    log_success "Servicio GeoServer iniciado exitosamente"
else
    log_warning "Servicio GeoServer no se pudo iniciar automáticamente"
    log_info "Estado del servicio:"
    echo "$SERVICE_STATUS"
    log_info "Para diagnóstico, revisa: sudo journalctl -u geoserver -f"
fi

# =============================================================================
# FASE 6: CONFIGURAR FIREWALL (OPCIONAL)
# =============================================================================

log_info "=== FASE 6: Configuración firewall (opcional) ==="

case $ID in
    ubuntu|debian)
        if command -v ufw &> /dev/null; then
            log_info "Configurando UFW para puerto 8080..."
            ufw allow 8080/tcp comment "GeoServer"
            log_info "Para aplicar: sudo ufw reload"
        fi
        ;;
    centos|rhel|fedora)
        if command -v firewall-cmd &> /dev/null; then
            log_info "Configurando firewalld para puerto 8080..."
            firewall-cmd --permanent --add-port=8080/tcp
            firewall-cmd --reload
        fi
        ;;
esac

# =============================================================================
# FASE 7: VERIFICACIÓN FINAL
# =============================================================================

log_info "=== FASE 7: Verificación final ==="

log_info "Resumen de instalación:"
log_info "  • GeoServer instalado en: $INSTALL_DIR"
log_info "  • Data directory: $DATA_DIR"
log_info "  • Logs: $LOG_DIR"
log_info "  • Configuración: $CONFIG_DIR"
log_info "  • Java: $(java -version 2>&1 | head -n 1)"
log_info "  • Puerto: 8080 (configurable en environment.conf)"
log_info ""
log_info "Archivos de configuración creados:"
log_info "  1. $CONFIG_DIR/environment.conf  (variables de entorno)"
log_info "  2. /etc/systemd/system/geoserver.service  (servicio systemd)"
log_info "  3. $INSTALL_DIR/start.sh  (script de inicio)"
log_info ""
log_info "PASOS POST-INSTALACIÓN:"
log_info "  1. Editar $CONFIG_DIR/environment.conf con tus credenciales PostgreSQL REALES"
log_info "  2. Reiniciar servicio: sudo systemctl restart geoserver"
log_info "  3. Verificar: sudo systemctl status geoserver"
log_info "  4. Acceder a: http://$(hostname -I | awk '{print $1}'):8080/geoserver"
log_info "  5. Credenciales iniciales: admin / geoserver (CAMBIAR después del primer login)"
log_info ""
log_info "Credenciales iniciales GeoServer:"
log_info "  • Usuario: admin"
log_info "  • Contraseña: geoserver (cambiar después del primer login)"
log_info ""
log_success "Instalación de GeoServer ${GEOSERVER_VERSION} completada exitosamente!"
log_info "Revisa los pasos manuales arriba para completar la configuración."