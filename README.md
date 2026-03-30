# Bot de Subtítulos para Videos 🎬

Un bot de Telegram que transcribe y traduce automáticamente los subtítulos de videos usando transcripción por IA y traducción con Google Gemini.

## Características ✨

- 📥 **Descarga de videos** desde Telegram (soporta hasta 2GB)
- 🎤 **Transcripción automática** del audio usando Faster Whisper
- 🌐 **Traducción multiidioma** con Google Gemini API
- 🗣️ **Detección automática de idioma** si no se especifica
- 💬 **Interfaz interactiva** con botones para seleccionar idioma
- 📝 **Generación de subtítulos** en formato SRT

## Idiomas Soportados 🌍

- Español 🇪🇸
- Inglés 🇺🇸
- Francés 🇫🇷
- Alemán 🇩🇪
- Italiano 🇮🇹
- Portugués 🇵🇹
- Detección automática ❓

## Requisitos 📋

- Python 3.8+
- Cuenta de bot en Telegram
- API ID y Hash de Telegram
- API Key de Google Gemini

## Instalación 🛠️

1. **Clonar o descargar el repositorio**
   ```bash
   git clone <repositorio>
   cd botsubtitulos
   ```

2. **Crear un entorno virtual**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # En Windows
   ```

3. **Instalar las dependencias**
   ```bash
   pip install -r requirements.txt
   ```

## Configuración ⚙️

Crear un archivo `.env` en la raíz del proyecto con las siguientes variables:

```env
api_id=YOUR_API_ID
api_hash=YOUR_API_HASH
client_session=YOUR_CLIENT_SESSION
bot_token=YOUR_BOT_TOKEN
gemini_api_key=YOUR_GEMINI_API_KEY
gemini_api_key2=YOUR_GEMINI_API_KEY_2
```

### Cómo obtener las credenciales:

- **API ID y Hash**: [my.telegram.org](https://my.telegram.org)
- **Bot Token**: Crear con [@BotFather](https://t.me/botfather) en Telegram
- **Gemini API Key**: [Google AI Studio](https://aistudio.google.com/)

## Uso 🚀

1. **Iniciar el bot**
   ```bash
   python botsubtitulos.py
   ```

2. **En Telegram**:
   - Envía un video al bot
   - Selecciona el idioma del audio del video
   - El bot procesará el video y generará los subtítulos
   - Recibirás el archivo SRT con los subtítulos traducidos

## Dependencias 📦

| Paquete | Versión | Descripción |
|---------|---------|-------------|
| Pyrogram | 2.0.106 | Cliente de Telegram para Python |
| faster_whisper | 1.2.1 | Transcripción de audio basada en Whisper |
| gemini_srt_translator | 3.0.1 | Traducción de subtítulos con Gemini |
| python-dotenv | 1.2.2 | Carga de variables de entorno |

## Flujo del Bot 🔄

1. ➡️ Usuario envía un video
2. ⏳ El bot descarga el video
3. 🎯 El bot muestra botones con opciones de idioma
4. 🗣️ Usuario selecciona el idioma del audio
5. 🎤 Se transcribe el audio usando Faster Whisper
6. 🌐 Se traducen los subtítulos con Gemini
7. 📤 Se envían los subtítulos al usuario

## Limitaciones ⚠️

- Tamaño máximo de video: 2GB
- Requiere conexión a Internet
- Depende de los límites de API de Google Gemini
- El procesamiento puede tardar según el tamaño del video

## Troubleshooting 🐛

- **Error de API**: Verifica que las claves en `.env` sean correctas
- **Video no se descarga**: Asegúrate de que el tamaño sea menor a 2GB
- **Errores de transcripción**: Verifica que el audio sea de calidad

## Licencia 📄

Este proyecto está disponible bajo licencia MIT.

## Autor ✏️

**Joe Colino** https://github.com/joepc74

---

**Última actualización**: Marzo 2026
