import logging
import pymongo
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.error import TelegramError
from typing import Set, Dict

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot configuration
BOT_TOKEN = '7679605071:AAFVQ2VNf5q-Ce0ev5YGDYj7H_Y6SB2gEQA'
ADMIN_ID = 6490401448

# Initialize channels list
REQUIRED_CHANNELS = []

# MongoDB connection
MONGO_URI = "mongodb+srv://giftcodebot:giftcodebotpass@giftcodebot.n3wkcog.mongodb.net/?retryWrites=true&w=majority&appName=giftcodebot"
client = pymongo.MongoClient(MONGO_URI)
db = client["giftcodebot"]
users_collection = db["users"]
codes_collection = db["codes"]


# Load data from MongoDB
def load_data() -> tuple[Set[int], Set[int], dict]:
    stored_data = users_collection.find_one({"_id": "user_data"}) or {"users": [], "blocked": []}
    stored_codes = codes_collection.find_one({"_id": "codes"}) or {"diuwin": "ECC19E1117D561A6769EF3245F01F5C4", "jalwa": "ECC19E1117D561A6769EF3245F01F5C4"}
    stored_channels = codes_collection.find_one({"_id": "channels"}) or {"channels": []}

    user_data = set(stored_data.get("users", []))
    blocked_users = set(stored_data.get("blocked", []))

    global REQUIRED_CHANNELS
    REQUIRED_CHANNELS = stored_channels.get("channels", [1002629702845,1002436175379,1002125928281])

    return user_data, blocked_users, stored_codes

user_data, blocked_users, codes = load_data()
user_codes = {}

def get_channel_link(channel):
    try:
        return f"https://t.me/joinchat/{channel}" #assuming these are now just channel IDs
    except:
        return "Unknown"

def check_channels_membership(user_id, context):
    try:
        for channel in REQUIRED_CHANNELS:
            try:
                logger.info(f"Checking membership for user {user_id} in channel {channel}")
                member = context.bot.get_chat_member(chat_id=channel, user_id=user_id)
                if member.status not in ['member', 'administrator', 'creator']:
                    logger.info(f"User {user_id} is not a member of {channel} (status: {member.status})")
                    return False
                logger.info(f"User {user_id} is a member of {channel} (status: {member.status})")
            except TelegramError as e:
                logger.error(f"Error checking membership for channel {channel}: {str(e)}")
                return False
        logger.info(f"User {user_id} is a member of all channels")
        return True
    except Exception as e:
        logger.error(f"Unexpected error in membership check: {str(e)}")
        return False

def start(update: Update, context: CallbackContext):
    user = update.effective_user
    user_data.add(user.id)
    # Save user data to MongoDB
    users_collection.update_one({"_id": "user_data"}, {"$set": {"users": list(user_data)}}, upsert=True)

    welcome_message = (
        "ᴀʟʟ ᴄᴏʟᴏᴜʀ ᴛʀᴀᴅɪɴɢ ₹100-500 ʙɪɢ ɢɪꜰᴛ ᴄᴏᴅᴇ ᴀᴠᴀɪʟᴀʙʟᴇ ɪɴ ʙᴏᴛ 📬🗒\n\n"
        "🎁 ᴊᴜꜱᴛ ᴊᴏɪɴ ᴀʟʟ ᴄʜᴀɴɴᴇʟ ᴀɴᴅ ᴄʟᴀɪᴍ ᴀʟʟ ꜱɪᴛᴇꜱ ᴄᴏᴅᴇ 🚚"
    )

    # Create buttons for all required channels
    keyboard = []
    for i, channel in enumerate(REQUIRED_CHANNELS, 1):
        try:
            chat = context.bot.get_chat(channel)
            invite_link = chat.invite_link or f"https://t.me/joinchat/{channel}"
            keyboard.append([InlineKeyboardButton(f"Join Channel {i}", url=invite_link)])
        except TelegramError:
            keyboard.append([InlineKeyboardButton(f"Join Channel {i}", url=f"https://t.me/joinchat/{channel}")])

    keyboard.append([InlineKeyboardButton("✅ Joined", callback_data="joined")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_photo(
            chat_id=user.id,
            photo="https://imgur.com/a/bOmGGVT",
            caption=welcome_message,
            reply_markup=reply_markup
        )

def join_button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    user = update.effective_user
    query.answer()

    # Delete the previous message
    if query.message:
        query.message.delete()

    if check_channels_membership(user.id, context):
        keyboard = [
            [
                InlineKeyboardButton("Diuwin", callback_data="diuwin"),
                InlineKeyboardButton("Jalwa Game", callback_data="jalwa")
            ],
            [
                InlineKeyboardButton("Tashan Win", callback_data="tashan")
            ],
            [
                InlineKeyboardButton("NUMBER HACK", callback_data="number_hack")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        try:
            context.bot.send_message(
                chat_id=user.id,
                text="*🟢 Choose Desire App To Claim 🟢*\n\n"
                     "*🎁 Claim Big Promo Codes And Get Upto ₹1 ~ ₹999 Random Amount !!*\n\n"
                     "*🎁 Must Active In All Channels To Get Daily Big Earning Promo Codes ✓✓*\n\n"
                     "*⚠️ Warning : Expired gift code will refresh in a few hours ⏰ Please wait patiently 🔐!!*",
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )
            logger.info(f"Sent app choice menu to user {user.id}")
        except TelegramError as e:
            logger.error(f"Failed to send message: {e}")
    else:
        try:
            context.bot.send_message(
                chat_id=user.id,
                text="😡 *Gaddari karbe Dust Manab!*\n\nJoin the channel and then click ✅ *Joined*.",
                parse_mode=ParseMode.MARKDOWN
            )
        except TelegramError as e:
            logger.error(f"Failed to notify join: {e}")

def code(update: Update, context: CallbackContext):
    user = update.effective_user
    if user.id in user_codes:
        update.message.reply_text(
            f"Your code is: {user_codes[user.id]}",
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        update.message.reply_text(
            "You haven't received a code yet. Please use /start to join the channel and get your code."
        )

def stats(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        update.message.reply_text("❌ You are not authorized to use this command.")
        return

    active_users = len(user_data) - len(blocked_users)
    update.message.reply_text(
        f"📊 Bot Statistics:\n"
        f"👥 Total Users: {len(user_data)}\n"
        f"🚫 Blocked Users: {len(blocked_users)}\n"
        f"✅ Active Users: {active_users}"
    )

def handle_app_buttons(update: Update, context: CallbackContext):
    query = update.callback_query
    user = update.effective_user
    query.answer()

    # Delete the previous message
    if query.message:
        query.message.delete()

    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        if query.data == "diuwin":
            promo_message = (
                "*ᴄʟᴀɪᴍ ᴅɪᴜᴡɪɴ ɢɪꜰᴛ ᴄᴏᴅᴇ 🤞💚*\n\n"
                f"*ɢɪꜰᴛ ᴄᴏᴅᴇ* 👉 `{codes['diuwin']}`\n\n"
                "*✅ ᴏꜰꜰɪᴄɪᴀʟ ʀᴇɢɪꜱᴛᴇʀ ʟɪɴᴋ ::* *https://www.6diuwin.com/#/register?invitationCode=328149554356*\n\n"
                "*⚠️ ᴍᴜꜱᴛ ʀᴇɢɪꜱᴛᴇʀ ᴜɴᴅᴇʀ ᴏꜰꜰɪᴄɪᴀʟ ʀᴇɢɪꜱᴛᴇʀ ʟɪɴᴋ ᴛᴏ ᴄʟᴀɪᴍ ɢɪꜰᴛ ᴄᴏᴅᴇ 🎁*"
            )
            context.bot.send_photo(
                    chat_id=user.id,
                    photo="https://imgur.com/noB4wOy",
                    caption=promo_message,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup
                )
        elif query.data == "jalwa":
            promo_message = (
                "*ᴄʟᴀɪᴍ ᴊᴀʟᴡᴀ ɢᴀᴍᴇ ɢɪꜰᴛ ᴄᴏᴅᴇ 🤞💙*\n\n"
                f"*ɢɪꜰᴛ ᴄᴏᴅᴇ* 👉 `{codes['jalwa']}`\n\n"
                "*✅ ᴏꜰꜰɪᴄɪᴀʟ ʀᴇɢɪꜱᴛᴇʀ ʟɪɴᴋ ::* *https://www.jalwa.live/#/register?invitationCode=78831216537*\n\n"
                "*⚠️ ᴍᴜꜱᴛ ʀᴇɢɪꜱᴛᴇʀ ᴜɴᴅᴇʀ ᴏꜰꜰɪᴄɪᴀʟ ʀᴇɢɪꜱᴛᴇʀ ʟɪɴᴋ ᴛᴏ ᴄʟᴀɪᴍ ɢɪꜰᴛ ᴄᴏᴅᴇ 🎁*"
            )
            context.bot.send_photo(
                    chat_id=user.id,
                    photo="https://imgur.com/a/yAPsd4R",
                    caption=promo_message,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup
                )
        elif query.data == "tashan":
            promo_message = (
                "*ᴄʟᴀɪᴍ ᴛᴀꜱʜᴀɴ ᴡɪɴ ɢɪꜰᴛ ᴄᴏᴅᴇ 🤞🤎*\n\n"
                f"*ɢɪꜰᴛ ᴄᴏᴅᴇ* 👉 `{codes.get('tashan', 'E13C37DF85131FACFECD5FAC28AD073E')}`\n\n"
                "*✅ ᴏꜰꜰɪᴄɪᴀʟ ʀᴇɢɪꜱᴛᴇʀ ʟɪɴᴋ ::* *https://www.tashanwin.net/#/register?invitationCode=48588452704*\n\n"
                "*⚠️ ᴍᴜꜱᴛ ʀᴇɢɪꜱᴛᴇʀ ᴜɴᴅᴇʀ ᴏꜰꜰɪᴄɪᴀʟ ʀᴇɢɪꜱᴛᴇʀ ʟɪɴᴋ ᴛᴏ ᴄʟᴀɪᴍ ɢɪꜰᴛ ᴄᴏᴅᴇ 🎁*"
            )
            context.bot.send_photo(
                    chat_id=user.id,
                    photo="https://imgur.com/a/3jccMyT",
                    caption=promo_message,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup
                )
        elif query.data == "number_hack":
            try:
                # Forward the file from your channel
                context.bot.copy_message(
                    chat_id=user.id,
                    from_chat_id=-1002589441318,
                    message_id=7,
                    reply_markup=reply_markup,
                    caption=(
                        "🎯 *VIP NUMBER HACK APK*\n\n"
                        "💯 *100% NUMBER PREDICTION ✓*\n"
                        "💯 *100% WORKING HACK ✓*\n\n"
                    ),
                    parse_mode=ParseMode.MARKDOWN
                )
            except TelegramError as e:
                logger.error(f"Failed to forward file: {e}")
                context.bot.send_message(
                    chat_id=user.id,
                    text="Sorry, there was an error. Please try again later.",
                    reply_markup=reply_markup
                )
        elif query.data == "back":
            try:
                # Delete all previous messages in the chat
                message_id = query.message.message_id
                for i in range(message_id, message_id - 5, -1):  # Try to delete last 5 messages
                    try:
                        context.bot.delete_message(chat_id=user.id, message_id=i)
                    except TelegramError:
                        pass

            except TelegramError:
                pass

            # Show app selection buttons again
            keyboard = [
                [
                    InlineKeyboardButton("Diuwin", callback_data="diuwin"),
                    InlineKeyboardButton("Jalwa Game", callback_data="jalwa")
                ],
                [
                    InlineKeyboardButton("Tashan Win", callback_data="tashan")
                ],
                [
                    InlineKeyboardButton("NUMBER HACK", callback_data="number_hack")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            context.bot.send_message(
                chat_id=user.id,
                text="*🟢 Choose Desire App To Claim 🟢*\n\n"
                     "*🎁 Claim Big Promo Codes And Get Upto ₹1 ~ ₹999 Random Amount !!*\n\n"
                     "*🎁 Must Active In All Channels To Get Daily Big Earning Promo Codes ✓✓*\n\n"
                     "*⚠️ Warning : Expired gift code will refresh in a few hours ⏰ Please wait patiently 🔐!!*",
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )
    except TelegramError as e:
        logger.error(f"Failed to send app message: {e}")

def error_handler(update: Update, context: CallbackContext):
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def cast(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        update.message.reply_text("❌ You are not authorized to use this command.")
        return

    message = ' '.join(context.args)
    if not message:
        update.message.reply_text("Please provide a message to broadcast.")
        return

    success = 0
    failed = 0
    for user_id in user_data:
        try:
            context.bot.send_message(chat_id=user_id, text=message, parse_mode=ParseMode.MARKDOWN)
            success += 1
        except TelegramError:
            failed += 1
            blocked_users.add(user_id)
    #Save changes to mongodb
    users_collection.update_one({"_id": "user_data"}, {"$set": {"users": list(user_data), "blocked": list(blocked_users)}}, upsert=True)

    update.message.reply_text(f"Broadcast completed!\nSuccess: {success}\nFailed: {failed}")

def set_jalwa_code(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        update.message.reply_text("❌ You are not authorized to use this command.")
        return

    if not context.args:
        update.message.reply_text("Please provide the new Jalwa game code.")
        return

    codes['jalwa'] = context.args[0]
    codes_collection.update_one({"_id": "codes"}, {"$set": codes}, upsert=True)
    update.message.reply_text(f"Jalwa game code updated to: {codes['jalwa']}")

def set_diuwin_code(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        update.message.reply_text("❌ You are not authorized to use this command.")
        return

    if not context.args:
        update.message.reply_text("Please provide the new Diuwin code.")
        return

    codes['diuwin'] = context.args[0]
    codes_collection.update_one({"_id": "codes"}, {"$set": codes}, upsert=True)
    update.message.reply_text(f"Diuwin code updated to: {codes['diuwin']}")

def set_tashan_code(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        update.message.reply_text("❌ You are not authorized to use this command.")
        return

    if not context.args:
        update.message.reply_text("Please provide the new Tashan Win code.")
        return

    codes['tashan'] = context.args[0]
    codes_collection.update_one({"_id": "codes"}, {"$set": codes}, upsert=True)
    update.message.reply_text(f"Tashan Win code updated to: {codes['tashan']}")

def set_channel(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        update.message.reply_text("❌ You are not authorized to use this command.")
        return

    if not context.args:
        update.message.reply_text("Please provide channel username or invite link.")
        return

    channel_input = context.args[0]
    
    try:
        # Handle different channel input formats
        if channel_input.startswith('https://t.me/'):
            if '/+' in channel_input or '/joinchat/' in channel_input:
                # Private channel
                channel_id = channel_input.split('/')[-1]
                try:
                    chat = context.bot.get_chat(channel_input)
                    channel_id = chat.id
                except:
                    update.message.reply_text("Invalid channel link or bot is not admin in the channel.")
                    return
            else:
                # Public channel
                username = channel_input.split('/')[-1]
                try:
                    chat = context.bot.get_chat('@' + username)
                    channel_id = chat.id
                except:
                    update.message.reply_text("Invalid channel username or bot is not admin in the channel.")
                    return
        elif channel_input.startswith('@'):
            try:
                chat = context.bot.get_chat(channel_input)
                channel_id = chat.id
            except:
                update.message.reply_text("Invalid channel username or bot is not admin in the channel.")
                return
        else:
            try:
                # Try as channel ID
                channel_id = int(channel_input)
                chat = context.bot.get_chat(channel_id)
            except:
                update.message.reply_text("Invalid channel format. Use channel username, invite link, or ID.")
                return

        global REQUIRED_CHANNELS
        if len(REQUIRED_CHANNELS) >= 12:
            update.message.reply_text("Maximum limit of 12 channels reached!")
            return

        if channel_id not in REQUIRED_CHANNELS:
            REQUIRED_CHANNELS.append(channel_id)
            # Update MongoDB
            try:
                codes_collection.update_one(
                    {"_id": "channels"},
                    {"$set": {"channels": REQUIRED_CHANNELS}},
                    upsert=True
                )
                # Get channel information
                invite_link = chat.invite_link or f"https://t.me/joinchat/{channel_id}"
                update.message.reply_text(
                    f"✅ Added channel {len(REQUIRED_CHANNELS)}: {chat.title}\n"
                    f"Channel ID: {channel_id}\n"
                    f"Invite Link: {invite_link}\n"
                    f"Total channels: {len(REQUIRED_CHANNELS)}"
                )
            except Exception as e:
                update.message.reply_text(f"Error updating database: {str(e)}")
        else:
            update.message.reply_text("This channel is already in the list!")
    except Exception as e:
        update.message.reply_text(f"An error occurred: {str(e)}")

def remove_channel(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        update.message.reply_text("❌ You are not authorized to use this command.")
        return

    if not context.args:
        update.message.reply_text("Please provide channel ID or 'channel NUMBER' to remove.")
        return

    global REQUIRED_CHANNELS

    # Handle removal by channel number
    if len(context.args) == 2 and context.args[0].lower() == 'channel':
        try:
            channel_num = int(context.args[1])
            if 1 <= channel_num <= len(REQUIRED_CHANNELS):
                removed_channel = REQUIRED_CHANNELS.pop(channel_num - 1)
                # Update MongoDB
                try:
                    codes_collection.update_one(
                        {"_id": "channels"},
                        {"$set": {"channels": REQUIRED_CHANNELS}},
                        upsert=True
                    )
                    update.message.reply_text(
                        f"✅ Successfully removed channel {channel_num}: {removed_channel}\n"
                        f"Total channels: {len(REQUIRED_CHANNELS)}"
                    )
                except Exception as e:
                    update.message.reply_text(f"Error updating database: {str(e)}")
            else:
                update.message.reply_text(f"Invalid channel number. Please use 1 to {len(REQUIRED_CHANNELS)}")
            return
        except ValueError:
            update.message.reply_text("Invalid channel number format")
            return

    # Handle removal by channel ID
    try:
        channel = int(context.args[0])  # Convert to integer since we're using channel IDs
        if channel in REQUIRED_CHANNELS:
            REQUIRED_CHANNELS.remove(channel)
            # Update MongoDB
            try:
                codes_collection.update_one(
                    {"_id": "channels"},
                    {"$set": {"channels": REQUIRED_CHANNELS}},
                    upsert=True
                )
                update.message.reply_text(
                    f"✅ Successfully removed channel: {channel}\n"
                    f"Total channels: {len(REQUIRED_CHANNELS)}"
                )
            except Exception as e:
                update.message.reply_text(f"Error updating database: {str(e)}")
        else:
            update.message.reply_text(f"Channel {channel} not found in required channels list")
    except ValueError:
        update.message.reply_text("Please provide a valid channel ID (numbers only)")



def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Add error handler
    dp.add_error_handler(error_handler)

    dp.add_handler(CommandHandler("start", start, run_async=True))
    dp.add_handler(CommandHandler("stats", stats))
    dp.add_handler(CommandHandler("code", code))
    dp.add_handler(CommandHandler("cast", cast))
    dp.add_handler(CommandHandler("setjalwagame", set_jalwa_code))
    dp.add_handler(CommandHandler("setdiuwin", set_diuwin_code))
    dp.add_handler(CommandHandler("settashanwin", set_tashan_code))
    dp.add_handler(CommandHandler("set_channel", set_channel))
    dp.add_handler(CommandHandler("removechannel", remove_channel))
    dp.add_handler(CallbackQueryHandler(join_button_callback, pattern="joined"))
    dp.add_handler(CallbackQueryHandler(handle_app_buttons, pattern="^(diuwin|jalwa|tashan|back|number_hack)$"))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
