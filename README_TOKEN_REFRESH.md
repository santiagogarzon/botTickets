# 🔄 Sistema de Renovación Automática de Tokens

Este sistema permite renovar automáticamente los tokens de autenticación de las aerolíneas sin intervención manual, manteniendo tu bot de búsqueda de vuelos funcionando sin interrupciones.

## 🚀 Características

- ✅ **Renovación automática**: Detecta tokens expirados y los renueva automáticamente
- ✅ **Integración transparente**: Se ejecuta automáticamente antes de cada búsqueda de vuelos
- ✅ **Múltiples aerolíneas**: Soporta Aerolíneas Argentinas y AirEuropa
- ✅ **Modo headless**: Ejecuta en segundo plano sin interfaz gráfica
- ✅ **Logging detallado**: Registra todo el proceso para debugging

## 📋 Requisitos

- Python 3.7+
- Google Chrome instalado
- Conexión a internet

## 🛠️ Instalación

### 1. Instalar dependencias

```bash
# Instalar todas las dependencias necesarias
python setup_token_refresh.py
```

O manualmente:

```bash
pip install -r requirements.txt
```

### 2. Verificar instalación

```bash
# Ejecutar tests completos
python test_token_refresh.py
```

## 📖 Uso

### Renovación Manual de Tokens

Si necesitas renovar los tokens manualmente:

```bash
# Renovación simple de todos los tokens
python simple_token_refresh.py

# Renovación inteligente (solo tokens expirados)
python smart_token_refresh.py
```

### Uso Automático

El sistema está integrado en el bot principal. Simplemente ejecuta:

```bash
python main.py
```

El bot automáticamente:

1. ✅ Verifica el estado de los tokens
2. ✅ Renueva tokens expirados si es necesario
3. ✅ Ejecuta las búsquedas de vuelos
4. ✅ Envía notificaciones de ofertas

## 🔧 Scripts Disponibles

| Script                     | Descripción                                         |
| -------------------------- | --------------------------------------------------- |
| `setup_token_refresh.py`   | Instala dependencias y configura ChromeDriver       |
| `simple_token_refresh.py`  | Renovación manual de todos los tokens               |
| `smart_token_refresh.py`   | Renovación inteligente (solo tokens expirados)      |
| `test_token_refresh.py`    | Tests completos del sistema                         |
| `check_ar_token.py`        | Verificar estado del token de Aerolíneas Argentinas |
| `check_aireuropa_token.py` | Verificar estado del token de AirEuropa             |

## 🧠 Cómo Funciona

### 1. Detección de Tokens Expirados

El sistema verifica automáticamente si los tokens actuales son válidos haciendo peticiones de prueba a las APIs de las aerolíneas.

### 2. Captura de Nuevos Tokens

Cuando detecta tokens expirados:

1. **Abre un navegador Chrome en modo headless**
2. **Navega a los sitios web de las aerolíneas**
3. **Interactúa con las páginas para generar peticiones API**
4. **Captura los nuevos tokens de los logs de red**
5. **Actualiza automáticamente el archivo `api_client.py`**

### 3. Integración Transparente

El sistema se ejecuta automáticamente antes de cada búsqueda de vuelos, asegurando que siempre tengas tokens válidos.

## 🔍 Troubleshooting

### Error: "ChromeDriver not found"

```bash
# Reinstalar ChromeDriver
python setup_token_refresh.py
```

### Error: "Selenium not installed"

```bash
# Instalar Selenium
pip install selenium webdriver-manager
```

### Error: "No tokens captured"

Esto puede ocurrir si:

- Los sitios web han cambiado su estructura
- Hay problemas de conectividad
- Los tokens se generan de forma diferente

**Solución**: Ejecuta manualmente los scripts de verificación:

```bash
python check_ar_token.py
python check_aireuropa_token.py
```

### Error: "Permission denied"

En sistemas Linux/macOS:

```bash
# Dar permisos de ejecución
chmod +x *.py
```

## 📊 Logs y Monitoreo

El sistema genera logs detallados que puedes revisar para debugging:

```
2024-01-15 10:30:00 - INFO - 🔍 Checking token status before flight search...
2024-01-15 10:30:01 - INFO - AR token valid: False
2024-01-15 10:30:01 - INFO - AirEuropa token valid: True
2024-01-15 10:30:01 - INFO - 🔄 Some tokens are expired, refreshing...
2024-01-15 10:30:05 - INFO - ✅ Captured fresh AR token: eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
2024-01-15 10:30:06 - INFO - ✅ AR token updated in api_client.py
2024-01-15 10:30:06 - INFO - ✅ Smart token refresh completed successfully!
```

## 🔒 Seguridad

- Los tokens se almacenan localmente en el archivo `api_client.py`
- No se envían a servidores externos
- El navegador se ejecuta en modo headless (sin interfaz visible)
- Los logs no contienen tokens completos por seguridad

## 🚀 Optimización

### Configuración de Chrome

El sistema usa estas opciones de Chrome para optimizar el rendimiento:

```python
chrome_options.add_argument("--headless")  # Sin interfaz gráfica
chrome_options.add_argument("--no-sandbox")  # Mejor rendimiento
chrome_options.add_argument("--disable-dev-shm-usage")  # Menos uso de memoria
chrome_options.add_argument("--disable-gpu")  # Sin aceleración GPU
```

### Frecuencia de Renovación

Los tokens se renuevan automáticamente:

- ✅ Antes de cada búsqueda de vuelos
- ✅ Solo si están expirados
- ✅ Sin interrumpir el funcionamiento normal del bot

## 📞 Soporte

Si encuentras problemas:

1. **Ejecuta los tests**: `python test_token_refresh.py`
2. **Revisa los logs** para identificar errores específicos
3. **Verifica la conectividad** a los sitios web de las aerolíneas
4. **Reinstala las dependencias**: `python setup_token_refresh.py`

## 🎯 Próximas Mejoras

- [ ] Soporte para más aerolíneas
- [ ] Renovación programada de tokens
- [ ] Notificaciones de renovación de tokens
- [ ] Backup automático de tokens válidos
- [ ] Interfaz web para monitoreo

---

**¡Disfruta de tu bot de vuelos sin preocuparte por los tokens!** 🛫
