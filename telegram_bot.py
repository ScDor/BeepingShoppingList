import logging
import os
from typing import Dict

import requests
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

from BarcodeHandler import parse_hazi_hinam, ShoppingList, decode_first_barcode, get_product_name, ProductException

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Welcome, {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )


def empty_command(update: Update, context: CallbackContext) -> None:
    if update.message.chat_id in shopping_lists:
        shopping_lists[update.message.chat_id].empty()
        update.message.reply_text("Shopping list emptied successfully")
    else:
        update.message.reply_text("Your shopping list was empty already")


def add_item(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    photo_id = update.message.photo[-1].file_id
    photo_url = context.bot.getFile(photo_id).file_path

    local_folder_path = os.path.join('incoming_photos', str(update.message.chat_id))
    if not os.path.exists(local_folder_path):
        os.mkdir(local_folder_path)

    local_photo_path = os.path.join(local_folder_path, update.message.date.isoformat()) + '.jpg'

    with open(local_photo_path, 'wb') as local_photo_file:
        photo_content = requests.get(photo_url).content
        local_photo_file.write(photo_content)

    try:
        item_name = get_product_name(prices, decode_first_barcode(local_photo_path))
        if update.message.chat_id not in shopping_lists:
            shopping_lists[update.message.chat_id] = ShoppingList()

        shopping_list = shopping_lists[update.message.chat_id]

        shopping_list.add_product(item_name)
        update.message.reply_text(str(shopping_list))
    except ProductException as e:
        update.message.reply_text(str(e))


def main() -> None:
    if not os.path.exists('incoming_photos'):
        os.mkdir('incoming_photos')

    updater = Updater(open('telegram_bot_token', 'rt').read())
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("empty", empty_command))

    dispatcher.add_handler(MessageHandler(Filters.photo & ~Filters.command, add_item))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    prices = parse_hazi_hinam()
    shopping_lists: Dict[int, ShoppingList] = {}

    main()
