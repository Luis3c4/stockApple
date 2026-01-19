# 📱 Configuración de Telegram Bot

Este documento explica cómo configurar las notificaciones de Telegram para el Apple Stock Bot.

## 🚀 Guía Rápida

### 1. Crear el Bot de Telegram

1. Abre Telegram y busca [@BotFather](https://t.me/BotFather)
2. Envía el comando: `/newbot`
3. Sigue las instrucciones:
   - Dale un nombre a tu bot (ej: "Apple Stock Notifier")
   - Dale un username (debe terminar en "bot", ej: "apple_stock_bot")
4. BotFather te dará un **Token** como este:
   ```
   123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   ```
5. ⚠️ **Guarda este token de forma segura**

### 2. Obtener tu Chat ID

Opción A - Método Manual:
1. Envía cualquier mensaje a tu bot (ej: "Hola")
2. Abre en tu navegador:
   ```
   https://api.telegram.org/bot<TU_TOKEN>/getUpdates
   ```
   Reemplaza `<TU_TOKEN>` con el token que te dio BotFather
3. Busca en el JSON el campo `"chat":{"id":123456789}`
4. Ese número es tu Chat ID

Opción B - Usando @userinfobot:
1. Busca [@userinfobot](https://t.me/userinfobot) en Telegram
2. Envíale `/start`
3. Te mostrará tu Chat ID directamente

### 3. Configurar el Archivo .env

1. Copia `.env.example` a `.env`:
   ```powershell
   copy .env.example .env
   ```

2. Edita `.env` y agrega tus credenciales:
   ```env
   TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   TELEGRAM_CHAT_ID=123456789
   TELEGRAM_ENABLED=true
   ```

### 4. Probar la Conexión

Ejecuta el test de Telegram:
```powershell
python main.py --test-telegram
```

Si todo está bien, recibirás un mensaje de prueba en Telegram.

## 📋 Comandos Útiles

```powershell
# Probar solo Telegram
python main.py --test-telegram

# Probar Apple Store y Telegram
python main.py --test

# Ejecutar scraper con notificaciones
python main.py

# Ejecutar sin notificaciones (temporal)
# En .env: TELEGRAM_ENABLED=false
python main.py
```

## 🎨 Formato de Mensajes

El bot enviará mensajes formateados en HTML con:

### ✅ Cuando hay stock disponible:
```
🎉 ¡STOCK DISPONIBLE!
📱 iPhone 17 Pro Max
🏪 6.9" | 2TB | Deep Blue | Unlocked

✅ TIENDAS CON STOCK (3):

✅ Wellington Green
   📍 Wellington, FL
   ⏰ Available Today

✅ Aventura
   📍 Aventura, FL
   ⏰ Available Today
...
```

### ❌ Cuando NO hay stock:
```
⚠️ Sin Stock Disponible
📱 iPhone 17 Pro Max

❌ SIN STOCK (15):
❌ Wellington Green (Wellington) - Currently Unavailable
❌ Aventura (Aventura) - Currently Unavailable
...
```

### ❌ En caso de error:
```
❌ ERROR EN SCRAPING

Error:
Timeout navegando Apple Store: ...
```

## 🔧 Solución de Problemas

### Error: "Token o Chat ID no configurados"
- Verifica que `.env` existe y tiene las variables correctas
- Asegúrate de no dejar espacios en blanco
- El token debe ser exactamente como lo dio BotFather

### Error: "Unauthorized"
- El token es incorrecto
- Crea un nuevo bot con BotFather

### Error: "Chat not found"
- El Chat ID es incorrecto
- Asegúrate de haber enviado al menos un mensaje al bot primero
- Verifica que el Chat ID sea un número, sin comillas

### No recibo mensajes
- Verifica que `TELEGRAM_ENABLED=true` en `.env`
- Asegúrate de haber iniciado conversación con el bot (envía /start)
- Verifica con `python main.py --test-telegram`

## 🔐 Seguridad

⚠️ **IMPORTANTE**: 
- **NO** compartas tu Token de Telegram
- **NO** subas el archivo `.env` a repositorios públicos
- El `.gitignore` ya está configurado para ignorar `.env`

## 📚 Más Información

- [Telegram Bot API](https://core.telegram.org/bots/api)
- [BotFather Commands](https://core.telegram.org/bots#botfather)
- [Formatting Options](https://core.telegram.org/bots/api#html-style)
