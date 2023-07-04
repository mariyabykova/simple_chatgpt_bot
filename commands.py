import openai
import os
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import CallbackContext


CHAT_HISTORY = [
    {
        'role': 'system',
        'content': 'You are a programming assistant',
    }
]
SUM_TOKENS = 0
TOTAL_TOKENS = 4000


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
        button = ReplyKeyboardMarkup([['/reset', '/tokens']],
                                 resize_keyboard=True)
        await update.message.reply_text(
            f'Привет, {update.message.chat.first_name}!'
            f' Я твой бот-помощник!'
            f' Задавай мне любые вопросы!',
            reply_markup=button
        )


async def reset(update: Update, context: CallbackContext):
    reset_messages()
    await update.message.reply_text('История чата была очищена.')


async def count_tokens(update: Update, context: CallbackContext):
    await update.message.reply_text(
        f'Ваш остаток токенов: {TOTAL_TOKENS - SUM_TOKENS}',
    )


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
        if SUM_TOKENS >= TOTAL_TOKENS:
            await update.message.reply_text('Вы использовали все токены!'
                                            ' История чата будет очищена.')
            reset_messages()
        return await update.message.reply_text(response.choices[0].message.content)
    except Exception:
        reset_messages()
        await update.message.reply_text('Ошибка! История чата будет очищена!'
                                        ' Попробуйте повторить запрос.')
