import tiktoken


def count_num_tokens(string, encoding_name):
    """Вспомогательная функция для подсчёта токенов в тексте,
    который вводит пользователь."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def update_history(chat_history, role, content):
    """Вспомогательная функция для обновления истории чата."""
    chat_history.append({'role': role, 'content': content})


def reset_messages(chat_history, chat_object):
    """Вспомогательная функция для очистки истории чата."""
    chat_history.clear()
    chat_history.append(chat_object)