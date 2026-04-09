from pyrogram import Client, filters, types, idle
from dotenv import load_dotenv
import gemini_srt_translator as gst
import os,sys
from faster_whisper import WhisperModel

rutas={}

# Carga los valores del archivo .env
load_dotenv()
api_id = os.getenv('api_id')
api_hash = os.getenv('api_hash')
client_session = os.getenv('client_session')
bot_token = os.getenv('bot_token')
gemini_api_key = os.getenv('gemini_api_key')
gemini_api_key2 = os.getenv('gemini_api_key2')
valid_users = os.getenv('valid_users').split(",") if os.getenv('valid_users') else None
superuser=os.getenv('superuser')

app = Client("video_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

def format_timestamp(
    seconds: float, always_include_hours: bool = True, decimal_marker: str = ","
):
    assert seconds >= 0, "non-negative timestamp expected"
    milliseconds = round(seconds * 1000.0)

    hours = milliseconds // 3_600_000
    milliseconds -= hours * 3_600_000

    minutes = milliseconds // 60_000
    milliseconds -= minutes * 60_000

    seconds = milliseconds // 1_000
    milliseconds -= seconds * 1_000

    hours_marker = f"{hours:02d}:" if always_include_hours or hours > 0 else ""
    return (
        f"{hours_marker}{minutes:02d}:{seconds:02d}{decimal_marker}{milliseconds:03d}"
    )

async def traducir_srt(input_path, output_path, target_language="Spanish"):
    print(f"Traduciendo {input_path} a {output_path} en idioma {target_language}")
    try:
        # Traducción automática usando gemini_srt_translator
        gst.gemini_api_key = gemini_api_key
        gst.gemini_api_key2 = gemini_api_key2
        gst.target_language = target_language
        gst.input_file = input_path
        gst.output_file= output_path
        gst.translate()
    except (Exception,SystemExit) as e:
        print(f"Error al traducir el archivo SRT: {e}")
        if os.path.exists(output_path):
            os.remove(output_path)
    base_input_path, _ = os.path.splitext(input_path)
    if os.path.exists(f"{base_input_path}.progress"):
        os.remove(f"{base_input_path}.progress")

# Manejador de inicio
@app.on_message(filters.command("start"))
async def start(client, message):
    if valid_users and str(message.from_user.id) not in valid_users:
        await message.reply("❌ No tienes permiso para usar este bot.")
        return
    await message.reply(
        "👋 ¡Hola! Soy un bot que puede generar subtítulos para tus videos. Simplemente envíame un video y elige el idioma del audio para obtener los subtítulos en formato SRT."
    )

# Manejador de fin para parar el bot
@app.on_message(filters.command("stop"))
async def stop(client, message):
    if str(message.from_user.id) != superuser:
        await message.reply("❌ No tienes permiso para realizar esta acción.")
        return
    await message.reply("👋 ¡Adiós! El bot se ha detenido.")
    # Detiene el cliente de Pyrogram
    sys.exit(0)

# Manejador archivos srt para traducirlos al español
@app.on_message(filters.document)
async def handle_srt(client, message):
    if valid_users and str(message.from_user.id) not in valid_users:
        await message.reply("❌ No tienes permiso para usar este bot.")
        return
    file_name = message.document.file_name
    if not file_name.lower().endswith(".srt"):
        await message.reply("❌ Por favor, envía un archivo con formato .srt para traducirlo al español.")
        return

    status = await message.reply("⏳ Descargando archivo SRT...")

    # Descargar el archivo
    try:
        file_path = await message.download()
    except Exception as e:
        print(f"Error al descargar el archivo SRT: {e}")
        await status.edit("❌ Error al descargar el archivo SRT. Por favor, inténtalo de nuevo.")
        return
    await status.edit("✅ Archivo SRT descargado. Traduciendo al Español...")
    output_path = f"{os.path.splitext(file_path)[0]}.es.srt"
    await traducir_srt(file_path, output_path)
    if os.path.exists(output_path):
        await message.reply_document(output_path, caption="Archivo SRT traducido al Español.")
        os.remove(output_path)
    else:
        await status.edit("❌ Error al traducir el archivo SRT al Español.")
    if os.path.exists(file_path):
        os.remove(file_path)

# Manejador para recibir el video
@app.on_message(filters.video)
async def handle_video(client, message):
    if valid_users and str(message.from_user.id) not in valid_users:
        await message.reply("❌ No tienes permiso para usar este bot.")
        return
    status = await message.reply("⏳ Descargando video...")

    # Descargar el archivo (Pyrogram soporta hasta 2GB)
    try:
        file_path = await message.download()
        rutas[message.id] = file_path

    except Exception as e:
        print(f"Error al descargar el video: {e}")
        await status.edit("❌ Error al descargar el video. Por favor, inténtalo de nuevo.")
        return

    # 2. Crear botones de idioma
    keyboard = types.InlineKeyboardMarkup([
        [
            types.InlineKeyboardButton("Inglés 🇺🇸", callback_data=f"lang|en|{message.id}"),
            types.InlineKeyboardButton("Francés 🇫🇷", callback_data=f"lang|fr|{message.id}"),
            types.InlineKeyboardButton("Alemán 🇩🇪", callback_data=f"lang|de|{message.id}")
        ],
        [
            types.InlineKeyboardButton("Italiano 🇮🇹", callback_data=f"lang|it|{message.id}"),
            types.InlineKeyboardButton("Portugués 🇵🇹", callback_data=f"lang|pt|{message.id}"),
            types.InlineKeyboardButton("Español 🇪🇸", callback_data=f"lang|es|{message.id}")
        ],
        [types.InlineKeyboardButton("Otro / Desconocido ❓", callback_data=f"lang|other|{message.id}")]
    ])

    await status.edit(
        f"✅ Video guardado en: `{file_path}`\n\n**¿En qué idioma está el audio?**",
        reply_markup=keyboard
    )

# 3. Manejador para la respuesta del botón
@app.on_callback_query(filters.regex(r"^lang\|"))
async def language_selected(client, callback_query):
    # Extraer datos: lang | idioma | id_mensaje_original
    _, language, msg_id = callback_query.data.split("|")
    file_path = rutas.get(int(msg_id))
    idiomas = {"es": "Español", "en": "Inglés", "fr": "Francés", "de": "Alemán", "it": "Italiano", "pt": "Portugués", "other": "Otro"}
    seleccionado = idiomas.get(language)

    # Confirmar selección y quitar botones
    await callback_query.answer(f"Has elegido: {seleccionado}")
    await callback_query.edit_message_text(
        f"🎬 Procesando video...\n🌐 Idioma registrado: **{seleccionado}**"
    )

    # Transcribe con faster-whisper
    try:
        model = WhisperModel("small", device="cpu", compute_type="int8")

        if language == "other":
            segments, info = model.transcribe(file_path)
            language = info.language
        else:
            segments, info = model.transcribe(file_path, language=language)
        base, ext = os.path.splitext(file_path)
        subtitulo_path = f"{base}.{language}.srt"
    except Exception as e:
        print(f"Error al transcribir el video: {e}")
        await callback_query.edit_message_text("❌ Error al transcribir el video. Asegúrate de que el formato sea compatible y vuelve a intentarlo.")
        return

    try:
        with open(subtitulo_path, "w", encoding="utf-8") as srt:
            for i, segment in enumerate(segments):
                #print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
                srt.write(f"{i+1}\n{format_timestamp(segment.start)} --> {format_timestamp(segment.end)}\n{segment.text[1:]}\n\n")
                if (i%10==0):
                    porcentaje = segment.start / info.duration * 100
                    barra = '█' * int(porcentaje // 10) + '▒' * (10 - int(porcentaje // 10))
                    texto = f"Progreso: |{barra}| {porcentaje:.1f}%"
                    # bot.edit_message_text(chat_id=..., message_id=..., text=texto)
                    await callback_query.edit_message_text(texto)
    except Exception as e:
        print(f"Error al procesar el video: {e}")
        await callback_query.edit_message_text("❌ Error al procesar el video. Asegúrate de que el formato sea compatible y vuelve a intentarlo.")
        return

    # Borra el archivo original para ahorrar espacio
    os.remove(file_path)
    rutas.pop(int(msg_id), None)

    if not os.path.exists(subtitulo_path):
        await callback_query.edit_message_text(
            f"❌ Error al generar subtítulos para el idioma {seleccionado}."
        )
    else:
        await callback_query.edit_message_text('Transcripción completa. Enviando subtítulos...')
        await callback_query.message.reply_document(subtitulo_path, caption=f"Subtítulos en {seleccionado} para el video.")
        if (language != "es"):
            translated_path = f"{base}.{language}.srt"
            try:
                await callback_query.edit_message_text('Traduciendo subtítulos al Español...')
                await traducir_srt(subtitulo_path, translated_path)
                if os.path.exists(translated_path):
                    await callback_query.message.reply_document(translated_path, caption=f"Subtítulos traducidos al Español para el video.")
                else:
                    await callback_query.edit_message_text("❌ Error al traducir los subtítulos al Español.")
            except Exception as e:
                print(f"Error al traducir los subtítulos: {e}")
                await callback_query.edit_message_text("❌ Error al traducir los subtítulos al Español.")
                return

        if os.path.exists(translated_path):
            os.remove(translated_path)
        if os.path.exists(subtitulo_path):
            os.remove(subtitulo_path)

async def start_bot():
    await app.start()
    try:
        await app.send_message(chat_id=str(superuser), text="El bot de subtítulos ha iniciado correctamente.")
    except Exception as e:
        print(f"Error al enviar mensaje de inicio: {e}")
    await idle()
    # await app.stop()

app.run(start_bot())
