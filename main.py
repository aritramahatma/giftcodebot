import logging
import pymongo
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.error import TelegramError

# Bot Token and MongoDB URL
BOT_TOKEN = '7679605071:AAFVQ2VNf5q-Ce0ev5YGDYj7H_Y6SB2gEQA'
MONGO_URI = "mongodb+srv://giftcodebot:giftcodebotpass@giftcodebot.n3wkcog.mongodb.net/?retryWrites=true&w=majority&appName=giftcodebot"

# Admin ID
ADMIN_ID = 6490401448

# Channel IDs to check join
REQUIRED_CHANNELS = [-1002629702845, -1002436175379, -1002125928281]

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB Setup
client = pymongo.MongoClient(MONGO_URI)
db = client["giftcodebot"]
users_col = db["users"]
codes_col = db["codes"]

# Load User Data
def load_data():
    user_data = users_col.find_one({"_id": "user_data"}) or {"users": [], "blocked": []}
    code_data = codes_col.find_one({"_id": "codes"}) or {"diuwin": "default1", "jalwa": "default2"}
    return set(user_data.get("users", [])), set(user_data.get("blocked", [])), code_data

user_data, blocked_users, codes = load_data()

# Check if user joined channels
def is_user_joined(user_id, context):
    try:
        for channel_id in REQUIRED_CHANNELS:
            member = context.bot.get_chat_member(chat_id=channel_id, user_id=user_id)
            if member.status not in ['member', 'administrator', 'creator']:
                return False
        return True
    except:
        return False

# Start Command
def start(update: Update, context: CallbackContext):
    user = update.effective_user
    user_data.add(user.id)
    users_col.update_one({"_id": "user_data"}, {"$set": {"users": list(user_data)}}, upsert=True)

    keyboard = []
    for idx, ch_id in enumerate(REQUIRED_CHANNELS, 1):
        try:
            chat = context.bot.get_chat(ch_id)
            invite_link = chat.invite_link if chat.invite_link else f"https://t.me/c/{str(ch_id)[4:]}"
            keyboard.append([InlineKeyboardButton(f"Join Channel {idx}", url=invite_link)])
        except:
            pass

    keyboard.append([InlineKeyboardButton("✅ Joined", callback_data="joined")])

    update.message.reply_text(
        "ᴀʟʟ ᴄᴏʟᴏᴜʀ ᴛʀᴀᴅɪɴɢ ₹100-500 ʙɪɢ ɢɪꜰᴛ ᴄᴏᴅᴇ ᴀᴠᴀɪʟᴀʙʟᴇ ɪɴ ʙᴏᴛ 📬🗒\n\n🎁 ᴊᴜꜱᴛ ᴊᴏɪɴ ᴀʟʟ ᴄʜᴀɴɴᴇʟꜱ ᴀɴᴅ ᴄʟᴀɪᴍ ᴀʟʟ ꜱɪᴛᴇꜱ ᴄᴏᴅᴇ 🚚",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Joined Button
def joined_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()

    if is_user_joined(user_id, context):
        buttons = [
            [InlineKeyboardButton("Diuwin", callback_data="diuwin"), InlineKeyboardButton("Jalwa Game", callback_data="jalwa")],
            [InlineKeyboardButton("Tashan Win", callback_data="tashan")],
            [InlineKeyboardButton("NUMBER HACK", callback_data="number_hack")]
        ]
        context.bot.send_message(
            chat_id=user_id,
            text="*🟢 Choose Desire App To Claim 🟢*",
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        context.bot.send_message(
            chat_id=user_id,
            text="😡 *Gaddari karbe Dust Manab!*\n\nJoin the channel and then click ✅ *Joined*.",
            parse_mode=ParseMode.MARKDOWN
        )

# Button Handler (Diuwin/Jalwa etc)
def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    query.answer()

    if query.message:
        query.message.delete()

    if data == "diuwin":
        context.bot.send_photo(
            chat_id=user_id,
            photo="https://imgur.com/noB4wOy.png",
            caption=f"*ɢɪꜰᴛ ᴄᴏᴅᴇ* 👉 `{codes.get('diuwin', 'NO_CODE')}`\n\n[Register Here](https://www.6diuwin.com/#/register?invitationCode=328149554356)",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back")]])
        )
    elif data == "jalwa":
        context.bot.send_photo(
            chat_id=user_id,
            photo="https://imgur.com/a/yAPsd4R.png",
            caption=f"*ɢɪꜰᴛ ᴄᴏᴅᴇ* 👉 `{codes.get('jalwa', 'NO_CODE')}`\n\n[Register Here](https://www.jalwa.live/#/register?invitationCode=78831216537)",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back")]])
        )
    elif data == "tashan":
        context.bot.send_photo(
            chat_id=user_id,
            photo="https://imgur.com/a/3jccMyT.png",
            caption=f"*ɢɪꜰᴛ ᴄᴏᴅᴇ* 👉 `{codes.get('tashan', 'NO_CODE')}`\n\n[Register Here](https://www.tashanwin.net/#/register?invitationCode=48588452704)",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back")]])
        )
    elif data == "number_hack":
        context.bot.send_message(
            chat_id=user_id,
            text="🎯 *VIP NUMBER HACK APK*\n\n💯 *100% Prediction ✓*\n💯 *100% Working*",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back")]])
        )
    elif data == "back":
        joined_callback(update, context)

# /stats command
def stats(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        return
    active = len(user_data) - len(blocked_users)
    update.message.reply_text(
        f"📊 Bot Statistics:\n👥 Total Users: {len(user_data)}\n🚫 Blocked Users: {len(blocked_users)}\n✅ Active Users: {active}"
    )

# /cast command
def cast(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        return
    message = ' '.join(context.args)
    if not message:
        update.message.reply_text("❌ Please provide message to broadcast.")
        return

    sent = 0
    fail = 0
    for uid in list(user_data):
        try:
            context.bot.send_message(chat_id=uid, text=message, parse_mode=ParseMode.MARKDOWN)
            sent += 1
        except:
            blocked_users.add(uid)
            fail += 1

    users_col.update_one({"_id": "user_data"}, {"$set": {"users": list(user_data), "blocked": list(blocked_users)}}, upsert=True)
    update.message.reply_text(f"✅ Broadcast Done!\nSent: {sent}\nFailed: {fail}")

# Error Handler
def error(update, context):
    logger.warning(f'Update {update} caused error {context.error}')

# Main
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("stats", stats))
    dp.add_handler(CommandHandler("cast", cast))
    dp.add_handler(CallbackQueryHandler(joined_callback, pattern="^joined$"))
    dp.add_handler(CallbackQueryHandler(button_handler))
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
