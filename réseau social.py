import os
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from yt_dlp import YoutubeDL
from yt_dlp.extractor import gen_extractor_classes

# 🔐 Token du bot Telegram
TOKEN = '6642551264:AAEfI-U29ppUrU5hlxLYqbxCWXRmDLDNdPA'

# 📂 Dossier temporaire pour les téléchargements
DOWNLOAD_DIR = 'downloads'
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# 🤖 Initialisation du bot
updater = Updater(TOKEN, use_context=True)
dispatcher = updater.dispatcher

# ✅ Fonction pour vérifier si une URL est supportée par yt-dlp
def is_supported_url(url):
    for extractor in gen_extractor_classes():
        if extractor.suitable(url) and extractor.IE_NAME != 'generic':
            return True
    return False

# 📥 Fonction pour télécharger une vidéo
def download_video(url):
    options = {
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
    }
    try:
        with YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=True)
            return ydl.prepare_filename(info)  # Retourne le chemin du fichier téléchargé
    except Exception as e:
        return str(e)

# 📤 Fonction pour envoyer une vidéo sur Telegram
def send_video_to_telegram(video_filename, chat_id, bot):
    file_size = os.path.getsize(video_filename)
    try:
        if file_size > 50 * 1024 * 1024:  # Si le fichier dépasse 50 Mo
            with open(video_filename, 'rb') as video_file:
                bot.send_document(chat_id, video_file, caption="Voici votre vidéo!")
        else:
            with open(video_filename, 'rb') as video_file:
                bot.send_video(chat_id, video_file, caption="Voici votre vidéo!")
    except Exception as e:
        bot.send_message(chat_id, f"❌ Erreur lors de l'envoi de la vidéo : {str(e)}")

# ⚙️ Commande /start
def start(update, context):
    update.message.reply_text("🎥 Envoyez-moi un lien direct vers une vidéo à télécharger!")

# ⚙️ Gestionnaire des messages avec des liens
def handle_message(update, context):
    url = update.message.text
    if is_supported_url(url):
        update.message.reply_text("🔗 Lien valide reçu. Téléchargement en cours...")
        video_filename = download_video(url)

        if os.path.exists(video_filename):
            update.message.reply_text("✅ Téléchargement terminé. Envoi en cours...")
            send_video_to_telegram(video_filename, update.message.chat.id, context.bot)
            os.remove(video_filename)  # Suppression du fichier après envoi
        else:
            update.message.reply_text(f"❌ Erreur lors du téléchargement : {video_filename}")
    else:
        update.message.reply_text("❌ URL non supportée. Veuillez fournir un lien direct vers une vidéo.")

# Configuration des gestionnaires
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

# 🚀 Lancement du bot
print("🤖 Bot démarré!")
updater.start_polling()
updater.idle()
