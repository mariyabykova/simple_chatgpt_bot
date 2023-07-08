import logging
import os
import sys

from dotenv import load_dotenv
import openai
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import CallbackContext, ConversationHandler

from messages_constants import (AUTHORIZATION_ERROR_MESSAGE, GREETING_MESSAGE,
                                INFORMATION_MESSAGE, SEARCH_MESSAGE)
from utils import (check_users, count_num_tokens, reset_messages,
                   update_history, delete_old_message)


load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='logs.log',
    filemode='w'
)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))


ALLOWED_VISITORS = []
ALL_HISTORY = {}
CHAT_OBJECT = {
    'role': 'system',
    'content': 'You are a bot-assistant'
}
MAX_PROMPT_LENGTH = 300
MAX_COMPLETION_LENGTH = 2000
MODEL = 'gpt-3.5-turbo'
PASSWORD = 0
SEARCH = 0
SECRET_PASSWORD = os.getenv('SECRET_PASSWORD')
SUM_TOKENS = 0
TOTAL_TOKENS = 4000


async def start(update: Update, context: CallbackContext):
    """Обработка команды /start."""
    if update.message:
        if check_users(update.message.chat.id, ALLOWED_VISITORS):
            logger.info(f'Пользователь {update.message.chat.first_name}'
                        f' начал работу с ботом.')
            button = ReplyKeyboardMarkup(
                [['/reset', '/tokens', '/information', '/search']],
                resize_keyboard=True
            )
            await update.message.reply_text(
                f'Привет, {update.message.chat.first_name}!'
                f' Я твой бот-помощник!'
                f' {GREETING_MESSAGE}',
                reply_markup=button
            )
        else:
            await update.message.reply_text(
                'Введите пароль!'
            )
            return PASSWORD


async def enter_password(update: Update, context: CallbackContext):
    """Ввод пароля для начала работы."""
    password = update.message.text
    if password == SECRET_PASSWORD:
        logger.info(f'Пользователь {update.message.chat.first_name}'
                    f' начал работу с ботом.')
        ALLOWED_VISITORS.append(update.message.chat.id)
        ALL_HISTORY[update.message.chat.id] = [
            [{'role': 'system', 'content': 'You are a bot-assistant'}],
            SUM_TOKENS
        ]
        button = ReplyKeyboardMarkup(
            [['/reset', '/tokens', '/information', '/search']],
            resize_keyboard=True
        )
        await update.message.reply_text(
            f'Пароль верный. Я готов к работе с тобой,'
            f' {update.message.chat.first_name}!'
            f' {GREETING_MESSAGE}',
            reply_markup=button
        )
        return ConversationHandler.END
    else:
        logger.info(f'Пользователь {update.message.chat.first_name}'
                    f' ввёл неверный пароль.')
        await update.message.reply_text(
            'Пароль неверный. Вы не можете пользоваться ботом.'
        )


async def get_informaion(update: Update, context: CallbackContext):
    """Информация о работе бота."""
    if check_users(update.message.chat.id, ALLOWED_VISITORS):
        logger.info(f'Пользователь {update.message.chat.first_name}'
                    ' запросил информацию о боте.')
        await update.message.reply_text(
            INFORMATION_MESSAGE.format(
                model=MODEL,
                max_tokens=(TOTAL_TOKENS - MAX_COMPLETION_LENGTH)
            )
        )
    else:
        await update.message.reply_text(AUTHORIZATION_ERROR_MESSAGE)


async def reset(update: Update, context: CallbackContext):
    """Очистка истории чата. Команда /reset."""
    if check_users(update.message.chat.id, ALLOWED_VISITORS):
        # global ALL_HISTORY
        personal_history = ALL_HISTORY[update.message.chat.id]
        logger.info(f'Пользователь {update.message.chat.first_name}'
                    ' очистил историю своего чата.')
        reset_messages(personal_history[0], CHAT_OBJECT)
        personal_history[1] = 0
        await update.message.reply_text('История чата была очищена.')
    else:
        await update.message.reply_text(AUTHORIZATION_ERROR_MESSAGE)


async def count_tokens(update: Update, context: CallbackContext):
    """Подсчёт количества оставшихся токенов. Команда /tokens"""
    if check_users(update.message.chat.id, ALLOWED_VISITORS):
        personal_history = ALL_HISTORY[update.message.chat.id]
        logger.info(f'Пользователь {update.message.chat.first_name}'
                    f' запросил остаток токенов:'
                    f' {TOTAL_TOKENS - MAX_COMPLETION_LENGTH - personal_history[1]}')
        await update.message.reply_text(
            f'Ваш остаток токенов:'
            f'{TOTAL_TOKENS - MAX_COMPLETION_LENGTH - personal_history[1]}',
        )
    else:
        await update.message.reply_text(AUTHORIZATION_ERROR_MESSAGE)


async def search_word(update: Update, context: CallbackContext):
    """Команда /search – пользователю предлагается ввести слово или фразу,
    которые он хочет найти в истории чата.
    """
    if check_users(update.message.chat.id, ALLOWED_VISITORS):
        logger.info(f'Пользователь {update.message.chat.first_name}'
                    f' выполнил команду search.')
        await update.message.reply_text(
                'Введите слово или фразу, которую нужно найти'
                ' в истории сообщений.'
            )
        return SEARCH
    else:
        await update.message.reply_text(AUTHORIZATION_ERROR_MESSAGE)


async def find_word(update: Update, context: CallbackContext):
    """Отправка пользователю сообщений из истории чата,
    в которых найдены искомые слова.
    """
    if check_users(update.message.chat.id, ALLOWED_VISITORS):
        word = update.message.text
        find_index = 0
        personal_history = ALL_HISTORY[update.message.chat.id]
        for element in personal_history[0]:
            result_answer = (element.get('content')).lower()
            result_author = element.get('role')
            if result_author == 'user':
                result_author = update.message.chat.first_name
            search_message = SEARCH_MESSAGE.format(
                word=word,
                author=result_author,
                answer=result_answer
            )
            if word.lower() in result_answer:
                logger.info(
                    f'Бот отправил пользователю'
                    f' {update.message.chat.first_name}'
                    f' сообщение: {search_message}',
                )
                await update.message.reply_text(search_message)
                find_index = 1
        if find_index == 0:
            logger.info(
                    f'Бот отправил пользователю'
                    f' {update.message.chat.first_name} сообщение:'
                    f' Слово {word} не найдено в истории чата.'

                )
            await update.message.reply_text(
                f'Слово {word} не найдено в истории чата.'
            )
        return ConversationHandler.END
    else:
        await update.message.reply_text(AUTHORIZATION_ERROR_MESSAGE)


async def get_answer_from_chatgpt(update: Update, context: CallbackContext):
    """Обработка ответа от ChatGPT."""
    if check_users(update.message.chat.id, ALLOWED_VISITORS):
        try:
            if count_num_tokens(update.message.text,
                                'cl100k_base') >= MAX_PROMPT_LENGTH:
                logger.info(
                    f'Пользователь {update.message.chat.first_name}'
                    f' отправил слишком длинный запрос боту.'
                    f' Пользователю отправлено предупреждение.'
                )
                return await update.message.reply_text(
                    'Вы использовали слишком много токенов.'
                    ' Сократите запрос.'
                )
            personal_history = ALL_HISTORY[update.message.chat.id]
            update_history(personal_history[0], 'user', update.message.text)
            logger.info(
                f'Пользователь {update.message.chat.first_name}'
                f' отправил запрос боту:'
                f' {update.message.text}'
            )
            response = openai.ChatCompletion.create(
                model=MODEL,
                messages=personal_history[0],
                max_tokens=MAX_COMPLETION_LENGTH,
            )
            update_history(personal_history[0], 'assistant',
                           response.choices[0].message.content)
            personal_history[1] += response['usage']['total_tokens']
            if personal_history[1] >= TOTAL_TOKENS - MAX_COMPLETION_LENGTH:
                await update.message.reply_text(
                    'Вы использовали слишком много токенов!'
                    ' Старые сообщения будут удалены.'
                )
                delete_old_message(personal_history[0])
                personal_history[1] = response['usage']['total_tokens']
            logger.info(f'Получен ответ от бота:'
                        f' {response.choices[0].message.content}'
                        f' Моя история {personal_history}'
                        f' Вся история {ALL_HISTORY}')
            return await update.message.reply_text(
                response.choices[0].message.content
            )
        except Exception as error:
            logger.error(f'{error}')
            personal_history = ALL_HISTORY[update.message.chat.id]
            reset_messages(personal_history[0], CHAT_OBJECT)
            personal_history[1] = 0
            await update.message.reply_text(
                'Ошибка OpenAI! История чата будет очищена!'
                ' Попробуйте повторить запрос.'
            )
    else:
        await update.message.reply_text(AUTHORIZATION_ERROR_MESSAGE)
