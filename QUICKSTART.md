# 🚀 Inicio Rápido - Apple Store Scraper

## ⚡ Instalación (solo primera vez)

```bash
# 1. Crear entorno virtual
python -m venv .venv

# 2. Activar entorno virtual
.venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt
playwright install chromium

# 4. Configurar (opcional - tiene defaults)
# Edita .env si quieres cambiar producto o estado
```

## 🎯 Uso diario

### Opción 1: Script de ayuda (recomendado)

```bash
# Ver navegador (recomendado para desarrollo)
.\run.ps1 visible

# Modo headless (rápido)
.\run.ps1 scrape

# Probar conexión
.\run.ps1 test

# Ver ayuda completa
.\run.ps1 help
```

### Opción 2: Python directo

```bash
# Activar entorno
.venv\Scripts\activate

# Ejecutar con navegador visible (desarrollo)
python main.py --headless=false

# Ejecutar modo headless (producción)
python main.py

# Guardar resultados en JSON
python main.py --save-json

# Probar conexión
python main.py --test
```

## ⚙️ Configuración

Edita `.env` para cambiar:

```env
# Producto a buscar
TARGET_PRODUCT=iPhone 17

# Estado/región
TARGET_STATE=Florida

# Ver navegador (true/false)
PLAYWRIGHT_HEADLESS=false
```

## 🔧 Actualizar selectores CSS

⚠️ **IMPORTANTE**: Apple cambia su sitio frecuentemente

1. Ejecuta: `.\run.ps1 visible`
2. Observa qué elementos busca
3. Inspecciona con F12 en el navegador
4. Actualiza selectores en `services/apple_scraper.py`
5. Busca el método `_extract_availability_data()`

## 📸 Debugging

- **Logs**: `logs/apple_bot_YYYYMMDD.log`
- **Screenshots**: `screenshots/`
- **Navegador visible**: `.\run.ps1 visible`

## 💡 Tips

- Usa `visible` durante desarrollo para ver qué pasa
- Revisa screenshots si algo falla
- Los logs tienen información detallada
- Actualiza selectores CSS según estructura actual de Apple

## 📚 Más información

Ver [README.md](README.md) para documentación completa.
