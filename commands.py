import openai
import os
from telegram import Update
from telegram.ext import CallbackContext

from dataclasses import dataclass


CHAT_HISTORY = [
    {
        'role': 'system',
        'content': 'You are a programming assistant',
    }
]
TOTAL_TOKENS = 4000
SUM_TOKENS = 0


def update_history(message, role, content):
    CHAT_HISTORY.append({'role': role, 'content': content})


def reset_messages():
    CHAT_HISTORY.clear()
    CHAT_HISTORY.append({
        'role': 'system',
        'content': 'You are a programming assistant'
    })


MODEL = 'gpt-3.5-turbo'
openai.api_key = os.getenv('OPENAI_API_KEY')


async def start(update: Update, context: CallbackContext):
    """Обработка команды /start."""
    if update.message:
        await update.message.reply_text('Привет! Я твой бот-помощник!'
                                        ' Задавай мне любые вопросы!')


async def reset(update: Update, context: CallbackContext):
    reset_messages()
    await update.message.reply_text('История чата была очищена.')


async def get_answer_from_chatgpt(update: Update, context: CallbackContext):
    """Обработка ответа от ChatGPT."""
    try:
        global SUM_TOKENS
        update_history(CHAT_HISTORY, 'user', update.message.text)
        response = openai.ChatCompletion.create(
            model=MODEL,
            messages=CHAT_HISTORY,
            max_tokens=TOTAL_TOKENS,
        )
        SUM_TOKENS += response['usage']['total_tokens']
        print(CHAT_HISTORY)
        print(SUM_TOKENS)
        print(response['usage']['total_tokens'])
        if SUM_TOKENS >= TOTAL_TOKENS:
            await update.message.reply_text('Вы использовали все токены!'
                                            ' История чата будет очищена.')
            reset_messages()
        return await update.message.reply_text(response.choices[0].message.content)
    except Exception:
        reset_messages()
        await update.message.reply_text('Ошибка! История чата будет очищена!'
                                        ' Попробуйте повторить запрос.')
