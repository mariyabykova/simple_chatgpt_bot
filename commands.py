import openai
from telegram import Update
from telegram.ext import CallbackContext


async def start(update: Update, context: CallbackContext):
    if update.message:
        await update.message.reply_text('Привет! Я твой бот-помощник! '
                                        'Задавай мне любые вопросы!')
