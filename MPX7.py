from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)
import logging
from typing import Dict, Set

# -------------------- CONFIGURATION --------------------
TOKEN = "7520847694:AAGXLKTvD0dHU2nyaGmCuN0DovelGHHr5Pg"
ADMIN_IDS = {"5524867269", "6213264970"}
banned_users: Set[str] = set()
user_lang: Dict[str, str] = {}
forward_map: Dict[int, int] = {}

# -------------------- LOGGER --------------------
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# -------------------- LANGUAGES --------------------
LANGUAGES = {
    "hindi": {
        "welcome": "🇮🇳 नमस्ते! अब आप फीडबैक भेज सकते हैं। 😊",
        "full_welcome": (
            "🚀 SkullCheat Feedback Bot में आपका स्वागत है!\n\n"
            "📢 चैनल: @Skull_Cheats\n"
            "👤 डेवलपर: @SkullModOwner\n"
            "📤 स्क्रीनशॉट भेजें: @SkullCheat_FileBot\n\n"
            "⚠️ ध्यान दें: बिना फीडबैक के कोई Key नहीं मिलेगी! 🔑"
        ),
        "user": "👤 यूजर डैशबोर्ड\n\n🆔 ID: {user_id}\n🌐 भाषा: {lang}\n🚫 बैन: {banned}\n👥 कुल यूजर: {total}",
        "banned": "🚫 आप प्रतिबंधित हैं। कोई क्रिया नहीं।",
        "language_set": "✅ भाषा सेट हो गई है!\n\n{message}",
        "unauthorized": "❌ आप अधिकृत नहीं हैं।",
        "ban_success": "🚫 यूजर {user_id} को बैन किया गया।",
        "unban_success": "✅ यूजर {user_id} का बैन हटाया गया।",
        "broadcast_result": "📢 संदेश {count} यूजर्स को भेजा गया, {failed} असफल रहे।",
        "admin_reply_prefix": "💬 एडमिन का जवाब:\n\n",
        "reply_success": "✅ संदेश सफलतापूर्वक भेजा गया!",
        "reply_failed": "❌ संदेश भेजने में विफल।",
        "invalid_format": "⚠️ फॉर्मेट सपोर्ट नहीं है।",
        "user_not_found": "⚠️ मूल यूजर नहीं मिला।",
        "reply_instructions": "❌ कृपया यूजर के संदेश पर रिप्लाई करें।",
        "commands": (
            "📚 उपलब्ध कमांड्स:\n\n"
            "🚀 /start - बोट शुरू करें\n"
            "👤 /user - अपनी जानकारी देखें\n"
            "🌐 /language - भाषा बदलें\n"
            "📝 /feedback - फीडबैक भेजें\n"
            "❓ /help - मदद देखें\n\n"
            "🔨 एडमिन कमांड्स:\n"
            "🚫 /ban <user_id> - यूजर को बैन करें\n"
            "✅ /unban <user_id> - यूजर का बैन हटाएं\n"
            "📢 /broadcast - सभी को संदेश भेजें\n"
            "📜 /commands - सभी कमांड्स देखें"
        ),
        "help": (
            "🆘 मदद केंद्र\n\n"
            "1. फीडबैक भेजने के लिए सीधे संदेश लिखें या मीडिया भेजें\n"
            "2. भाषा बदलने के लिए /language कमांड का उपयोग करें\n"
            "3. अपनी जानकारी देखने के लिए /user कमांड का उपयोग करें\n\n"
            "समस्याएं? @SkullModOwner से संपर्क करें"
        )
    },
    "english": {
        "welcome": "🇺🇸 Hello! You can now send your feedback. 👍",
        "full_welcome": (
            "🚀 Welcome to SkullCheat Feedback Bot!\n\n"
            "📢 Channel: @Skull_Cheats\n"
            "👤 Developer: @SkullModOwner\n"
            "📤 Send Screenshots: @SkullCheat_FileBot\n\n"
            "⚠️ Note: You won't get any key without feedback! 🔑"
        ),
        "user": "👤 User Dashboard\n\n🆔 ID: {user_id}\n🌐 Language: {lang}\n🚫 Banned: {banned}\n👥 Total Users: {total}",
        "banned": "🚫 You are banned. No actions allowed.",
        "language_set": "✅ Language set!\n\n{message}",
        "unauthorized": "❌ Unauthorized.",
        "ban_success": "🚫 User {user_id} banned.",
        "unban_success": "✅ User {user_id} unbanned.",
        "broadcast_result": "📢 Message sent to {count} users, {failed} failed.",
        "admin_reply_prefix": "💬 Admin reply:\n\n",
        "reply_success": "✅ Message sent successfully!",
        "reply_failed": "❌ Failed to send message.",
        "invalid_format": "⚠️ Format not supported.",
        "user_not_found": "⚠️ Original user not found.",
        "reply_instructions": "❌ Please reply to user's message.",
        "commands": (
            "📚 Available Commands:\n\n"
            "🚀 /start - Start the bot\n"
            "👤 /user - Show your info\n"
            "🌐 /language - Change language\n"
            "📝 /feedback - Send feedback\n"
            "❓ /help - Show help\n\n"
            "🔨 Admin Commands:\n"
            "🚫 /ban <user_id> - Ban a user\n"
            "✅ /unban <user_id> - Unban a user\n"
            "📢 /broadcast - Broadcast message\n"
            "📜 /commands - Show all commands"
        ),
        "help": (
            "🆘 Help Center\n\n"
            "1. To send feedback, just type your message or send media\n"
            "2. Use /language command to change language\n"
            "3. Use /user command to see your info\n\n"
            "Problems? Contact @SkullModOwner"
        )
    },
    "urdu": {
        "welcome": "🇵🇰 ہیلو! اب آپ اپنا فیڈ بیک بھیج سکتے ہیں۔",
        "full_welcome": (
            "🚀 اسکل چیٹ فیڈ بیک بوٹ میں خوش آمدید!\n\n"
            "📢 چینل: @Skull_Cheats\n"
            "👤 ڈویلپر: @SkullModOwner\n"
            "📤 اسکرین شاٹس بھیجیں: @SkullCheat_FileBot\n\n"
            "⚠️ نوٹ: فیڈ بیک کے بغیر کوئی کلید نہیں ملے گی! 🔑"
        ),
        "user": "👤 یوزر ڈیش بورڈ\n\n🆔 ID: {user_id}\n🌐 زبان: {lang}\n🚫 پابندی: {banned}\n👥 کل صارفین: {total}",
        "banned": "🚫 آپ پر پابندی عائد ہے۔ کوئی کارروائی نہیں۔",
        "language_set": "✅ زبان سیٹ ہو گئی!\n\n{message}",
        "unauthorized": "❌ غیر مجاز۔",
        "ban_success": "🚫 صارف {user_id} پر پابندی لگا دی گئی۔",
        "unban_success": "✅ صارف {user_id} کی پابندی ہٹا دی گئی۔",
        "broadcast_result": "📢 پیغام {count} صارفین کو بھیجا گیا، {failed} ناکام ہوئے۔",
        "admin_reply_prefix": "💬 ایڈمن کا جواب:\n\n",
        "reply_success": "✅ پیغام کامیابی سے بھیج دیا گیا!",
        "reply_failed": "❌ پیغام بھیجنے میں ناکام۔",
        "invalid_format": "⚠️ فارمیٹ سپورٹ نہیں کیا گیا۔",
        "user_not_found": "⚠️ اصل صارف نہیں ملا۔",
        "reply_instructions": "❌ براہ کرم صارف کے پیغام کا جواب دیں۔",
        "commands": (
            "📚 دستیاب کمانڈز:\n\n"
            "🚀 /start - بوٹ شروع کریں\n"
            "👤 /user - اپنی معلومات دیکھیں\n"
            "🌐 /language - زبان تبدیل کریں\n"
            "📝 /feedback - فیڈ بیک بھیجیں\n"
            "❓ /help - مدد دیکھیں\n\n"
            "🔨 ایڈمن کمانڈز:\n"
            "🚫 /ban <user_id> - صارف پر پابندی لگائیں\n"
            "✅ /unban <user_id> - صارف کی پابندی ہٹائیں\n"
            "📢 /broadcast - تمام کو پیغام بھیجیں\n"
            "📜 /commands - تمام کمانڈز دیکھیں"
        ),
        "help": (
            "🆘 ہیلپ سینٹر\n\n"
            "1. فیڈ بیک بھیجنے کے لیے براہ راست پیغام لکھیں یا میڈیا بھیجیں\n"
            "2. زبان تبدیل کرنے کے لیے /language کمانڈ استعمال کریں\n"
            "3. اپنی معلومات دیکھنے کے لیے /user کمانڈ استعمال کریں\n\n"
            "مسائل؟ @SkullModOwner سے رابطہ کریں"
        )
    },
    "chinese": {
        "welcome": "🇨🇳 你好！您现在可以发送反馈了。",
        "full_welcome": (
            "🚀 欢迎使用SkullCheat反馈机器人!\n\n"
            "📢 频道: @Skull_Cheats\n"
            "👤 开发者: @SkullModOwner\n"
            "📤 发送截图: @SkullCheat_FileBot\n\n"
            "⚠️ 注意: 没有反馈将不会获得任何密钥! 🔑"
        ),
        "user": "👤 用户面板\n\n🆔 ID: {user_id}\n🌐 语言: {lang}\n🚫 封禁: {banned}\n👥 总用户: {total}",
        "banned": "🚫 您已被封禁。不允许任何操作。",
        "language_set": "✅ 语言设置成功!\n\n{message}",
        "unauthorized": "❌ 未经授权。",
        "ban_success": "🚫 用户 {user_id} 已被封禁。",
        "unban_success": "✅ 用户 {user_id} 已解封。",
        "broadcast_result": "📢 消息已发送给 {count} 用户, {failed} 失败。",
        "admin_reply_prefix": "💬 管理员回复:\n\n",
        "reply_success": "✅ 消息发送成功!",
        "reply_failed": "❌ 发送消息失败。",
        "invalid_format": "⚠️ 不支持此格式。",
        "user_not_found": "⚠️ 未找到原始用户。",
        "reply_instructions": "❌ 请回复用户的消息。",
        "commands": (
            "📚 可用命令:\n\n"
            "🚀 /start - 启动机器人\n"
            "👤 /user - 查看您的信息\n"
            "🌐 /language - 更改语言\n"
            "📝 /feedback - 发送反馈\n"
            "❓ /help - 查看帮助\n\n"
            "🔨 管理员命令:\n"
            "🚫 /ban <user_id> - 封禁用户\n"
            "✅ /unban <user_id> - 解封用户\n"
            "📢 /broadcast - 广播消息\n"
            "📜 /commands - 查看所有命令"
        ),
        "help": (
            "🆘 帮助中心\n\n"
            "1. 发送反馈只需输入您的消息或发送媒体\n"
            "2. 使用/language命令更改语言\n"
            "3. 使用/user命令查看您的信息\n\n"
            "有问题? 联系 @SkullModOwner"
        )
    },
    "french": {
        "welcome": "🇫🇷 Bonjour ! Vous pouvez maintenant envoyer vos commentaires.",
        "full_welcome": (
            "🚀 Bienvenue sur le bot de feedback SkullCheat !\n\n"
            "📢 Chaîne: @Skull_Cheats\n"
            "👤 Développeur: @SkullModOwner\n"
            "📤 Envoyer des captures d'écran: @SkullCheat_FileBot\n\n"
            "⚠️ Remarque: Vous n'obtiendrez aucune clé sans feedback ! 🔑"
        ),
        "user": "👤 Tableau de bord utilisateur\n\n🆔 ID: {user_id}\n🌐 Langue: {lang}\n🚫 Banni: {banned}\n👥 Total utilisateurs: {total}",
        "banned": "🚫 Vous êtes banni. Aucune action autorisée.",
        "language_set": "✅ Langue définie !\n\n{message}",
        "unauthorized": "❌ Non autorisé.",
        "ban_success": "🚫 Utilisateur {user_id} banni.",
        "unban_success": "✅ Utilisateur {user_id} débanni.",
        "broadcast_result": "📢 Message envoyé à {count} utilisateurs, {failed} échecs.",
        "admin_reply_prefix": "💬 Réponse de l'admin:\n\n",
        "reply_success": "✅ Message envoyé avec succès !",
        "reply_failed": "❌ Échec de l'envoi du message.",
        "invalid_format": "⚠️ Format non pris en charge.",
        "user_not_found": "⚠️ Utilisateur original non trouvé.",
        "reply_instructions": "❌ Veuillez répondre au message de l'utilisateur.",
        "commands": (
            "📚 Commandes disponibles:\n\n"
            "🚀 /start - Démarrer le bot\n"
            "👤 /user - Afficher vos informations\n"
            "🌐 /language - Changer de langue\n"
            "📝 /feedback - Envoyer des commentaires\n"
            "❓ /help - Afficher l'aide\n\n"
            "🔨 Commandes admin:\n"
            "🚫 /ban <user_id> - Bannir un utilisateur\n"
            "✅ /unban <user_id> - Débannir un utilisateur\n"
            "📢 /broadcast - Diffuser un message\n"
            "📜 /commands - Afficher toutes les commandes"
        ),
        "help": (
            "🆘 Centre d'aide\n\n"
            "1. Pour envoyer des commentaires, tapez simplement votre message ou envoyez des médias\n"
            "2. Utilisez la commande /language pour changer de langue\n"
            "3. Utilisez la commande /user pour voir vos informations\n\n"
            "Problèmes? Contactez @SkullModOwner"
        )
    },
    "spanish": {
        "welcome": "🇪🇸 ¡Hola! Ahora puedes enviar tus comentarios.",
        "full_welcome": (
            "🚀 ¡Bienvenido al bot de comentarios SkullCheat!\n\n"
            "📢 Canal: @Skull_Cheats\n"
            "👤 Desarrollador: @SkullModOwner\n"
            "📤 Enviar capturas de pantalla: @SkullCheat_FileBot\n\n"
            "⚠️ Nota: ¡No obtendrás ninguna clave sin comentarios! 🔑"
        ),
        "user": "👤 Panel de usuario\n\n🆔 ID: {user_id}\n🌐 Idioma: {lang}\n🚫 Baneado: {banned}\n👥 Total de usuarios: {total}",
        "banned": "🚫 Estás baneado. No se permiten acciones.",
        "language_set": "✅ ¡Idioma establecido!\n\n{message}",
        "unauthorized": "❌ No autorizado.",
        "ban_success": "🚫 Usuario {user_id} baneado.",
        "unban_success": "✅ Usuario {user_id} desbaneado.",
        "broadcast_result": "📢 Mensaje enviado a {count} usuarios, {failed} fallidos.",
        "admin_reply_prefix": "💬 Respuesta del admin:\n\n",
        "reply_success": "✅ ¡Mensaje enviado con éxito!",
        "reply_failed": "❌ Error al enviar el mensaje.",
        "invalid_format": "⚠️ Formato no soportado.",
        "user_not_found": "⚠️ Usuario original no encontrado.",
        "reply_instructions": "❌ Por favor, responde al mensaje del usuario.",
        "commands": (
            "📚 Comandos disponibles:\n\n"
            "🚀 /start - Iniciar el bot\n"
            "👤 /user - Mostrar tu información\n"
            "🌐 /language - Cambiar idioma\n"
            "📝 /feedback - Enviar comentarios\n"
            "❓ /help - Mostrar ayuda\n\n"
            "🔨 Comandos de admin:\n"
            "🚫 /ban <user_id> - Banear a un usuario\n"
            "✅ /unban <user_id> - Desbanear a un usuario\n"
            "📢 /broadcast - Transmitir mensaje\n"
            "📜 /commands - Mostrar todos los comandos"
        ),
        "help": (
            "🆘 Centro de ayuda\n\n"
            "1. Para enviar comentarios, simplemente escribe tu mensaje o envía medios\n"
            "2. Usa el comando /language para cambiar el idioma\n"
            "3. Usa el comando /user para ver tu información\n\n"
            "¿Problemas? Contacta a @SkullModOwner"
        )
    },
    "turkish": {
        "welcome": "🇹🇷 Merhaba! Artık geri bildirim gönderebilirsiniz.",
        "full_welcome": (
            "🚀 SkullCheat Geri Bildirim Botuna Hoş Geldiniz!\n\n"
            "📢 Kanal: @Skull_Cheats\n"
            "👤 Geliştirici: @SkullModOwner\n"
            "📤 Ekran görüntüleri gönderin: @SkullCheat_FileBot\n\n"
            "⚠️ Not: Geri bildirim olmadan herhangi bir anahtar alamazsınız! 🔑"
        ),
        "user": "👤 Kullanıcı Paneli\n\n🆔 ID: {user_id}\n🌐 Dil: {lang}\n🚫 Yasaklı: {banned}\n👥 Toplam kullanıcı: {total}",
        "banned": "🚫 Yasaklandınız. Hiçbir işleme izin verilmiyor.",
        "language_set": "✅ Dil ayarlandı!\n\n{message}",
        "unauthorized": "❌ Yetkisiz.",
        "ban_success": "🚫 Kullanıcı {user_id} yasaklandı.",
        "unban_success": "✅ Kullanıcı {user_id} yasağı kaldırıldı.",
        "broadcast_result": "📢 Mesaj {count} kullanıcıya gönderildi, {failed} başarısız.",
        "admin_reply_prefix": "💬 Admin yanıtı:\n\n",
        "reply_success": "✅ Mesaj başarıyla gönderildi!",
        "reply_failed": "❌ Mesaj gönderilemedi.",
        "invalid_format": "⚠️ Desteklenmeyen biçim.",
        "user_not_found": "⚠️ Orijinal kullanıcı bulunamadı.",
        "reply_instructions": "❌ Lütfen kullanıcının mesajına yanıt verin.",
        "commands": (
            "📚 Mevcut komutlar:\n\n"
            "🚀 /start - Botu başlat\n"
            "👤 /user - Bilgilerini göster\n"
            "🌐 /language - Dil değiştir\n"
            "📝 /feedback - Geri bildirim gönder\n"
            "❓ /help - Yardım göster\n\n"
            "🔨 Admin komutları:\n"
            "🚫 /ban <user_id> - Kullanıcıyı yasakla\n"
            "✅ /unban <user_id> - Kullanıcı yasağını kaldır\n"
            "📢 /broadcast - Mesaj yayınla\n"
            "📜 /commands - Tüm komutları göster"
        ),
        "help": (
            "🆘 Yardım Merkezi\n\n"
            "1. Geri bildirim göndermek için sadece mesaj yazın veya medya gönderin\n"
            "2. Dil değiştirmek için /language komutunu kullanın\n"
            "3. Bilgilerinizi görmek için /user komutunu kullanın\n\n"
            "Sorunlar? @SkullModOwner ile iletişime geçin"
        )
    }
}

# -------------------- HELPER FUNCTIONS --------------------
def get_user_language(user_id: str) -> str:
    """Get user's preferred language, default to English if not set."""
    return user_lang.get(user_id, "english")

def get_message(user_id: str, key: str, **kwargs) -> str:
    """Get localized message for user."""
    lang = get_user_language(user_id)
    return LANGUAGES.get(lang, LANGUAGES["english"]).get(key, "").format(**kwargs)

def is_admin(user_id: str) -> bool:
    """Check if user is admin."""
    return user_id in ADMIN_IDS

def is_banned(user_id: str) -> bool:
    """Check if user is banned."""
    return user_id in banned_users

# -------------------- COMMAND HANDLERS --------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    
    if is_banned(user_id):
        await update.message.reply_text(get_message(user_id, "banned"))
        return

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🇮🇳 Hindi", callback_data="lang_hindi"),
         InlineKeyboardButton("🇺🇸 English", callback_data="lang_english")],
        [InlineKeyboardButton("🇵🇰 Urdu", callback_data="lang_urdu"),
         InlineKeyboardButton("🇨🇳 Chinese", callback_data="lang_chinese")],
        [InlineKeyboardButton("🇫🇷 French", callback_data="lang_french"),
         InlineKeyboardButton("🇪🇸 Spanish", callback_data="lang_spanish")],
        [InlineKeyboardButton("🇹🇷 Turkish", callback_data="lang_turkish")]
    ])
    
    await update.message.reply_text(
        "🌐 अपनी भाषा चुनें / Select Your Language:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

async def language_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    lang = query.data.replace("lang_", "")

    user_lang[user_id] = lang
    
    welcome_msg = LANGUAGES.get(lang, LANGUAGES["english"])["welcome"]
    full_welcome = LANGUAGES.get(lang, LANGUAGES["english"])["full_welcome"]
    
    await query.edit_message_text(
        get_message(user_id, "language_set", message=welcome_msg),
        parse_mode="HTML"
    )
    await context.bot.send_message(
        chat_id=int(user_id),
        text=full_welcome,
        parse_mode="HTML"
    )

async def change_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    
    if is_banned(user_id):
        await update.message.reply_text(get_message(user_id, "banned"))
        return

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🇮🇳 Hindi", callback_data="lang_hindi"),
         InlineKeyboardButton("🇺🇸 English", callback_data="lang_english")],
        [InlineKeyboardButton("🇵🇰 Urdu", callback_data="lang_urdu"),
         InlineKeyboardButton("🇨🇳 Chinese", callback_data="lang_chinese")],
        [InlineKeyboardButton("🇫🇷 French", callback_data="lang_french"),
         InlineKeyboardButton("🇪🇸 Spanish", callback_data="lang_spanish")],
        [InlineKeyboardButton("🇹🇷 Turkish", callback_data="lang_turkish")]
    ])
    
    await update.message.reply_text(
        "🌐 अपनी भाषा चुनें / Select Your Language:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

async def user_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    user_id = str(user.id)
    lang = get_user_language(user_id)
    banned = "Yes 🚫" if is_banned(user_id) else "No ✅"
    total = len(user_lang)

    await update.message.reply_text(
        get_message(user_id, "user", user_id=user_id, lang=lang.capitalize(), banned=banned, total=total),
        parse_mode="HTML"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    await update.message.reply_text(
        get_message(user_id, "help"),
        parse_mode="HTML"
    )

async def feedback_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    
    if is_banned(user_id):
        await update.message.reply_text(get_message(user_id, "banned"))
        return

    await update.message.reply_text(
        get_message(user_id, "welcome"),
        parse_mode="HTML"
    )

async def commands_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    await update.message.reply_text(
        get_message(user_id, "commands"),
        parse_mode="HTML"
    )

# -------------------- ADMIN COMMANDS --------------------
async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    admin_id = str(update.effective_user.id)
    
    if not is_admin(admin_id):
        await update.message.reply_text(get_message(admin_id, "unauthorized"))
        return

    if not context.args:
        await update.message.reply_text("⚠️ Usage: /ban <user_id>")
        return
    
    user_id = context.args[0]
    banned_users.add(user_id)
    await update.message.reply_text(get_message(admin_id, "ban_success", user_id=user_id))

async def unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    admin_id = str(update.effective_user.id)
    
    if not is_admin(admin_id):
        await update.message.reply_text(get_message(admin_id, "unauthorized"))
        return

    if not context.args:
        await update.message.reply_text("⚠️ Usage: /unban <user_id>")
        return
    
    user_id = context.args[0]
    banned_users.discard(user_id)
    await update.message.reply_text(get_message(admin_id, "unban_success", user_id=user_id))

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    admin_id = str(update.effective_user.id)
    
    if not is_admin(admin_id):
        await update.message.reply_text(get_message(admin_id, "unauthorized"))
        return

    if not update.message.reply_to_message and not context.args:
        await update.message.reply_text("⚠️ Usage: Reply to a message or type /broadcast <message>")
        return
    
    msg = update.message.reply_to_message if update.message.reply_to_message else update.message
    msg_text = " ".join(context.args) if context.args else None
    
    count = 0
    failed = 0
    
    for uid in list(user_lang.keys()):
        try:
            if update.message.reply_to_message:
                await context.bot.copy_message(
                    chat_id=int(uid),
                    from_chat_id=update.message.chat_id,
                    message_id=msg.message_id
                )
            else:
                await context.bot.send_message(
                    chat_id=int(uid),
                    text=msg_text
                )
            count += 1
        except Exception as e:
            failed += 1
            logger.warning(f"Broadcast to {uid} failed: {e}")
    
    await update.message.reply_text(
        get_message(admin_id, "broadcast_result", count=count, failed=failed)
    )

# -------------------- MESSAGE HANDLERS --------------------
async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    user_id = str(user.id)

    if is_banned(user_id):
        await update.message.reply_text(get_message(user_id, "banned"))
        return
    
    for admin_id in ADMIN_IDS:
        try:
            if update.message.text:
                sent = await context.bot.send_message(
                    chat_id=int(admin_id),
                    text=(
                        f"📩 From: {user.full_name} (@{user.username or 'NoUsername'})\n"
                        f"🆔 ID: {user.id}\n\n"
                        f"📝 {update.message.text}"
                    ),
                    parse_mode="HTML"
                )
            else:
                sent = await context.bot.forward_message(
                    chat_id=int(admin_id),
                    from_chat_id=user.id,
                    message_id=update.message.message_id
                )
            forward_map[sent.message_id] = user.id
        except Exception as e:
            logger.error(f"Forward Error to admin {admin_id}: {e}")

async def handle_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    admin_id = str(update.effective_user.id)
    
    if not is_admin(admin_id):
        await update.message.reply_text(get_message(admin_id, "unauthorized"))
        return

    msg = update.message
    if not msg.reply_to_message:
        await update.message.reply_text(get_message(admin_id, "reply_instructions"))
        return
    
    reply_msg_id = msg.reply_to_message.message_id
    user_id = forward_map.get(reply_msg_id)
    
    if not user_id:
        await update.message.reply_text(get_message(admin_id, "user_not_found"))
        return
    
    try:
        prefix = get_message(admin_id, "admin_reply_prefix")
        kwargs = {"chat_id": user_id, "parse_mode": "HTML"}
        
        if msg.text:
            await context.bot.send_message(text=prefix + msg.text, **kwargs)
        elif msg.photo:
            await context.bot.send_photo(
                photo=msg.photo[-1].file_id,
                caption=prefix + (msg.caption or ""),
                **kwargs
            )
        elif msg.document:
            await context.bot.send_document(
                document=msg.document.file_id,
                caption=prefix + (msg.caption or ""),
                **kwargs
            )
        elif msg.video:
            await context.bot.send_video(
                video=msg.video.file_id,
                caption=prefix + (msg.caption or ""),
                **kwargs
            )
        elif msg.audio:
            await context.bot.send_audio(
                audio=msg.audio.file_id,
                caption=prefix + (msg.caption or ""),
                **kwargs
            )
        elif msg.voice:
            await context.bot.send_voice(
                voice=msg.voice.file_id,
                caption=prefix + (msg.caption or ""),
                **kwargs
            )
        elif msg.sticker:
            await context.bot.send_sticker(
                chat_id=user_id,
                sticker=msg.sticker.file_id
            )
        else:
            await update.message.reply_text(get_message(admin_id, "invalid_format"))
            return
        
        await update.message.reply_text(get_message(admin_id, "reply_success"))
    except Exception as e:
        logger.error(f"Reply Error: {e}")
        await update.message.reply_text(get_message(admin_id, "reply_failed"))

# -------------------- MAIN FUNCTION --------------------
def main() -> None:
    """Start the bot."""
    application = ApplicationBuilder().token(TOKEN).build()

    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("user", user_dashboard))
    application.add_handler(CommandHandler("language", change_language))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("feedback", feedback_command))
    application.add_handler(CommandHandler("commands", commands_list))
    
    # Admin command handlers
    application.add_handler(CommandHandler("ban", ban_user))
    application.add_handler(CommandHandler("unban", unban_user))
    application.add_handler(CommandHandler("broadcast", broadcast))

    # Callback handlers
    application.add_handler(CallbackQueryHandler(language_selected, pattern="^lang_"))

    # Message handlers
    application.add_handler(MessageHandler(filters.ChatType.PRIVATE & filters.REPLY, handle_admin_reply))
    application.add_handler(MessageHandler(filters.ChatType.PRIVATE & ~filters.COMMAND, handle_user_message))

    # Start the Bot
    application.run_polling()
    logger.info("Bot started and running...")

if __name__ == "__main__":
    main()