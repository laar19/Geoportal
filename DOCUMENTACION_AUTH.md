# 📋 Documentación - Sistema de Autenticación Geoportal

## 🎯 Issues Implementados

### ✅ Issue #3: "añadir el botón de cerrar sesión"
- **Ubicación:** Sidebar (icono rojo de logout)
- **Visibilidad:** Solo cuando `ENABLE_KEYCLOAK_AUTH=true` y usuario está logueado
- **Acción:** Redirige a `/logout` endpoint

### ✅ Issue #4: "Cambiar el menú contextual una vez el usuario haya iniciado sesión y añadir el botón de cerrar sesión"
- **Plugin:** Leaflet.contextmenu (CDN)
- **Acceso:** Click derecho en el mapa
- **Opciones condicionales:**
  - **Siempre disponibles:** Medir distancia, Medir área, Obtener coordenadas, Cambiar capa base, Centrar mapa
  - **Solo con auth habilitado y NO logueado:** "Iniciar sesión"
  - **Solo con auth habilitado y SÍ logueado:** "Mi perfil", "Descargar datos", **"Cerrar sesión"**

### ✅ Issue #6: "Login keycloak" (Interfaz UI)
- **Variable control:** `ENABLE_KEYCLOAK_AUTH` en `.env`
- **Elementos UI en sidebar:**
  - Icono usuario (verde cuando logueado)
  - Botón "Iniciar sesión" 
  - Botón "Cerrar sesión" (rojo)
  - Indicador estado auth (dot verde/rojo)

## ⚙️ Configuración

### Variable de Control `ENABLE_KEYCLOAK_AUTH`
```bash
# En archivo .env
ENABLE_KEYCLOAK_AUTH=false  # Deshabilita auth (modo testing)
ENABLE_KEYCLOAK_AUTH=true   # Habilita auth (requiere Keycloak configurado)
```

### Archivo `.env.example` actualizado
```bash
# ... otras variables ...
ENABLE_KEYCLOAK_AUTH=True  # True: enforce login; False: bypass login_required
```

## 🔧 Arquitectura Técnica

### Frontend (`auth-ui.js`)
```javascript
class AuthUI {
  // Gestión estado auth frontend
  // Comunicación con backend via /api/auth/status
  // Actualización dinámica de UI
  // Sistema de notificaciones
}
```

### Menú Contextual (`context-menu.js`)
```javascript
class ContextMenuManager {
  // Configuración Leaflet.contextmenu
  // Opciones condicionales basadas en auth state
  // Eventos personalizados para comunicación
}
```

### Backend (`main.py`)
```python
@app.route('/api/auth/status')
def auth_status():
    # Retorna estado auth en JSON
    # Respeta ENABLE_KEYCLOAK_AUTH
    # Usa sesión Flask para determinar login
```

## 🚀 Uso y Pruebas

### Modo Testing Rápido (sin Keycloak)
1. Configurar `ENABLE_KEYCLOAK_AUTH=false` en `.env`
2. La aplicación NO requerirá autenticación
3. Los decoradores `@login_required` serán bypassed
4. Frontend mostrará estado "auth deshabilitado"

### Modo Producción (con Keycloak)
1. Configurar `ENABLE_KEYCLOAK_AUTH=true` en `.env`
2. Configurar variables Keycloak en `.env`
3. La aplicación requerirá autenticación
4. Rutas con `@login_required` estarán protegidas

### Pruebas Interactivas
1. **Abrir interfaz:** `http://localhost:8874/`
2. **Verificar sidebar:** Elementos auth visibles
3. **Menú contextual:** Click derecho en mapa
4. **Endpoint API:** `http://localhost:8874/api/auth/status`
5. **Debug controls:** Botones en esquina inferior derecha (solo localhost)

## 📁 Archivos Modificados/Creados

### Modificados
- `geoportal_app/templates/sidebar.html` - Elementos auth UI
- `geoportal_app/templates/index.html` - Scripts + elemento hidden auth
- `geoportal_app/main.py` - Endpoint `/api/auth/status` + variable template
- `geoportal_app/static/js/auth-ui.js` - Lógica frontend auth

### Creados
- `geoportal_app/static/js/context-menu.js` - Menú contextual Leaflet

## 🔍 Verificación de Implementación

### Checklist
- [x] Botón cerrar sesión visible en sidebar cuando logueado
- [x] Menú contextual muestra opciones condicionales
- [x] Botón cerrar sesión en menú contextual cuando logueado
- [x] Variable `ENABLE_KEYCLOAK_AUTH` controla visibilidad
- [x] Endpoint `/api/auth/status` retorna JSON correcto
- [x] Frontend actualiza dinámicamente según estado auth
- [x] Sistema funciona con auth habilitado/deshabilitado

### Comandos de Verificación
```bash
# Probar endpoint
curl http://localhost:8874/api/auth/status

# Verificar servicios
docker compose ps

# Ver logs aplicación
docker logs geoportal_app --tail 20

# Rebuildear cambios
docker compose build web && docker compose up -d web
```

## 🐛 Solución de Problemas

### Endpoint retorna 404
```bash
# Rebuildear y reiniciar
docker compose build web
docker compose restart web
```

### Error "ModuleNotFoundError: No module named 'geoportal_app'"
- Verificar importaciones en `main.py` (usar `from login_keycloak import` no `from geoportal_app.login_keycloak import`)

### Menú contextual no aparece
- Verificar que CDN de Leaflet.contextmenu esté cargado
- Verificar que `context-menu.js` esté incluido después de Leaflet

### Elementos auth no visibles
- Verificar valor de `ENABLE_KEYCLOAK_AUTH` en `.env`
- Verificar que `auth-ui.js` esté cargado
- Revisar consola JavaScript para errores

## 📊 Estado Actual
- **Commit:** `c8c137d` en rama `testing`
- **Push:** ✅ Realizado a GitHub
- **Servicios:** ✅ Todos corriendo
- **Endpoint:** ✅ Funcionando
- **Interfaz:** ✅ Implementada

## 🔮 Próximos Pasos
1. Configurar Keycloak real en máquina virtual
2. Probar flujo completo OAuth
3. Implementar roles y permisos
4. Mejorar UI de perfil de usuario