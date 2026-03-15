#!/bin/bash
# =============================================================================
# Geoportal Flask App - Manual Deployment Script
# =============================================================================
#
# Este script instala la aplicación Flask del geoportal en entorno Python puro
# usando pyenv + Python 3.10.12 + Gunicorn + Systemd, sin Docker.
#
# Sigue EXACTAMENTE el template proporcionado por el usuario:
# 1. Instala dependencias del sistema
# 2. Instala pyenv usando curl
# 3. Configura Python 3.10.12
# 4. Crea entorno virtual .venv
# 5. Instala dependencias Python
# 6. Configura variables de entorno
# 7. Configura Gunicorn + Systemd
#
# USO: sudo ./deploy_app.sh
#
# Variables de entorno (configurar antes de ejecutar o en .env.app):
#   POSTGRES_DB_HOST=postgres.remoto.com
#   POSTGRES_DB_PORT=5432
#   POSTGRES_DB_NAME=geoportal_db
#   POSTGRES_DB_USER=usuario
#   POSTGRES_DB_PASSWORD=password
#   GEOSERVER_HOST=http://localhost:8080
#   GEOSERVER_ADMIN_USER=admin
#   GEOSERVER_ADMIN_PASSWORD=geoserver
#   FLASK_HOST=0.0.0.0
#   WEB_HOST_PORT=8874
#   FLASK_DEBUG=false
#   GUNICORN_WORKERS=3
#   GUNICORN_TIMEOUT=120
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
PYTHON_VERSION="3.10.12"
APP_NAME="geoportal"
APP_USER=$(whoami)  # Usuario actual

# Directorios
APP_DIR="/opt/geoportal"
VENV_DIR="$APP_DIR/.venv"
LOG_DIR="/var/log/geoportal"
CONFIG_DIR="/etc/geoportal"
SERVICE_FILE="/etc/systemd/system/geoportal.service"

# Repositorio (ajustar si es diferente)
REPO_URL="https://github.com/laar19/Geoportal.git"
REPO_DIR="$APP_DIR/repo"

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

log_info "Iniciando despliegue manual de Geoportal Flask App"
log_info "Fecha: $(date)"
log_info "Usuario: $(whoami)"
log_info "Hostname: $(hostname)"
log_info "Python target: $PYTHON_VERSION"

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
# FASE 1: INSTALAR DEPENDENCIAS DEL SISTEMA (root)
# =============================================================================

log_info "=== FASE 1: Instalando dependencias del sistema ==="

case $ID in
    ubuntu|debian)
        log_info "Actualizando repositorios APT..."
        apt-get update
        
        log_info "Instalando dependencias de compilación y sistema..."
        apt-get install -y build-essential libssl-dev zlib1g-dev \
            libbz2-dev libreadline-dev libsqlite3-dev curl git \
            libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev \
            libffi-dev liblzma-dev python3-dev python3-venv python3-pip \
            nginx  # Para futura configuración con proxy
        ;;
    centos|rhel|fedora)
        log_info "Instalando dependencias en RHEL/CentOS..."
        dnf groupinstall -y "Development Tools"
        dnf install -y openssl-devel zlib-devel bzip2-devel \
            readline-devel sqlite-devel curl git ncurses-devel \
            xz-devel tk-devel libxml2-devel libxmlsec1-devel \
            libffi-devel xz-devel python3-devel python3-pip \
            nginx
        ;;
    *)
        log_error "Distribución no soportada: $ID"
        ;;
esac

log_success "Dependencias del sistema instaladas"

# =============================================================================
# FASE 2: INSTALAR PYENV (como usuario que ejecuta el script)
# =============================================================================

log_info "=== FASE 2: Instalando pyenv ==="

# Verificar si pyenv ya está instalado
if command -v pyenv &> /dev/null; then
    log_info "pyenv ya está instalado"
else
    log_info "Instalando pyenv usando el instalador automático..."
    
    # Instalar pyenv para el usuario actual (no global)
    curl https://pyenv.run | bash
    
    # Configurar variables de entorno para esta sesión
    export PYENV_ROOT="$HOME/.pyenv"
    export PATH="$PYENV_ROOT/bin:$PATH"
    
    # Inicializar pyenv para esta sesión
    eval "$(pyenv init -)"
    eval "$(pyenv virtualenv-init -)"
    
    # Configurar en shell para sesiones futuras
    cat >> ~/.bashrc << 'EOF'
# Pyenv configuration
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
EOF
    
    # Aplicar cambios inmediatamente
    source ~/.bashrc
    
    log_success "pyenv instalado y configurado"
fi

# Verificar instalación
if ! command -v pyenv &> /dev/null; then
    log_error "pyenv no se instaló correctamente"
fi

log_info "Versión pyenv: $(pyenv --version 2>/dev/null || echo 'No disponible')"

# =============================================================================
# FASE 3: INSTALAR PYTHON 3.10.12 CON PYENV
# =============================================================================

log_info "=== FASE 3: Instalando Python $PYTHON_VERSION ==="

# Verificar si Python ya está instalado
if pyenv versions | grep -q "$PYTHON_VERSION"; then
    log_info "Python $PYTHON_VERSION ya está instalado via pyenv"
else
    log_info "Instalando Python $PYTHON_VERSION (esto puede tomar varios minutos)..."
    
    # Instalar Python
    pyenv install "$PYTHON_VERSION"
    
    if [[ $? -ne 0 ]]; then
        log_error "Falló la instalación de Python $PYTHON_VERSION"
    fi
    
    log_success "Python $PYTHON_VERSION instalado"
fi

# Establecer versión global
log_info "Estableciendo Python $PYTHON_VERSION como versión global..."
pyenv global "$PYTHON_VERSION"

# Verificar
INSTALLED_PYTHON=$(python --version 2>&1)
log_info "Python activo: $INSTALLED_PYTHON"

# =============================================================================
# FASE 4: PREPARAR DIRECTORIOS DE LA APLICACIÓN
# =============================================================================

log_info "=== FASE 4: Preparando directorios de la aplicación ==="

# Crear directorios
for dir in "$APP_DIR" "$LOG_DIR" "$CONFIG_DIR"; do
    if [[ ! -d "$dir" ]]; then
        log_info "Creando directorio: $dir"
        mkdir -p "$dir"
        chown "$APP_USER:$APP_USER" "$dir"
    else
        log_info "Directorio ya existe: $dir"
    fi
done

# Permisos
chmod 755 "$APP_DIR"
chmod 755 "$CONFIG_DIR"
chmod 775 "$LOG_DIR"

# =============================================================================
# FASE 5: CLONAR/COPIAR CÓDIGO DE LA APLICACIÓN
# =============================================================================

log_info "=== FASE 5: Obteniendo código de la aplicación ==="

if [[ -d "$REPO_DIR" ]]; then
    log_info "Repositorio ya existe, actualizando..."
    cd "$REPO_DIR"
    git pull origin main
else
    log_info "Clonando repositorio desde $REPO_URL..."
    git clone "$REPO_URL" "$REPO_DIR"
fi

# Verificar que existe requirements.txt
if [[ ! -f "$REPO_DIR/requirements.txt" ]]; then
    log_error "No se encontró requirements.txt en $REPO_DIR"
fi

log_info "Código de la aplicación disponible en: $REPO_DIR"

# =============================================================================
# FASE 6: CREAR ENTORNO VIRTUAL E INSTALAR DEPENDENCIAS
# =============================================================================

log_info "=== FASE 6: Configurando entorno Python ==="

cd "$APP_DIR"

# Crear entorno virtual
if [[ ! -d "$VENV_DIR" ]]; then
    log_info "Creando entorno virtual en $VENV_DIR..."
    python -m venv "$VENV_DIR"
else
    log_info "Entorno virtual ya existe: $VENV_DIR"
fi

# Activar entorno virtual
source "$VENV_DIR/bin/activate"

# Actualizar pip
log_info "Actualizando pip..."
pip install --upgrade pip

# Instalar dependencias
log_info "Instalando dependencias desde requirements.txt..."
pip install -r "$REPO_DIR/requirements.txt"

# Gunicorn ya está en requirements.txt, se instalará automáticamente
log_info "Gunicorn se instalará desde requirements.txt"

log_success "Dependencias Python instaladas"

# =============================================================================
# FASE 7: CONFIGURAR VARIABLES DE ENTORNO
# =============================================================================

log_info "=== FASE 7: Configurando variables de entorno ==="

# Crear archivo de configuración
ENV_FILE="$CONFIG_DIR/environment.conf"
cat > "$ENV_FILE" << 'EOF'
# =============================================================================
# Geoportal Flask App - Environment Variables
# =============================================================================
# 
# CONFIGURAR CON VALORES REALES ANTES DE INICIAR LA APLICACIÓN
#

# PostgreSQL remoto (Base de datos principal)
POSTGRES_DB_HOST="postgres.remoto.com"
POSTGRES_DB_PORT="5432"
POSTGRES_DB_NAME="geoportal_db"
POSTGRES_DB_USER="usuario"
POSTGRES_DB_PASSWORD="password"

# GeoServer remoto
GEOSERVER_HOST="http://localhost:8080"
GEOSERVER_ADMIN_USER="admin"
GEOSERVER_ADMIN_PASSWORD="geoserver"

# Aplicación Flask
FLASK_APP="app:create_app()"
FLASK_ENV="production"
FLASK_DEBUG="false"
SECRET_KEY="cambiar-esta-clave-secreta-por-una-segura"
WEB_HOST="0.0.0.0"
WEB_HOST_PORT="8874"

# Gunicorn configuration
GUNICORN_WORKERS="3"
GUNICORN_TIMEOUT="120"
GUNICORN_BIND="0.0.0.0:8874"
GUNICORN_LOG_LEVEL="info"
GUNICORN_ACCESS_LOG="$LOG_DIR/access.log"
GUNICORN_ERROR_LOG="$LOG_DIR/error.log"

# Características GIS (no modificar a menos que sepas lo que haces)
GIS_ENABLED="true"
LEAFLET_VERSION="1.9.4"
CRS_DEFAULT="EPSG:4326"

# =============================================================================
# NO MODIFICAR LAS SIGUIENTES VARIABLES
# =============================================================================
APP_DIR="/opt/geoportal"
VENV_DIR="$APP_DIR/.venv"
REPO_DIR="$APP_DIR/repo"
EOF

log_info "Archivo de configuración creado: $ENV_FILE"
log_warning "IMPORTANTE: Edita $ENV_FILE con tus credenciales REALES antes de continuar"

# Crear archivo .env en directorio de la app (para compatibilidad)
APP_ENV_FILE="$REPO_DIR/.env"
cp "$ENV_FILE" "$APP_ENV_FILE"
log_info "Copia de configuración creada en: $APP_ENV_FILE"

# =============================================================================
# FASE 8: CONFIGURAR GUNICORN
# =============================================================================

log_info "=== FASE 8: Configurando Gunicorn ==="

# Crear script de inicio para Gunicorn
GUNICORN_START="$APP_DIR/start_gunicorn.sh"
cat > "$GUNICORN_START" << 'EOF'
#!/bin/bash
# Script de inicio para Geoportal con Gunicorn

# Cargar variables de entorno
if [ -f /etc/geoportal/environment.conf ]; then
    source /etc/geoportal/environment.conf
fi

# Activar entorno virtual
source /opt/geoportal/.venv/bin/activate

# Configurar variables para Flask
export FLASK_APP="$FLASK_APP"
export FLASK_ENV="$FLASK_ENV"
export SECRET_KEY="$SECRET_KEY"

# Navegar al directorio de la aplicación
cd /opt/geoportal/repo

# Ejecutar Gunicorn
exec gunicorn \
    --bind "$GUNICORN_BIND" \
    --workers "$GUNICORN_WORKERS" \
    --timeout "$GUNICORN_TIMEOUT" \
    --log-level "$GUNICORN_LOG_LEVEL" \
    --access-logfile "$GUNICORN_ACCESS_LOG" \
    --error-logfile "$GUNICORN_ERROR_LOG" \
    --preload \
    "app:create_app()"
EOF

chmod +x "$GUNICORN_START"
chown "$APP_USER:$APP_USER" "$GUNICORN_START"

log_info "Script Gunicorn creado: $GUNICORN_START"

# =============================================================================
# FASE 9: CONFIGURAR SERVICIO SYSTEMD
# =============================================================================

log_info "=== FASE 9: Configurando servicio Systemd ==="

cat > "$SERVICE_FILE" << EOF
[Unit]
Description=Geoportal Flask Application
After=network.target
Wants=network.target

[Service]
Type=simple
User=$APP_USER
Group=$APP_USER
EnvironmentFile=$CONFIG_DIR/environment.conf
WorkingDirectory=$REPO_DIR
ExecStart=$GUNICORN_START
ExecStop=/bin/kill -s TERM \$MAINPID
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

# Security hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$LOG_DIR $REPO_DIR

# Environment
Environment="PATH=$VENV_DIR/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
Environment="PYTHONPATH=$REPO_DIR"

[Install]
WantedBy=multi-user.target
EOF

log_info "Servicio systemd creado: $SERVICE_FILE"

# =============================================================================
# FASE 10: HABILITAR E INICIAR SERVICIO
# =============================================================================

log_info "=== FASE 10: Iniciando servicio ==="

# Recargar systemd
log_info "Recargando systemd..."
systemctl daemon-reload

# Habilitar servicio
log_info "Habilitando servicio geoportal..."
systemctl enable geoportal

# Iniciar servicio
log_info "Iniciando servicio geoportal..."
systemctl start geoportal

# Verificar estado
sleep 5
SERVICE_STATUS=$(systemctl status geoportal --no-pager -l)
if echo "$SERVICE_STATUS" | grep -q "active (running)"; then
    log_success "Servicio Geoportal iniciado exitosamente"
else
    log_warning "Servicio Geoportal no se pudo iniciar automáticamente"
    log_info "Estado del servicio:"
    echo "$SERVICE_STATUS"
    log_info "Para diagnóstico, revisa: sudo journalctl -u geoportal -f"
fi

# =============================================================================
# FASE 11: CONFIGURAR FIREWALL (OPCIONAL)
# =============================================================================

log_info "=== FASE 11: Configuración firewall (opcional) ==="

case $ID in
    ubuntu|debian)
        if command -v ufw &> /dev/null; then
            log_info "Configurando UFW para puerto 8874..."
            ufw allow 8874/tcp comment "Geoportal Flask App"
            log_info "Para aplicar: sudo ufw reload"
        fi
        ;;
    centos|rhel|fedora)
        if command -v firewall-cmd &> /dev/null; then
            log_info "Configurando firewalld para puerto 8874..."
            firewall-cmd --permanent --add-port=8874/tcp
            firewall-cmd --reload
        fi
        ;;
esac

# =============================================================================
# FASE 12: VERIFICACIÓN FINAL
# =============================================================================

log_info "=== FASE 12: Verificación final ==="

log_info "Resumen de instalación:"
log_info "  • Aplicación instalada en: $APP_DIR"
log_info "  • Entorno virtual: $VENV_DIR"
log_info "  • Código fuente: $REPO_DIR"
log_info "  • Logs: $LOG_DIR"
log_info "  • Configuración: $CONFIG_DIR"
log_info "  • Python: $(python --version 2>&1)"
log_info "  • Puerto: 8874 (configurable en $ENV_FILE)"
log_info ""
log_info "Archivos de configuración creados:"
log_info "  1. $ENV_FILE  (variables de entorno - EDITAR CON CREDENCIALES REALES)"
log_info "  2. $SERVICE_FILE  (servicio systemd)"
log_info "  3. $GUNICORN_START  (script de inicio Gunicorn)"
log_info ""
log_info "PASOS POST-INSTALACIÓN REQUERIDOS:"
log_info "  1. EDITAR $ENV_FILE con tus credenciales REALES de PostgreSQL y GeoServer"
log_info "  2. Copiar configuración a app: cp $ENV_FILE $APP_ENV_FILE"
log_info "  3. Si el servicio no inició: sudo systemctl restart geoportal"
log_info "  4. Verificar logs: sudo journalctl -u geoportal -f"
log_info "  5. Acceder a: http://$(hostname -I | awk '{print $1}'):8874"
log_info ""
log_info "Comandos de administración:"
log_info "  • Estado: sudo systemctl status geoportal"
log_info "  • Iniciar: sudo systemctl start geoportal"
log_info "  • Detener: sudo systemctl stop geoportal"
log_info "  • Reiniciar: sudo systemctl restart geoportal"
log_info "  • Logs: sudo journalctl -u geoportal -f"
log_info ""
log_info "Verificación de funcionamiento:"
log_info "  curl -s http://localhost:8874/health"
log_info "  curl -s http://localhost:8874/api/status"
log_info ""
log_success "Instalación de Geoportal Flask App completada exitosamente!"
log_info "Recuerda EDITAR las credenciales en $ENV_FILE antes de usar la aplicación."
