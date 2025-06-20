"""
Telegram Feedback Bot - Clean Structure
Author: SkullModOwner
Date: 2025-06-20
"""

import os
import json
import logging
from typing import Dict, Set, Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
)
import uuid
import random
import pathlib
import subprocess
import platform
import psutil
import socket
import time
import datetime

# -------------------- CONFIGURATION --------------------
TOKEN = "8008021512:AAHEtYedUgpy31iRVWy5WjxCuELuTZTWPfQ"
ADMIN_IDS = {"5524867269", "7306222826"}
FILE_DB = "files_db.json"
FILES_DB = "files.json"
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB

# -------------------- GLOBAL STATE --------------------
banned_users: Set[str] = set()
user_lang: Dict[str, str] = {}
forward_map: Dict[int, int] = {}
admin_upload_flags = set()

# -------------------- LOGGER --------------------
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# -------------------- LANGUAGE DATA --------------------
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
    },
    "bengali": {
        "welcome": "🇧🇩 স্বাগতম! এখন আপনি আপনার প্রতিক্রিয়া পাঠাতে পারেন।",
        "full_welcome": (
            "🚀 SkullCheat প্রতিক্রিয়া বট-এ স্বাগতম!\n\n"
            "📢 চ্যানেল: @Skull_Cheats\n"
            "👤 ডেভেলপার: @SkullModOwner\n"
            "📤 স্ক্রীনশট পাঠান: @SkullCheat_FileBot\n\n"
            "⚠️ নোট: প্রতিক্রিয়া ছাড়া আপনি কোনও কী পাবেন না! 🔑"
        ),
        "user": "👤 ব্যবহারকারী ড্যাশবোর্ড\n\n🆔 ID: {user_id}\n🌐 ভাষা: {lang}\n🚫 নিষিদ্ধ: {banned}\n👥 মোট ব্যবহারকারী: {total}",
        "banned": "🚫 আপনি নিষিদ্ধ। কোনও ক্রিয়া অনুমোদিত নয়।",
        "language_set": "✅ ভাষা সেট করা হয়েছে!\n\n{message}",
        "unauthorized": "❌ অনুমোদিত নয়।",
        "ban_success": "🚫 ব্যবহারকারী {user_id} নিষিদ্ধ হয়েছে।",
        "unban_success": "✅ ব্যবহারকারী {user_id} এর নিষেধাজ্ঞা প্রত্যাহার করা হয়েছে।",
        "broadcast_result": "📢 বার্তা {count} ব্যবহারকারীর কাছে পাঠানো হয়েছে, {failed} ব্যর্থ হয়েছে।",
        "admin_reply_prefix": "💬 প্রশাসকের উত্তর:\n\n",
        "reply_success": "✅ বার্তা সফলভাবে পাঠানো হয়েছে!",
        "reply_failed": "❌ বার্তা পাঠাতে ব্যর্থ হয়েছে।",
        "invalid_format": "⚠️ ফরম্যাট সমর্থিত নয়।",
        "user_not_found": "⚠️ মূল ব্যবহারকারী পাওয়া যায়নি।",
        "reply_instructions": "❌ দয়া করে ব্যবহারকারীর বার্তায় উত্তর দিন।",
        "commands": (
            "📚 উপলব্ধ কমান্ড:\n\n"
            "🚀 /start - বট শুরু করুন\n"
            "👤 /user - আপনার তথ্য দেখান\n"
            "🌐 /language - ভাষা পরিবর্তন করুন\n"
            "📝 /feedback - প্রতিক্রিয়া পাঠান\n"
            "❓ /help - সহায়তা দেখান\n\n"
            "🔨 প্রশাসক কমান্ড:\n"
            "🚫 /ban <user_id> - একটি ব্যবহারকারী নিষিদ্ধ করুন\n"
            "✅ /unban <user_id> - একটি ব্যবহারকারীর নিষেধাজ্ঞা প্রত্যাহার করুন\n"
            "📢 /broadcast - বার্তা সম্প্রচার করুন\n"
            "📜 /commands - সমস্ত কমান্ড দেখান"
        ),
        "help": (
            "🆘 সহায়তা কেন্দ্র\n\n"
            "1. প্রতিক্রিয়া পাঠাতে, কেবল আপনার বার্তা টাইপ করুন বা মিডিয়া পাঠান\n"
            "2. ভাষা পরিবর্তন করতে /language কমান্ড ব্যবহার করুন\n"
            "3. আপনার তথ্য দেখতে /user কমান্ড ব্যবহার করুন\n\n"
            "সমস্যা? @SkullModOwner এর সাথে যোগাযোগ করুন"
        )
    },
    "telugu": {
        "welcome": "🇮🇳 స్వాగతం! మీరు ఇప్పుడు మీ అభిప్రాయాన్ని పంపవచ్చు.",
        "full_welcome": (
            "🚀 SkullCheat అభిప్రాయ బాట్ కు స్వాగతం!\n\n"
            "📢 ఛానల్: @Skull_Cheats\n"
            "👤 డెవలపర్: @SkullModOwner\n"
            "📤 స్క్రీన్‌షాట్‌లు పంపండి: @SkullCheat_FileBot\n\n"
            "⚠️ గమనిక: అభిప్రాయం లేకుండా మీకు ఎలాంటి కీ లభించదు! 🔑"
        ),
        "user": "👤 వినియోగదారు డాష్‌బోర్డ్\n\n🆔 ID: {user_id}\n🌐 భాష: {lang}\n🚫 నిషేధిత: {banned}\n👥 మొత్తం వినియోగదారులు: {total}",
        "banned": "🚫 మీరు నిషేధితులయ్యారు. ఎలాంటి చర్యలు అనుమతించబడవు.",
        "language_set": "✅ భాష సెట్ చేయబడింది!\n\n{message}",
        "unauthorized": "❌ అనుమతించబడలేదు.",
        "ban_success": "🚫 వినియోగదారు {user_id} నిషేధించబడింది.",
        "unban_success": "✅ వినియోగదారు {user_id} యొక్క నిషేధం తొలగించబడింది.",
        "broadcast_result": "📢 సందేశం {count} వినియోగదారులకు పంపబడింది, {failed} విఫలమైంది.",
        "admin_reply_prefix": "💬 అడ్మిన్ సమాధానం:\n\n",
        "reply_success": "✅ సందేశం విజయవంతంగా పంపబడింది!",
        "reply_failed": "❌ సందేశం పంపడంలో విఫలమైంది.",
        "invalid_format": "⚠️ ఫార్మాట్ మద్దతు లేదు.",
        "user_not_found": "⚠️ అసలు వినియోగదారు కనుగొనబడలేదు.",
        "reply_instructions": "❌ దయచేసి వినియోగదారుని సందేశానికి సమాధానం ఇవ్వండి.",
        "commands": (
            "📚 అందుబాటులో ఉన్న ఆదేశాలు:\n\n"
            "🚀 /start - బాట్ ప్రారంభించండి\n"
            "👤 /user - మీ సమాచారాన్ని చూపించండి\n"
            "🌐 /language - భాషను మార్చండి\n"
            "📝 /feedback - అభిప్రాయం పంపండి\n"
            "❓ /help - సహాయం చూపించండి\n\n"
            "🔨 అడ్మిన్ ఆదేశాలు:\n"
            "🚫 /ban <user_id> - వినియోగదారుని నిషేధించండి\n"
            "✅ /unban <user_id> - వినియోగదారుని నిషేధం తొలగించండి\n"
            "📢 /broadcast - సందేశాన్ని ప్రసారం చేయండి\n"
            "📜 /commands - అన్ని ఆదేశాలను చూపించండి"
        ),
        "help": (
            "🆘 సహాయ కేంద్రం\n\n"
            "1. అభిప్రాయం పంపడానికి, కేవలం మీ సందేశాన్ని టైప్ చేయండి లేదా మీడియాను పంపండి\n"
            "2. భాషను మార్చడానికి /language ఆదేశాన్ని ఉపయోగించండి\n"
            "3. మీ సమాచారాన్ని చూడటానికి /user ఆదేశాన్ని ఉపయోగించండి\n\n"
            "సమస్యలు? @SkullModOwner తో సంప్రదించండి"
        )
    },
    "marathi": {
        "welcome": "🇮🇳 स्वागत आहे! आपण आता आपली प्रतिक्रिया पाठवू शकता.",
        "full_welcome": (
            "🚀 SkullCheat फीडबॅक बॉटमध्ये आपले स्वागत आहे!\n\n"
            "📢 चॅनेल: @Skull_Cheats\n"
            "👤 विकासक: @SkullModOwner\n"
            "📤 स्क्रीनशॉट पाठवा: @SkullCheat_FileBot\n\n"
            "⚠️ नोट: फीडबॅकशिवाय तुम्हाला कोणतीही की मिळणार नाही! 🔑"
        ),
        "user": "👤 वापरकर्ता डॅशबोर्ड\n\n🆔 ID: {user_id}\n🌐 भाषा: {lang}\n🚫 बंदी: {banned}\n👥 एकूण वापरकर्ते: {total}",
        "banned": "🚫 तुम्हाला बंदी घालण्यात आली आहे. कोणतीही क्रिया करण्यास मनाई आहे.",
        "language_set": "✅ भाषा सेट करण्यात आली आहे!\n\n{message}",
        "unauthorized": "❌ अधिकृत नाही.",
        "ban_success": "🚫 वापरकर्ता {user_id} बंदी घातली गेली आहे.",
        "unban_success": "✅ वापरकर्ता {user_id} ची बंदी काढण्यात आली आहे.",
        "broadcast_result": "📢 संदेश {count} वापरकर्त्यांना पाठविला गेला, {failed} अयशस्वी.",
        "admin_reply_prefix": "💬 प्रशासकाची प्रतिक्रिया:\n\n",
        "reply_success": "✅ संदेश यशस्वीरित्या पाठविला गेला!",
        "reply_failed": "❌ संदेश पाठवण्यात अयशस्वी.",
        "invalid_format": "⚠️ फॉरमॅटला समर्थन नाही.",
        "user_not_found": "⚠️ मूळ वापरकर्ता सापडला नाही.",
        "reply_instructions": "❌ कृपया वापरकर्त्याच्या संदेशावर उत्तर द्या.",
        "commands": (
            "📚 उपलब्ध आदेश:\n\n"
            "🚀 /start - बॉट सुरू करा\n"
            "👤 /user - तुमची माहिती दर्शवा\n"
            "🌐 /language - भाषा बदला\n"
            "📝 /feedback - फीडबॅक पाठवा\n"
            "❓ /help - मदत दर्शवा\n\n"
            "🔨 प्रशासक आदेश:\n"
            "🚫 /ban <user_id> - वापरकर्त्यावर बंदी घाला\n"
            "✅ /unban <user_id> - वापरकर्त्याची बंदी काढा\n"
            "📢 /broadcast - संदेश प्रसारित करा\n"
            "📜 /commands - सर्व आदेश दर्शवा"
        ),
        "help": (
            "🆘 मदत केंद्र\n\n"
            "1. फीडबॅक पाठवण्यासाठी, फक्त तुमचा संदेश टाइप करा किंवा मीडिया पाठवा\n"
            "2. भाषा बदलण्यासाठी /language आदेश वापरा\n"
            "3. तुमची माहिती पाहण्यासाठी /user आदेश वापरा\n\n"
            "समस्यांचा सामना करत आहात का? @SkullModOwner यांच्याशी संपर्क साधा"
        )
    },
    "tamil": {
        "welcome": "🇮🇳 வணக்கம்! நீங்கள் இப்போது உங்கள் கருத்துகளை அனுப்பலாம்.",
        "full_welcome": (
            "🚀 SkullCheat கருத்து பாட்டில் உங்களை வரவேற்கிறோம்!\n\n"
            "📢 சேனல்: @Skull_Cheats\n"
            "👤 டெவலப்பர்: @SkullModOwner\n"
            "📤 திரைபடங்களை அனுப்பவும்: @SkullCheat_FileBot\n\n"
            "⚠️ குறிப்பு: கருத்து இல்லாமல் நீங்கள் எந்த விசையையும் பெற முடியாது! 🔑"
        ),
        "user": "👤 பயனர் டாஷ்போர்டு\n\n🆔 ID: {user_id}\n🌐 மொழி: {lang}\n🚫 தடை: {banned}\n👥 மொத்த பயனர்கள்: {total}",
        "banned": "🚫 நீங்கள் தடை செய்யப்பட்டுள்ளீர்கள். எந்த நடவடிக்கைகளும் அனுமதிக்கப்படவில்லை.",
        "language_set": "✅ மொழி அமைக்கப்பட்டது!\n\n{message}",
        "unauthorized": "❌ அனுமதிக்கப்படவில்லை.",
        "ban_success": "🚫 பயனர் {user_id} தடை செய்யப்பட்டது.",
        "unban_success": "✅ பயனர் {user_id} இன் தடை kaldırıldı.",
        "broadcast_result": "📢 செய்தி {count} பயனர்களுக்கு அனுப்பப்பட்டது, {failed} தோல்வியுற்றது.",
        "admin_reply_prefix": "💬 நிர்வாகியின் பதில்:\n\n",
        "reply_success": "✅ செய்தி வெற்றிகரமாக அனுப்பப்பட்டது!",
        "reply_failed": "❌ செய்தி அனுப்புவதில் தோல்வி.",
        "invalid_format": "⚠️ வடிவம் ஆதரிக்கப்படவில்லை.",
        "user_not_found": "⚠️ முதன்மை பயனர் காணப்படவில்லை.",
        "reply_instructions": "❌ தயவுசெய்து பயனரின் செய்திக்கு பதிலளிக்கவும்.",
        "commands": (
            "📚 கிடைக்கும் கட்டளைகள்:\n\n"
            "🚀 /start - பாட்டை தொடங்கவும்\n"
            "👤 /user - உங்கள் தகவலைக் காண்பிக்கவும்\n"
            "🌐 /language - மொழியை மாற்றவும்\n"
            "📝 /feedback - கருத்துகளை அனுப்பவும்\n"
            "❓ /help - உதவியை காண்பிக்கவும்\n\n"
            "🔨 நிர்வாகி கட்டளைகள்:\n"
            "🚫 /ban <user_id> - பயனரை தடை செய்யவும்\n"
            "✅ /unban <user_id> - பயனரின் தடை kaldırıldı.\n"
            "📢 /broadcast - செய்தியை ஒளிபரப்பவும்\n"
            "📜 /commands - அனைத்து கட்டளைகளையும் காண்பிக்கவும்"
        ),
        "help": (
            "🆘 உதவி மையம்\n\n"
            "1. கருத்துகளை அனுப்ப, உங்கள் செய்தியைத் தட்டச்சி செய்யவும் அல்லது மீடியாவை அனுப்பவும்\n"
            "2. மொழியை மாற்ற /language கட்டளையைப் பயன்படுத்தவும்\n"
            "3. உங்கள் தகவலைப் பார்க்க /user கட்டளையைப் பயன்படுத்தவும்\n\n"
            "சிக்கல்களா? @SkullModOwner உடன் தொடர்பு கொள்ளவும்"
        )
    },
    "gujarati": {
        "welcome": "🇮🇳 સ્વાગત છે! તમે હવે તમારી પ્રતિસાદ મોકલી શકો છો.",
        "full_welcome": (
            "🚀 SkullCheat પ્રતિસાદ બોટમાં આપનું સ્વાગત છે!\n\n"
            "📢 ચેનલ: @Skull_Cheats\n"
            "👤 ડેવલપર: @SkullModOwner\n"
            "📤 સ્ક્રીનશોટ મોકલો: @SkullCheat_FileBot\n\n"
            "⚠️ નોંધ: પ્રતિસાદ વિના તમને કોઈ કી મળશે નહીં! 🔑"
        ),
        "user": "👤 વપરાશકર્તા ડેશબોર્ડ\n\n🆔 ID: {user_id}\n🌐 ભાષા: {lang}\n🚫 પ્રતિબંધિત: {banned}\n👥 કુલ વપરાશકર્તાઓ: {total}",
        "banned": "🚫 તમે પ્રતિબંધિત છો. કોઈપણ ક્રિયા કરવાની મંજૂરી નથી.",
        "language_set": "✅ ભાષા સેટ કરવામાં આવી છે!\n\n{message}",
        "unauthorized": "❌ અધિકૃત નથી.",
        "ban_success": "🚫 વપરાશકર્તા {user_id} પ્રતિબંધિત થયો છે.",
        "unban_success": "✅ વપરાશકર્તા {user_id} નો પ્રતિબંધ હટાવવામાં આવ્યો છે.",
        "broadcast_result": "📢 સંદેશા {count} વપરાશકર્તાઓને મોકલવામાં આવ્યો, {failed} નિષ્ફળ રહ્યો.",
        "admin_reply_prefix": "💬 પ્રશાસકની પ્રતિસાદ:\n\n",
        "reply_success": "✅ સંદેશો સફળતાપૂર્વક મોકલવામાં આવ્યો!",
        "reply_failed": "❌ સંદેશો મોકલવામાં નિષ્ફળ.",
        "invalid_format": "⚠️ ફોર્મેટને સપોર્ટ નથી કરતું.",
        "user_not_found": "⚠️ મૂળ વપરાશકર્તા મળ્યો નથી.",
        "reply_instructions": "❌ કૃપા કરીને વપરાશકર્તાના સંદેશા પર જવાબ આપો.",
        "commands": (
            "📚 ઉપલબ્ધ આદેશો:\n\n"
            "🚀 /start - બોટ શરૂ કરો\n"
            "👤 /user - તમારી માહિતી બતાવો\n"
            "🌐 /language - ભાષા બદલો\n"
            "📝 /feedback - પ્રતિસાદ મોકલો\n"
            "❓ /help - મદદ જુઓ\n\n"
            "🔨 પ્રશાસક આદેશો:\n"
            "🚫 /ban <user_id> - વપરાશકર્તાને પ્રતિબંધિત કરો\n"
            "✅ /unban <user_id> - વપરાશકર્તાની પ્રતિબંધ હટાવો\n"
            "📢 /broadcast - સંદેશા પ્રસારિત કરો\n"
            "📜 /commands - તમામ આદેશો જુઓ"
        ),
        "help": (
            "🆘 મદદ કેન્દ્ર\n\n"
            "1. પ્રતિસાદ મોકલવા માટે, ફક્ત તમારું સંદેશા ટાઇપ કરો અથવા મીડિયા મોકલો\n"
            "2. ભાષા બદલવા માટે /language આદેશનો ઉપયોગ કરો\n"
            "3. તમારી માહિતી જોવા માટે /user આદેશનો ઉપયોગ કરો\n\n"
            "સમસ્યાઓ? @SkullModOwner સાથે સંપર્ક કરો"
        )
    },
    "kannada": {
        "welcome": "🇮🇳 ಸ್ವಾಗತ! ನೀವು ಈಗ ನಿಮ್ಮ ಪ್ರತಿಕ್ರಿಯೆಯನ್ನು ಕಳುಹಿಸಬಹುದು.",
        "full_welcome": (
            "🚀 SkullCheat ಪ್ರತಿಕ್ರಿಯೆ ಬಾಟ್ ಗೆ ಸ್ವಾಗತ!\n\n"
            "📢 ಚಾನೆಲ್: @Skull_Cheats\n"
            "👤 ಡೆವಲಪರ್: @SkullModOwner\n"
            "📤 ಸ್ಕ್ರೀನ್‌ಶಾಟ್‌ಗಳನ್ನು ಕಳುಹಿಸಿ: @SkullCheat_FileBot\n\n"
            "⚠️ ಟಿಪ್ಪಣಿ: ಪ್ರತಿಕ್ರಿಯೆ ಇಲ್ಲದೆ ನೀವು ಯಾವುದೇ ಕೀ ಪಡೆಯುವುದಿಲ್ಲ! 🔑"
        ),
        "user": "👤 ಬಳಕೆದಾರ ಡ್ಯಾಶ್‌ಬೋರ್ಡ್\n\n🆔 ID: {user_id}\n🌐 ಭಾಷೆ: {lang}\n🚫 ನಿಷೇಧಿತ: {banned}\n👥 ಒಟ್ಟು ಬಳಕೆದಾರರು: {total}",
        "banned": "🚫 ನೀವು ನಿಷೇಧಿತರಾಗಿದ್ದೀರಿ. ಯಾವುದೇ ಕ್ರಿಯೆಗಳಿಗೆ ಅನುಮತಿ ಇಲ್ಲ.",
        "language_set": "✅ ಭಾಷೆ ಹೊಂದಿಸಲಾಗಿದೆ!\n\n{message}",
        "unauthorized": "❌ ಅನುಮತಿಸಲಾಗಿಲ್ಲ.",
        "ban_success": "🚫 ಬಳಕೆದಾರ {user_id} ನಿಷೇಧಿಸಲಾಗಿದೆ.",
        "unban_success": "✅ ಬಳಕೆದಾರ {user_id} ನಿಷೇಧವನ್ನು ಹಿಂತೆಗೆದುಕೊಳ್ಳಲಾಗಿದೆ.",
        "broadcast_result": "📢 ಸಂದೇಶ {count} ಬಳಕೆದಾರರಿಗೆ ಕಳುಹಿಸಲಾಗಿದೆ, {failed} ವಿಫಲವಾಗಿದೆ.",
        "admin_reply_prefix": "💬 ಆಡಳಿತಗಾರನ ಪ್ರತಿಸ್ಪಂದನೆ:\n\n",
        "reply_success": "✅ ಸಂದೇಶ ಯಶಸ್ವಿಯಾಗಿ ಕಳುಹಿಸಲಾಗಿದೆ!",
        "reply_failed": "❌ ಸಂದೇಶ ಕಳುಹಿಸಲು ವಿಫಲವಾಗಿದೆ.",
        "invalid_format": "⚠️ ಫಾರ್ಮಾಟ್ ಬೆಂಬಲಿತವಲ್ಲ.",
        "user_not_found": "⚠️ ಮೂಲ ಬಳಕೆದಾರನನ್ನು ಕಂಡುಹಿಡಿಯಲಾಗಲಿಲ್ಲ.",
        "reply_instructions": "❌ ದಯವಿಟ್ಟು ಬಳಕೆದಾರನ ಸಂದೇಶಕ್ಕೆ ಉತ್ತರಿಸಿ.",
        "commands": (
            "📚 ಲಭ್ಯವಿರುವ ಆಜ್ಞೆಗಳು:\n\n"
            "🚀 /start - ಬಾಟ್ ಅನ್ನು ಪ್ರಾರಂಭಿಸಿ\n"
            "👤 /user - ನಿಮ್ಮ ಮಾಹಿತಿಯನ್ನು ತೋರಿಸಿ\n"
            "🌐 /language - ಭಾಷೆಯನ್ನು ಬದಲಾಯಿಸಿ\n"
            "📝 /feedback - ಪ್ರತಿಕ್ರಿಯೆ ಕಳುಹಿಸಿ\n"
            "❓ /help - ಸಹಾಯವನ್ನು ತೋರಿಸಿ\n\n"
            "🔨 ಆಡಳಿತಗಾರ ಆಜ್ಞೆಗಳು:\n"
            "🚫 /ban <user_id> - ಬಳಕೆದಾರನನ್ನು ನಿಷೇಧಿಸಿ\n"
            "✅ /unban <user_id> - ಬಳಕೆದಾರನ ನಿಷೇಧವನ್ನು ಹಿಂತೆಗೆದುಕೊಳ್ಳಿ\n"
            "📢 /broadcast - ಸಂದೇಶವನ್ನು ಪ್ರಸಾರ ಮಾಡಿ\n"
            "📜 /commands - ಎಲ್ಲಾ ಆಜ್ಞೆಗಳನ್ನು ತೋರಿಸಿ"
        ),
        "help": (
            "🆘 ಸಹಾಯ ಕೇಂದ್ರ\n\n"
            "1. ಪ್ರತಿಕ್ರಿಯೆ ಕಳುಹಿಸಲು, ನಿಮ್ಮ ಸಂದೇಶವನ್ನು ಟೈಪ್ ಮಾಡಿ ಅಥವಾ ಮಾಧ್ಯಮವನ್ನು ಕಳುಹಿಸಿ\n"
            "2. ಭಾಷೆಯನ್ನು ಬದಲಾಯಿಸಲು /language ಆಜ್ಞೆಯನ್ನು ಬಳಸಿರಿ\n"
            "3. ನಿಮ್ಮ ಮಾಹಿತಿಯನ್ನು ನೋಡಲು /user ಆಜ್ಞೆಯನ್ನು ಬಳಸಿರಿ\n\n"
            "ಸಮಸ್ಯೆಗಳಿದ್ದರೆ? @SkullModOwner ಅವರನ್ನು ಸಂಪರ್ಕಿಸಿ"
        )
    },
    "malayalam": {
        "welcome": "🇮🇳 സ്വാഗതം! നിങ്ങൾ ഇപ്പോൾ നിങ്ങളുടെ പ്രതികരണം അയയ്ക്കാം.",
        "full_welcome": (
            "🚀 SkullCheat പ്രതികരണം ബോട്ട് ലേക്ക് സ്വാഗതം!\n\n"
            "📢 ചാനൽ: @Skull_Cheats\n"
            "👤 ഡെവലപ്പർ: @SkullModOwner\n"
            "📤 സ്ക്രീൻഷോട്ടുകൾ അയയ്ക്കുക: @SkullCheat_FileBot\n\n"
            "⚠️ കുറിപ്പ്: പ്രതികരണം ഇല്ലാതെ നിങ്ങൾക്ക് ഏതെങ്കിലും കീ ലഭ്യമാകില്ല! 🔑"
        ),
        "user": "👤 ഉപയോക്തൃ ഡാഷ്‌ബോർഡ്\n\n🆔 ID: {user_id}\n🌐 ഭാഷ: {lang}\n🚫 നിരോധിതം: {banned}\n👥 മൊത്തം ഉപയോക്താക്കൾ: {total}",
        "banned": "🚫 നിങ്ങൾ നിരോധിതരായിരിക്കുന്നു. ഏതെങ്കിലും പ്രവർത്തനങ്ങൾ അനുവദനീയമല്ല.",
        "language_set": "✅ ഭാഷ ക്രമീകരിച്ചിരിക്കുന്നു!\n\n{message}",
        "unauthorized": "❌ അനുമതിയില്ല.",
        "ban_success": "🚫 ഉപയോക്താവ് {user_id} നിരോധിക്കപ്പെട്ടു.",
        "admin_reply_prefix": "💬 അഡ്മിൻ പ്രതികരണം:\n\n",
        "reply_success": "✅ സന്ദേശം വിജയകരമായി അയച്ചിരിക്കുന്നു!",
        "reply_failed": "❌ സന്ദേശം അയക്കുന്നതിൽ പരാജയപ്പെട്ടു.",
        "invalid_format": "⚠️ ഫോർമാറ്റ് പിന്തുണയില്ല.",
        "user_not_found": "⚠️ പ്രാഥമിക ഉപയോക്താവ് കണ്ടെത്തിയില്ല.",
        "reply_instructions": "❌ ദയവായി ഉപയോക്താവിന്റെ സന്ദേശത്തിന് മറുപടി നൽകുക.",
        "commands": (
            "📚 ലഭ്യമായ കമാൻഡുകൾ:\n\n"
            "🚀 /start - ബോട്ട് ആരംഭിക്കുക\n"
            "👤 /user - നിങ്ങളുടെ വിവരങ്ങൾ കാണിക്കുക\n"
            "🌐 /language - ഭാഷ മാറ്റുക\n"
            "📝 /feedback - പ്രതികരണം അയയ്ക്കുക\n"
            "❓ /help - സഹായം കാണിക്കുക\n\n"
            "🔨 അഡ്മിൻ കമാൻഡുകൾ:\n"
            "🚫 /ban <user_id> - ഉപയോക്താവിനെ നിരോധിക്കുക\n"
            "✅ /unban <user_id> - ഉപയോക്താവിന്റെ നിരോധനം പിൻവലിക്കുക\n"
            "📢 /broadcast - സന്ദേശം പ്രചരിക്കുക\n"
            "📜 /commands - എല്ലാ കമാൻഡുകളും കാണിക്കുക"
        ),
        "help": (
            "🆘 സഹായ കേന്ദ്രം\n\n"
            "1. പ്രതികരണം അയയ്ക്കാൻ, നിങ്ങളുടെ സന്ദേശം ടೈപ്പ് ചെയ്യുക അല്ലെങ്കിൽ മീഡിയ അയയ്ക്കുക\n"
            "2. ഭാഷ മാറ്റാൻ /language കമാൻഡ് ഉപയോഗിക്കുക\n"
            "3. നിങ്ങളുടെ വിവരങ്ങൾ കാണാൻ /user കമാൻഡ് ഉപയോഗിക്കുക\n\n"
            "പ്രശ്നങ്ങൾ ഉണ്ടോ? @SkullModOwner നെ ബന്ധപ്പെടുക"
        )
    },
}

# Supported languages for selection (code, label, emoji)
LANG_CHOICES = [
    ("hindi", "🇮🇳 Hindi"),
    ("bengali", "🇧🇩 Bengali"),
    ("telugu", "🇮🇳 Telugu"),
    ("marathi", "🇮🇳 Marathi"),
    ("tamil", "🇮🇳 Tamil"),
    ("gujarati", "🇮🇳 Gujarati"),
    ("kannada", "🇮🇳 Kannada"),
    ("malayalam", "🇮🇳 Malayalam"),
    ("english", "🇺🇸 English"),
    ("urdu", "🇵🇰 Urdu"),
    ("chinese", "🇨🇳 Chinese"),
    ("french", "🇫🇷 French"),
    ("spanish", "🇪🇸 Spanish"),
    ("turkish", "🇹🇷 Turkish"),
]

# -------------------- UTILITY FUNCTIONS --------------------
def get_user_language(user_id: str) -> str:
    """Get user's preferred language, default to English if not set."""
    return user_lang.get(user_id, "english")

def get_message(user_id: str, key: str, **kwargs: Any) -> str:
    """Get localized message for user."""
    lang = get_user_language(user_id)
    return LANGUAGES.get(lang, LANGUAGES["english"]).get(key, "").format(**kwargs)

def is_admin(user_id: str) -> bool:
    """Check if user is admin."""
    return user_id in ADMIN_IDS

def is_banned(user_id: str) -> bool:
    """Check if user is banned."""
    return user_id in banned_users

# -------------------- FILE DB UTILS --------------------
def ensure_file_db():
    if not os.path.exists(FILE_DB):
        with open(FILE_DB, "w") as f:
            json.dump({}, f)

def save_file(file_id, file_info):
    ensure_file_db()
    with open(FILE_DB, "r") as f:
        data = json.load(f)
    data[file_id] = file_info
    with open(FILE_DB, "w") as f:
        json.dump(data, f)

def get_file_info(file_id):
    ensure_file_db()
    with open(FILE_DB, "r") as f:
        data = json.load(f)
    return data.get(file_id)

# -------------------- FILE UPLOAD UTILS --------------------
# Ensure files.json exists
if not os.path.exists(FILES_DB):
    with open(FILES_DB, "w") as f:
        json.dump({}, f)

def save_uploaded_file(unique_id, file_info):
    with open(FILES_DB, "r") as f:
        data = json.load(f)
    data[unique_id] = file_info
    with open(FILES_DB, "w") as f:
        json.dump(data, f)

def get_uploaded_file(unique_id):
    with open(FILES_DB, "r") as f:
        data = json.load(f)
    return data.get(unique_id)

# -------------------- USER REGISTRATION & STATS --------------------
def register_user(user_id: str, lang: str = "english"):
    """Register a new user if not already registered."""
    if user_id not in user_lang:
        user_lang[user_id] = lang
        logger.info(f"Registered new user: {user_id} with lang: {lang}")

def get_total_users() -> int:
    return len(user_lang)

def get_banned_users() -> list:
    return list(banned_users)

def get_stats() -> dict:
    return {
        "total_users": get_total_users(),
        "banned_users": len(banned_users),
        "languages": {lang: list(user_lang.values()).count(lang) for lang in LANGUAGES.keys()}
    }

# -------------------- ADMIN: BAN, UNBAN, BROADCAST --------------------
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
                await context.bot.copy_message(chat_id=int(uid), from_chat_id=update.message.chat_id, message_id=msg.message_id)
            else:
            logger.warning(f"Broadcast to {uid} failed: {e}")
    await update.message.reply_text(get_message(admin_id, "broadcast_result", count=count, failed=failed))

# -------------------- ADMIN: STATS & BANLIST --------------------
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    admin_id = str(update.effective_user.id)
    if not is_admin(admin_id):
        await update.message.reply_text(get_message(admin_id, "unauthorized"))
        return
    stats = get_stats()
    msg = (
        f"📊 <b>Bot Stats</b>\n"
        f"👥 Total Users: <b>{stats['total_users']}</b>\n"
        f"🚫 Banned Users: <b>{stats['banned_users']}</b>\n"
        f"🌐 Languages: " + ", ".join([f"{k}: {v}" for k, v in stats['languages'].items()])
    )
    await update.message.reply_text(msg, parse_mode="HTML")

async def banlist_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    admin_id = str(update.effective_user.id)
    if not is_admin(admin_id):
        await update.message.reply_text(get_message(admin_id, "unauthorized"))
        return
    if not banned_users:
        await update.message.reply_text("✅ No users are currently banned.")
        return
    msg = "🚫 <b>Banned Users:</b>\n" + "\n".join(banned_users)
    await update.message.reply_text(msg, parse_mode="HTML")

# -------------------- ENHANCED USER HANDLERS --------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    register_user(user_id)
    if is_banned(user_id):
        await update.message.reply_text(get_message(user_id, "banned"))
        return

    # Build language keyboard dynamically
    keyboard = []
    row = []
    for idx, (code, label) in enumerate(LANG_CHOICES):
        row.append(InlineKeyboardButton(label, callback_data=f"lang_{code}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    await update.message.reply_text(
        "🌐 अपनी भाषा चुनें / Select Your Language:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )
    # After language selection, show command keyboard
    # (This will be triggered in language_selected)

async def language_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    lang = query.data.replace("lang_", "")
    user_lang[user_id] = lang
    welcome_msg = LANGUAGES.get(lang, LANGUAGES.get("english", {})).get("welcome", "Welcome!")
    full_welcome = LANGUAGES.get(lang, LANGUAGES.get("english", {})).get("full_welcome", "Welcome!")
    await query.edit_message_text(
        get_message(user_id, "language_set", message=welcome_msg),
        parse_mode="HTML"
    )
    await context.bot.send_message(
        chat_id=int(user_id),
        text=full_welcome,
        parse_mode="HTML",
        reply_markup=get_command_keyboard(user_id)
    )

async def change_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)

    if is_banned(user_id):
        await update.message.reply_text(get_message(user_id, "banned"))
        return

    await start(update, context)

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
    await update.message.reply_text(get_message(user_id, "help"), parse_mode="HTML")

async def feedback_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)

    if is_banned(user_id):
        await update.message.reply_text(get_message(user_id, "banned"))
        return

    await update.message.reply_text(get_message(user_id, "welcome"), parse_mode="HTML")

# -------------------- HANDLERS: MESSAGES --------------------
async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    user_id = str(user.id)
    register_user(user_id)
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
            await context.bot.send_photo(photo=msg.photo[-1].file_id, caption=prefix + (msg.caption or ""), **kwargs)
        elif msg.document:
            await context.bot.send_document(document=msg.document.file_id, caption=prefix + (msg.caption or ""), **kwargs)
        elif msg.video:
            await context.bot.send_video(video=msg.video.file_id, caption=prefix + (msg.caption or ""), **kwargs)
        elif msg.audio:
            await context.bot.send_audio(audio=msg.audio.file_id, caption=prefix + (msg.caption or ""), **kwargs)
        elif msg.voice:
            await context.bot.send_voice(voice=msg.voice.file_id, caption=prefix + (msg.caption or ""), **kwargs)
        elif msg.sticker:
            await context.bot.send_sticker(chat_id=user_id, sticker=msg.sticker.file_id)
        else:
            await update.message.reply_text(get_message(admin_id, "invalid_format"))
            return

        await update.message.reply_text(get_message(admin_id, "reply_success"))
    except Exception as e:
        logger.error(f"Reply Error: {e}")
        await update.message.reply_text(get_message(admin_id, "reply_failed"))

# -------------------- FILE SHARING SYSTEM (SIMPLE, ROBUST) --------------------
import json as _json
from uuid import uuid4 as _uuid4

FILES_DB = "files.json"

async def upload_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text("📤 Send me a file to upload (Max 500MB).")
        context.user_data['awaiting_upload'] = True
    except Exception as e:
        logger.error(f"/upload error: {e}")
        await update.message.reply_text("❌ Error: Could not start upload process.")

async def handle_file_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get('awaiting_upload'):
        return
    user_id = str(update.effective_user.id)
    file = update.message.document or update.message.video or update.message.audio or (update.message.photo[-1] if update.message.photo else None)
    if not file:
        await update.message.reply_text("❌ Unsupported file type.")
        context.user_data['awaiting_upload'] = False
        return
    if getattr(file, 'file_size', 0) > 500 * 1024 * 1024:
        await update.message.reply_text("❌ File too large! Max 500MB.")
        context.user_data['awaiting_upload'] = False
        return
    file_id = file.file_id
    file_name = getattr(file, 'file_name', 'Unnamed')
    file_type = 'photo' if update.message.photo else (
        'document' if update.message.document else (
            'video' if update.message.video else (
                'audio' if update.message.audio else 'unknown')))
    unique_id = str(_uuid4())[:10]
    # Load existing data
    try:
        if os.path.exists(FILES_DB):
            with open(FILES_DB, "r") as f:
                data = _json.load(f)
        else:
            data = {}
        # Save file info
        data[unique_id] = {
            "file_id": file_id,
            "file_name": file_name,
            "file_type": file_type,
            "uploader_id": user_id
        }
        with open(FILES_DB, "w") as f:
            _json.dump(data, f, indent=2)
        bot_username = (await context.bot.get_me()).username
        link = f"https://t.me/{bot_username}?start=file_{unique_id}"
        logger.info(f"File uploaded: {file_id} by {user_id}, link: {link}")
        await update.message.reply_text(f"✅ Your file is saved.\n🔗 Share this link:\n{link}")
    except Exception as e:
        logger.error(f"File upload error: {e}")
        await update.message.reply_text("❌ Error: Could not save file or generate link.")
    context.user_data['awaiting_upload'] = False

async def extended_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if args and args[0].startswith("file_"):
        file_key = args[0][5:]
        if os.path.exists(FILES_DB):
            with open(FILES_DB, "r") as f:
                data = _json.load(f)
            file_info = data.get(file_key)
            if file_info:
                try:
                    if file_info["file_type"] == "photo":
                        await context.bot.send_photo(update.effective_chat.id, photo=file_info["file_id"])
                    elif file_info["file_type"] == "video":
                        await context.bot.send_video(update.effective_chat.id, video=file_info["file_id"], caption=file_info["file_name"])
                    elif file_info["file_type"] == "audio":
                        await context.bot.send_audio(update.effective_chat.id, audio=file_info["file_id"], caption=file_info["file_name"])
                    else:
                        await context.bot.send_document(update.effective_chat.id, document=file_info["file_id"], filename=file_info["file_name"])
                    return
                except Exception as e:
                    await update.message.reply_text(f"❌ Error sending file: {e}")
                    return
        await update.message.reply_text("❌ File not found or link expired.")
    else:
        await start(update, context)

# --- FUN & UTILITY COMMANDS ---

async def myfiles_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if not os.path.exists(FILES_DB):
        await update.message.reply_text("You have not uploaded any files yet.")
        return
    with open(FILES_DB, "r") as f:
        data = _json.load(f)
    user_files = [(k, v) for k, v in data.items() if v.get("uploader_id") == user_id]
    if not user_files:
        await update.message.reply_text("You have not uploaded any files yet.")
        return
    bot_username = (await context.bot.get_me()).username
    msg = "\n".join([
        f"{i+1}. {v['file_name']} ({v['file_type']})\n🔗 https://t.me/{bot_username}?start=file_{k}"
        for i, (k, v) in enumerate(user_files)
    ])
    await update.message.reply_text(f"Your files:\n{msg}")

async def randomfile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not os.path.exists(FILES_DB):
        await update.message.reply_text("No files in the database yet.")
        return
    with open(FILES_DB, "r") as f:
        data = _json.load(f)
    if not data:
        await update.message.reply_text("No files in the database yet.")
        return
    k, v = random.choice(list(data.items()))
    bot_username = (await context.bot.get_me()).username
    link = f"https://t.me/{bot_username}?start=file_{k}"
    await update.message.reply_text(f"Random file: {v['file_name']} ({v['file_type']})\n🔗 {link}")

async def deletefile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /deletefile <file_id>")
        return
    file_id = args[0]
    if not os.path.exists(FILES_DB):
        await update.message.reply_text("No files found.")
        return
    with open(FILES_DB, "r") as f:
        data = _json.load(f)
    file_info = data.get(file_id)
    if not file_info:
        await update.message.reply_text("File not found.")
        return
    if file_info.get("uploader_id") != user_id:
        await update.message.reply_text("You can only delete your own files.")
        return
    del data[file_id]
    with open(FILES_DB, "w") as f:
        _json.dump(data, f, indent=2)
    await update.message.reply_text("File deleted successfully.")

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 <b>SkullCheat FileBot</b>\nCreated by @SkullModOwner\nUpload, share, and manage files easily!\nEnjoy!",
        parse_mode="HTML"
    )

async def fileinfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /fileinfo <file_id>")
        return
    file_id = args[0]
    if not os.path.exists(FILES_DB):
        await update.message.reply_text("No files found.")
        return
    with open(FILES_DB, "r") as f:
        data = _json.load(f)
    file_info = data.get(file_id)
    if not file_info:
        await update.message.reply_text("File not found.")
        return
    msg = f"<b>File Info</b>\nName: {file_info['file_name']}\nType: {file_info['file_type']}\nUploader: {file_info['uploader_id']}\nID: {file_id}"
    await update.message.reply_text(msg, parse_mode="HTML")

async def commands_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    # 1. Detect user language (default to 'en')
    lang_code = get_user_language(user_id)
    lang_file = f"lang/{lang_code[:2]}.json"
    if not os.path.exists(lang_file):
        lang_file = "lang/en.json"
    try:
        with open(lang_file, "r") as f:
            lang_data = json.load(f)
    except Exception:
        with open("lang/en.json", "r") as f:
            lang_data = json.load(f)
    # Fallback for missing keys
    def get_cmd(key, subkey):
        try:
            return lang_data["commands"][key][subkey]
        except Exception:
            with open("lang/en.json", "r") as f:
                en_data = json.load(f)
            return en_data["commands"].get(key, {}).get(subkey, f"/{key}")
    def get_section(section):
        try:
            return lang_data["sections"][section]
        except Exception:
            with open("lang/en.json", "r") as f:
                en_data = json.load(f)
            return en_data["sections"].get(section, section.title())
    # 2. Command groupings
    user_cmds = [
        "start", "help", "about", "user", "language", "feedback", "commands"
    ]
    file_cmds = [
        "upload", "myfiles", "randomfile", "deletefile", "fileinfo"
    ]
    admin_cmds = [
        "ban", "unban", "broadcast", "stats", "banlist"
    ]
    # 3. Build message
    msg = "<b>" + get_section("user") + "</b>\n"
    for cmd in user_cmds:
        msg += f"{get_cmd(cmd, 'label')} - {get_cmd(cmd, 'desc')}\n"
    msg += "\n<b>" + get_section("file") + "</b>\n"
    for cmd in file_cmds:
        msg += f"{get_cmd(cmd, 'label')} - {get_cmd(cmd, 'desc')}\n"
    if is_admin(user_id):
        msg += "\n<b>" + get_section("admin") + "</b>\n"
        for cmd in admin_cmds:
            msg += f"{get_cmd(cmd, 'label')} - {get_cmd(cmd, 'desc')}\n"
    await update.message.reply_text(msg, parse_mode="HTML")

# Utility to get localized command labels for keyboard
COMMON_COMMANDS = ["commands", "help", "language", "about"]
def get_command_keyboard(user_id: str):
    lang_code = get_user_language(user_id)
    lang_file = f"lang/{lang_code[:2]}.json"
    if not os.path.exists(lang_file):
        lang_file = "lang/en.json"
    try:
        with open(lang_file, "r") as f:
            lang_data = json.load(f)
    except Exception:
        with open("lang/en.json", "r") as f:
            lang_data = json.load(f)
    row = [lang_data["commands"].get(cmd, {}).get("label", f"/{cmd}") for cmd in COMMON_COMMANDS]
    return ReplyKeyboardMarkup([row], resize_keyboard=True)

# -------------------- MAIN FUNCTION --------------------
def main() -> None:
    application = ApplicationBuilder().token(TOKEN).build()

    # File upload handlers
    application.add_handler(CommandHandler("upload", upload_command))

    # Start handler (with file sharing)
    application.add_handler(CommandHandler("start", extended_start))

    # User commands
    application.add_handler(CommandHandler("user", user_dashboard))
    application.add_handler(CommandHandler("language", change_language))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("feedback", feedback_command))
    application.add_handler(CommandHandler("commands", commands_command))  # Add new

    # Admin commands
    application.add_handler(CommandHandler("ban", ban_user))
    application.add_handler(CommandHandler("unban", unban_user))
    application.add_handler(CommandHandler("broadcast", broadcast))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("banlist", banlist_command))

    # Fun & utility commands
    application.add_handler(CommandHandler("myfiles", myfiles_command))
    application.add_handler(CommandHandler("randomfile", randomfile_command))
    application.add_handler(CommandHandler("deletefile", deletefile_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(CommandHandler("fileinfo", fileinfo_command))

    # Callback for language selection
    application.add_handler(CallbackQueryHandler(language_selected, pattern="^lang_"))

    # Message handlers
    application.add_handler(MessageHandler(filters.ChatType.PRIVATE & (filters.Document.ALL | filters.VIDEO | filters.AUDIO), handle_file_upload))
    application.add_handler(MessageHandler(filters.ChatType.PRIVATE & filters.REPLY, handle_admin_reply))
    application.add_handler(MessageHandler(filters.ChatType.PRIVATE & ~filters.COMMAND, handle_user_message))

    # Start the Bot
    application.run_polling()
    logger.info("Bot started and running...")

if __name__ == "__main__":
    main()
