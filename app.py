import requests
from bs4 import BeautifulSoup
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext
import threading
import time

from keep_alive import keep_alive

keep_alive()

BOT_TOKEN = "6887561344:AAHKTK9FoMyO7zEB6YZqyR6MjQmhywG2wjc"
CHAT_ID = -1002155752084  # Will be set when the user sends /start
PRODUCT_URLS = [
    "https://www.dzrt.com/en/seaside-frost.html",
    "https://www.dzrt.com/en/purple-mist.html",
    "https://www.dzrt.com/en/spicy-zest.html",
    "https://www.dzrt.com/en/mint-fusion.html",
    "https://www.dzrt.com/en/garden-mint.html",
    "https://www.dzrt.com/en/edgy-mint.html",
    "https://www.dzrt.com/en/highland-berries.html",
    "https://www.dzrt.com/en/icy-rush.html",
]

CHECK_INTERVAL = 300

bot = Bot(token=BOT_TOKEN)
is_checking = False  # Flag to control checking process


def start(update: Update, context: CallbackContext):
    global CHAT_ID
    CHAT_ID = update.message.chat_id
    update.message.reply_text("Started checking the product availability.")
    # Start the checking process in a new thread
    if not is_checking:
        threading.Thread(target=check_product_availability).start()


def check_product_availability():
    global is_checking
    is_checking = True
    while is_checking:
        try:
            for a_product_url in PRODUCT_URLS:
                response = requests.get(a_product_url)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, "html.parser")

                product_status_div = soup.find("div", class_="product-info-stock-sku")
                if product_status_div:
                    stock_unavailable = product_status_div.find(
                        "div", class_="stock unavailable"
                    )
                    if (
                        stock_unavailable
                        and "Back In Stock Soon" in stock_unavailable.text
                    ):
                        print("Product is still out of stock.")
                    else:
                        bot.send_message(
                            chat_id=CHAT_ID,
                            text=f"The product is now available! Check it here: {a_product_url}",
                        )
                        is_checking = False
                        break
                else:
                    print("Product status div not found.")
        except requests.exceptions.RequestException as e:
            print(f"Error checking the product: {e}")
        time.sleep(CHECK_INTERVAL)


def stop(update: Update, context: CallbackContext):
    global is_checking
    is_checking = False
    update.message.reply_text("Stopped checking the product availability.")


def main():

    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("stop", stop))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":

    main()
