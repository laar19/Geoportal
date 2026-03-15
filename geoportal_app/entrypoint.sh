#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║           🌍 GEOPORTAL WEB APP - STARTING                 ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Print configuration
echo -e "${YELLOW}📋 Configuration:${NC}"
echo -e "   Database Host:     ${POSTGRES_DB_HOST:-not set}"
echo -e "   Database Port:     ${POSTGRES_DB_PORT:-not set}"
echo -e "   Database Name:     ${POSTGRES_DB_NAME:-not set}"
echo -e "   Database User:     ${POSTGRES_DB_USER:-not set}"
echo -e "   Geoserver Host:    ${GEOSERVER_HOST:-not set}"
echo -e "   Geoserver Port:    ${GEOSERVER_PORT:-not set}"
echo -e "   Web App Port:      ${WEB_CONTAINER_PORT:-not set}"
echo -e "   Keycloak Auth:     ${ENABLE_KEYCLOAK_AUTH:-not set}"
echo ""

# Function to check PostgreSQL connection
check_postgres() {
    echo -e "${YELLOW}🔍 Checking PostgreSQL connection...${NC}"
    
    # Try to connect using pg_isready or python
    python3 << EOF
import sys
import psycopg2
import os

host = os.getenv('POSTGRES_DB_HOST', 'localhost')
port = os.getenv('POSTGRES_DB_PORT', '5432')
dbname = os.getenv('POSTGRES_DB_NAME', 'geoportal_db')
user = os.getenv('POSTGRES_DB_USER', 'root')
password = os.getenv('POSTGRES_DB_PASSWORD', 'root')

try:
    conn = psycopg2.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password,
        connect_timeout=10
    )
    conn.close()
    print(f"   ✅ PostgreSQL connection successful: {host}:{port}/{dbname}")
    sys.exit(0)
except psycopg2.OperationalError as e:
    print(f"   ❌ PostgreSQL connection FAILED: {host}:{port}/{dbname}")
    print(f"   Error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"   ❌ PostgreSQL connection FAILED: {str(e)}")
    sys.exit(1)
EOF
}

# Function to check Geoserver connection
check_geoserver() {
    echo -e "${YELLOW}🔍 Checking Geoserver connection...${NC}"
    
    python3 << EOF
import sys
import urllib.request
import urllib.error
import os
import ssl

host = os.getenv('GEOSERVER_HOST', 'http://localhost')
port = os.getenv('GEOSERVER_PORT', '8080')
url = f"{host}:{port}/geoserver/web/"

try:
    # Create unverified context for self-signed certs
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    req = urllib.request.Request(url, method='HEAD')
    response = urllib.request.urlopen(req, timeout=10, context=ctx)
    print(f"   ✅ Geoserver connection successful: {url}")
    sys.exit(0)
except urllib.error.URLError as e:
    print(f"   ⚠️  Geoserver not responding yet: {url}")
    print(f"   Reason: {e.reason}")
    print(f"   (This is normal during startup, Geoserver takes time to initialize)")
    sys.exit(0)  # Don't fail, geoserver takes time
except Exception as e:
    print(f"   ⚠️  Geoserver check skipped: {str(e)}")
    sys.exit(0)
EOF
}

# Check connections
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
check_postgres
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ FATAL: Cannot connect to PostgreSQL database!${NC}"
    echo -e "${RED}   Please ensure the database container is running and healthy.${NC}"
    echo -e "${RED}   Check: docker compose ps${NC}"
    exit 1
fi

check_geoserver
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Run database setup
echo -e "${YELLOW}⏳ Running database setup (setup_db.py)...${NC}"
if python setup_db.py; then
    echo -e "${GREEN}   ✅ Database setup completed successfully${NC}"
else
    echo -e "${RED}   ❌ Database setup failed!${NC}"
    exit 1
fi
echo ""

# Final startup message
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║           ✅ GEOPORTAL WEB APP - RUNNING                  ║${NC}"
echo -e "${GREEN}╠═══════════════════════════════════════════════════════════╣${NC}"
echo -e "${GREEN}║  🌐 Access at: http://localhost:${WEB_HOST_PORT:-8874}                       ║${NC}"
echo -e "${GREEN}║  🗺️  Geoserver: http://localhost:8870/geoserver           ║${NC}"
echo -e "${GREEN}║  📊 pgAdmin:   http://localhost:8872                      ║${NC}"
echo -e "${GREEN}║  📋 Adminer:   http://localhost:8873                      ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📝 Logs will appear below...${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Start the Flask application with Gunicorn
echo -e "${YELLOW}🚀 Starting Gunicorn server with ${workers:-auto} workers...${NC}"
echo -e "${YELLOW}   Config: gunicorn.conf.py${NC}"
echo -e "${YELLOW}   App: main:app${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Calculate workers if not set
if [ -z "$GUNICORN_WORKERS" ]; then
    CPU_COUNT=$(nproc 2>/dev/null || echo 1)
    GUNICORN_WORKERS=$((CPU_COUNT * 2 + 1))
    echo -e "${BLUE}📊 Auto-detected $CPU_COUNT CPU cores, using $GUNICORN_WORKERS workers${NC}"
fi

export GUNICORN_WORKERS

# Start Gunicorn
exec gunicorn --config gunicorn.conf.py main:app
