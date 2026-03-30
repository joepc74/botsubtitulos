from pyrogram import Client, filters, types
from dotenv import load_dotenv
import gemini_srt_translator as gst
import os,subprocess
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

# 1. Manejador para recibir el video
@app.on_message(filters.video)
async def handle_video(client, message):
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

    # Aquí puedes guardar el idioma en una base de datos o procesar el archivo
    # print(f"El video del mensaje {msg_id} está en {seleccionado}, ruta del archivo: {file_path}")

    # Ejecutar whisper-ctranslate2 --output_format srt --output_dir {folder} --language {language} "{file_path}"
    # folder=os.path.dirname(file_path)
    # subprocess.run(["whisper-ctranslate2", "--output_format", "srt", "--output_dir", folder, "--language", language, file_path])
    # Añadir el codigo de idioma al nombre del archivo de subtitulos
    # base, ext = os.path.splitext(file_path)
    # subtitulo_path = f"{base}.{language}.srt"
    # os.rename(f"{base}.srt", subtitulo_path)

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
            try:
                # Traducción automática usando gemini_srt_translator
                translated_path = f"{base}.es.srt"
                gst.gemini_api_key = gemini_api_key
                gst.gemini_api_key2 = gemini_api_key2
                gst.target_language = "Spanish"
                gst.input_file = subtitulo_path
                gst.output_file= translated_path
                gst.translate()

                await callback_query.message.reply_document(translated_path, caption=f"Subtítulos traducidos al Español para el video.")
                os.remove(translated_path)
            except Exception as e:
                print(f"Error al traducir los subtítulos: {e}")
                await callback_query.message.reply_text("⚠️ No se pudieron traducir los subtítulos al Español.")
        os.remove(subtitulo_path)

app.run()
