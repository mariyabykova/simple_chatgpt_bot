import logging
import os

from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler

from commands import start


load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
OPENAI_API_TOKEN = os.getenv('OPENAI_API_KEY')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)


def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.run_polling()


if __name__ == '__main__':
    main()
