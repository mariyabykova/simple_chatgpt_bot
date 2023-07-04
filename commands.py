import os

from dotenv import load_dotenv
import openai
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import CallbackContext, ConversationHandler


load_dotenv()


AUTHORIZATION_ERROR_MESSAGE = ('Вы не имеете права пользоваться ботом.'
                               ' Выполните команду /start,'
                               ' а затем введите пароль.')
ALLOWED_VISITORS = []
CHAT_OBJECT = {
    'role': 'system',
    'content': 'You are a programming assistant'
}
CHAT_HISTORY = [CHAT_OBJECT]
MODEL = 'gpt-3.5-turbo'
PASSWORD = 0
SECRET_PASSWORD = os.getenv('SECRET_PASSWORD')
SUM_TOKENS = 0
TOTAL_TOKENS = 4000


def update_history(message, role, content):
    """Вспомогательная функция для обновления истории чата."""
    CHAT_HISTORY.append({'role': role, 'content': content})


def reset_messages():
    """Вспомогательная функция для очистки истории чата."""
    CHAT_HISTORY.clear()
    CHAT_HISTORY.append(CHAT_OBJECT)


def check_users(user_id):
    """Вспомогательная функция для проверки прав доступа пользователя."""
    if user_id in ALLOWED_VISITORS:
        return True


async def start(update: Update, context: CallbackContext):
    """Обработка команды /start."""
    if update.message:
        if update.message.chat.id in ALLOWED_VISITORS:
            button = ReplyKeyboardMarkup([['/reset', '/tokens']],
                                 resize_keyboard=True)
            await update.message.reply_text(
                f'Привет, {update.message.chat.first_name}!'
                f' Я твой бот-помощник!'
                f' Задавай мне любые вопросы!',
                reply_markup=button
            )
        else:
            await update.message.reply_text(
                f'Введите пароль!'
            )
            return PASSWORD


async def enter_password(update: Update, context: CallbackContext):
    """Ввод пароля для начала работы."""
    password = update.message.text
    if password == SECRET_PASSWORD:
        ALLOWED_VISITORS.append(update.message.chat.id)
        await update.message.reply_text(
            'Пароль верный. Я готов к работе с тобой!'
            ' Можешь задавать мне любые вопросы.'
            ' Очистить историю поиска можно командой /reset.'
            ' Посмотреть остаток токенов после запроса можно командой /tokens'
        )
        return ConversationHandler.END
    else:
        await update.message.reply_text(
        'Пароль неверный. Вы не можете пользоваться ботом.'
        )


async def reset(update: Update, context: CallbackContext):
    """Очистка истории чата."""
    if check_users(update.message.chat.id):
        reset_messages()
        await update.message.reply_text('История чата была очищена.')
    else:
        await update.message.reply_text(AUTHORIZATION_ERROR_MESSAGE)


async def count_tokens(update: Update, context: CallbackContext):
    """Подсчёт количества оставшихся токенов."""
    if check_users(update.message.chat.id):
        await update.message.reply_text(
            f'Ваш остаток токенов: {TOTAL_TOKENS - SUM_TOKENS}',
        )
    else:
        await update.message.reply_text(AUTHORIZATION_ERROR_MESSAGE)


async def get_answer_from_chatgpt(update: Update, context: CallbackContext):
    """Обработка ответа от ChatGPT."""
    if check_users(update.message.chat.id):
        try:
            global SUM_TOKENS
            update_history(CHAT_HISTORY, 'user', update.message.text)
            response = openai.ChatCompletion.create(
                model=MODEL,
                messages=CHAT_HISTORY,
                max_tokens=TOTAL_TOKENS,
            )
            update_history(CHAT_HISTORY, 'assistant', response.choices[0].message.content)
            print(CHAT_HISTORY)
            SUM_TOKENS += response['usage']['total_tokens']
            if SUM_TOKENS >= TOTAL_TOKENS:
                await update.message.reply_text('Вы использовали все токены!'
                                                ' История чата будет очищена.')
                reset_messages()
            return await update.message.reply_text(
                response.choices[0].message.content
            )
        except Exception:
            reset_messages()
            await update.message.reply_text('Ошибка! История чата будет очищена!'
                                            ' Попробуйте повторить запрос.')
    else:
        await update.message.reply_text(AUTHORIZATION_ERROR_MESSAGE)
