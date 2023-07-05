import logging
import os
import sys

from dotenv import load_dotenv
import openai
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import CallbackContext, ConversationHandler

from utils import check_users, count_num_tokens, reset_messages, update_history


load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))


AUTHORIZATION_ERROR_MESSAGE = ('Вы не имеете права пользоваться ботом.'
                               ' Выполните команду /start,'
                               ' а затем введите пароль.')
ALLOWED_VISITORS = []
CHAT_OBJECT = {
    'role': 'system',
    'content': 'You are a bot-assistant'
}
CHAT_HISTORY = [CHAT_OBJECT]
GREETING_MESSAGE = (
    f' Задавай мне любые вопросы!'
    f' Очистить историю поиска можно командой /reset.'
    f' Посмотреть остаток токенов после запроса можно командой /tokens'
)
MODEL = 'gpt-3.5-turbo'
PASSWORD = 0
SECRET_PASSWORD = os.getenv('SECRET_PASSWORD')
SUM_TOKENS = 0
TOTAL_TOKENS = 3500


async def start(update: Update, context: CallbackContext):
    """Обработка команды /start."""
    if update.message:
        if check_users(update.message.chat.id, ALLOWED_VISITORS):
            button = ReplyKeyboardMarkup(
                [['/reset', '/tokens']], resize_keyboard=True
            )
            await update.message.reply_text(
                f'Привет, {update.message.chat.first_name}!'
                f' Я твой бот-помощник!'
                f' {GREETING_MESSAGE}',
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
        button = ReplyKeyboardMarkup(
            [['/reset', '/tokens']], resize_keyboard=True
        )
        await update.message.reply_text(
            f'Пароль верный. Я готов к работе с тобой,'
            f' {update.message.chat.first_name}!'
            f' {GREETING_MESSAGE}',
            reply_markup=button
        )
        return ConversationHandler.END
    else:
        await update.message.reply_text(
        'Пароль неверный. Вы не можете пользоваться ботом.'
        )


async def reset(update: Update, context: CallbackContext):
    """Очистка истории чата. Команда /reset."""
    if check_users(update.message.chat.id, ALLOWED_VISITORS):
        reset_messages(CHAT_HISTORY, CHAT_OBJECT)
        await update.message.reply_text('История чата была очищена.')
    else:
        await update.message.reply_text(AUTHORIZATION_ERROR_MESSAGE)


async def count_tokens(update: Update, context: CallbackContext):
    """Подсчёт количества оставшихся токенов. Команда /tokens"""
    if check_users(update.message.chat.id, ALLOWED_VISITORS):
        await update.message.reply_text(
            f'Ваш остаток токенов: {TOTAL_TOKENS - SUM_TOKENS}',
        )
    else:
        await update.message.reply_text(AUTHORIZATION_ERROR_MESSAGE)


async def get_answer_from_chatgpt(update: Update, context: CallbackContext):
    """Обработка ответа от ChatGPT."""
    if check_users(update.message.chat.id, ALLOWED_VISITORS):
        try:
            global SUM_TOKENS
            if count_num_tokens(update.message.text, 'cl100k_base') >= 300:
                return await update.message.reply_text(
                    'Вы использовали слишком много токенов.'
                    ' Сократите запрос.'
                )
            update_history(CHAT_HISTORY, 'user', update.message.text)
            response = openai.ChatCompletion.create(
                model=MODEL,
                messages=CHAT_HISTORY,
                max_tokens=TOTAL_TOKENS,
            )
            update_history(CHAT_HISTORY, 'assistant',
                           response.choices[0].message.content)
            SUM_TOKENS += response['usage']['total_tokens']
            print(CHAT_HISTORY)
            print(SUM_TOKENS)
            if SUM_TOKENS >= TOTAL_TOKENS:
                await update.message.reply_text('Вы использовали все токены!'
                                                ' История чата будет очищена.')
                reset_messages(CHAT_HISTORY, CHAT_OBJECT)
            return await update.message.reply_text(
                response.choices[0].message.content
            )
        except Exception as error:
            logger.error(f'{error}')
            reset_messages(CHAT_HISTORY, CHAT_OBJECT)
            await update.message.reply_text('Ошибка! История чата будет очищена!'
                                            ' Попробуйте повторить запрос.')
    else:
        await update.message.reply_text(AUTHORIZATION_ERROR_MESSAGE)
