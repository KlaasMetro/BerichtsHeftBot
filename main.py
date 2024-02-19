from typing import Final
import requests
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from pydub import AudioSegment
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import logic

TOKEN: Final = '#Telegram Token here'
BOT_USERNAME: Final = '#Telegram Bot name'

#Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hi, lass uns mit deinem Berichtsheft anfangen!') 


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hi, schreibe etwas, damit ich antworten kann.') 


async def new_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Erstellen wir einen neuen Berichtsheft Eintrag!')
    context.user_data['message_text'] = update.message.text

    keyboard = [
        [KeyboardButton("Montag")],
        [KeyboardButton("Dienstag")],
        [KeyboardButton("Mittwoch")],
        [KeyboardButton("Donnerstag")],
        [KeyboardButton("Freitag")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    message = await update.message.reply_text('Wähle einen Tag für dein Bericht aus:', reply_markup = reply_markup)
    context.user_data['message_id'] = message.message_id


#Responses
    
def handle_response(text: str) -> str:
    processed: str = text.lower()
    if 'hallo' in processed:
        return 'Moin moin!'
    if 'montag' in processed:
        return 'Alles klar, nehme nun deine Audio auf um den Bericht für Montag zu erstellen.'
    if 'dienstag' in processed:
        return 'Alles klar, nehme nun deine Audio auf um den Bericht für Dienstag zu erstellen.'
    if 'mittwoch' in processed:
        return 'Alles klar, nehme nun deine Audio auf um den Bericht für Mittwoch zu erstellen.'
    if 'donnerstag' in processed:
        return 'Alles klar, nehme nun deine Audio auf um den Bericht für Donnerstag zu erstellen.'
    if 'freitag' in processed:
        return 'Alles klar, nehme nun deine Audio auf um den Bericht für Freitag zu erstellen.'
    return 'Damit kann ich nichts anfangen. schreibe /hilfe.'


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text


    print(f'User({update.message.chat.id}) in {message_type}: "{text}"')

    if 'Montag' in text or 'Dienstag' in text or 'Mittwoch' in text or 'Donnerstag' in text or 'Freitag' in text:
        context.user_data['selected_day'] = text

    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        response: str = handle_response(text)
    print('Bot:', response)
    await update.message.reply_text(response)


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')


async def save_voice_message(update: Update, context):
    voice_message = update.message.voice
    file_id = voice_message.file_id
    file = await context.bot.get_file(file_id)
    file_url = file.file_path
    file_content = requests.get(file_url).content
    ogg_filename = f'voice_message_{file_id}.ogg'

    with open(ogg_filename, 'wb') as f:
        f.write(file_content)

    wav_filename = f'voice_message_{file_id}.wav'
    audio = AudioSegment.from_ogg(ogg_filename)
    audio.export(wav_filename, format="wav")

    transcript_text = logic.transribe_audio_to_text(f'voice_message_{file_id}.wav')
    summarized_text = logic.summarize_transcripton(transcript_text)
    logic.write_text_in_File(summarized_text)
    logic.write_text_in_docx(summarized_text, context.user_data.get('selected_day') )
    await update.message.reply_text('Dein Bericht wurde erfolgreich eingefügt')





if __name__ == '__main__':
    print('starting bot...')
app = Application.builder().token(TOKEN).build()

#Commands
app.add_handler(CommandHandler('start', start_command))
app.add_handler(CommandHandler('hilfe', help_command))
app.add_handler(CommandHandler('neuer_eintrag', new_entry))


#Messages
app.add_handler(MessageHandler(filters.TEXT, handle_message))
app.add_handler(MessageHandler(filters.VOICE, save_voice_message))

#Errors
app.add_error_handler(error)

#Polls the bot
print('Polling...')
app.run_polling(poll_interval=3)