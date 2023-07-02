import openai
import os
from telegram import Update
from telegram.ext import CallbackContext


MODEL = 'text-davinci-003'
openai.api_key = os.getenv('OPENAI_API_KEY')


async def start(update: Update, context: CallbackContext):
    if update.message:
        await update.message.reply_text('Привет! Я твой бот-помощник!'
                                        ' Задавай мне любые вопросы!')


async def get_answer_from_chatgpt(update: Update, context: CallbackContext):
    response = openai.Completion.create(
        model=MODEL,
        prompt=update.message.text,
        max_tokens=4000,
    )
    return await update.message.reply_text(response.choices[0].text)
