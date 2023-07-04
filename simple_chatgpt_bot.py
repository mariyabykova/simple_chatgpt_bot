import logging
import os

from dotenv import load_dotenv
import openai
from telegram.ext import (ApplicationBuilder, ConversationHandler,
                          CommandHandler,
                          filters, MessageHandler)

from commands import (count_tokens, enter_password,
                      get_answer_from_chatgpt,
                      reset, start,
                      PASSWORD)


load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
SECRET_PASSWORD = os.getenv('SECRET_PASSWORD')
openai.api_key = os.getenv('OPENAI_API_KEY')


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)


def main():
    """Основная логика работы бота."""
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_password)]},
        fallbacks=[]
    ))
    application.add_handler(CommandHandler('reset', reset))
    application.add_handler(CommandHandler('tokens', count_tokens))
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        get_answer_from_chatgpt,
    ))
    application.run_polling()


if __name__ == '__main__':
    main()
