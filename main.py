#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.
First, a few handler functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

from data import db_session
from data.voices import Voice
from data.rate import Rate
import logging
from config import *
from telegram import ForceReply, Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, \
    ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, CallbackQueryHandler, Filters
import random

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)
like = '\U0001F44D'
dislike = '\U0001F44E'
keyboard = [

    [
        KeyboardButton('/Add_voices'),
        KeyboardButton('/Listen_to_voices'),
    ]
]
reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

inline_keyboard = [
    [
        InlineKeyboardButton(like, callback_data=1),
        InlineKeyboardButton(dislike, callback_data=-1),
    ]
]
inline_reply_markup = InlineKeyboardMarkup(inline_keyboard)


# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, context: CallbackContext) -> None:
    context.chat_data["what_do"] = 0
    """Send a message when the command /start is issued."""

    user = update.effective_user
    update.message.reply_html(
        rf"""Hi {user.mention_html()}!
        This is an audiotiktok bot, listen to random voices and rate them.""",
        reply_markup=reply_markup
    )


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text("Help!")


def voiceanalysis(update: Update, context: CallbackContext) -> None:
    if context.chat_data["what_do"] == 1:
        session = db_session.create_session()
        voice = Voice(file_id=update.message.voice.file_id, user_name=update.effective_user.username,
                      date=update.message.date)
        session.add(voice)
        session.commit()
        session.close()
        context.chat_data["what_do"] = 0
        update.message.reply_text("Voice is add in database", reply_markup=reply_markup)
    else:
        update.message.reply_text("Add voice mode is not enabled")


def mode_of_add_voice(update: Update, context: CallbackContext) -> None:
    context.chat_data["what_do"] = 1
    update.message.reply_text("Let's record a voice", reply_markup=ReplyKeyboardRemove(reply_markup=True))


def mode_listen_to_voices(update: Update, context: CallbackContext) -> None:
    context.chat_data["what_do"] = 2
    session = db_session.create_session()
    voice = random.choice(session.query(Voice).all())
    context.chat_data["voice_id"] = voice.id
    marks = list(map(lambda x: x.mark, voice.rates))
    print(marks)
    rate = session.query(Rate).filter(Rate.user_name == update.effective_user.username,
                                      Rate.voice_id == voice.id).first()
    update.message.reply_text(
        f"@{voice.user_name}  likes-{marks.count(1)}  dislikes-{marks.count(-1)} date-{voice.date}, your mark now is {'not rated' if rate is None else like if rate.mark == 1 else dislike}")
    update.message.reply_voice(voice.file_id, reply_markup=inline_reply_markup)
    session.close()


def button(update: Update, context: CallbackContext) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    print(query)
    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()
    if abs(int(query.data)) == 1:
        session = db_session.create_session()
        mark = session.query(Rate).filter(Rate.user_name == query.from_user.username,
                                          Rate.voice_id == context.chat_data["voice_id"]).first()
        if mark:
            mark.mark = int(query.data)
        else:
            new_mark = Rate(user_name=query.from_user.username, voice_id=context.chat_data["voice_id"],
                            mark=int(query.data))
            session.add(new_mark)
        session.commit()
        session.close()


def main() -> None:
    db_session.global_init()
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Updater(TOKEN)
    # on different commands - answer in Telegram
    application.dispatcher.add_handler(CommandHandler("start", start))
    application.dispatcher.add_handler(CommandHandler("help", help_command))
    application.dispatcher.add_handler(CommandHandler("Add_voices", mode_of_add_voice))
    application.dispatcher.add_handler(CommandHandler("Listen_to_voices", mode_listen_to_voices))
    application.dispatcher.add_handler(CallbackQueryHandler(button))
    # on non command i.e message - echo the message on Telegram
    application.dispatcher.add_handler(MessageHandler(Filters.voice & ~Filters.command, voiceanalysis))
    # Run the bot until the user presses Ctrl-C
    application.start_polling()
    application.idle()


if __name__ == "__main__":
    main()
