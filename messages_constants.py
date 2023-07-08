AUTHORIZATION_ERROR_MESSAGE = ('Вы не имеете права пользоваться ботом.'
                               ' Выполните команду /start,'
                               ' а затем введите пароль.')

GREETING_MESSAGE = (
    ' Задавай мне любые вопросы!'
    ' Очистить историю чата можно командой /reset.'
    ' Посмотреть остаток токенов после запроса можно командой /tokens.'
    ' Подробную информацию о работе со мной можно узнать,'
    ' выполнив команду /information '
)

INFORMATION_MESSAGE = (
    'Бот использует языковую модель {model},'
    ' для которой максимальное количество токенов при запросах'
    ' не может превышать 4096. В связи с этим установлены ограничения'
    ' на количество токенов в текстах вопросов и ответов.'
    ' Токены, которые вы тратите на взаимодействие'
    ' с ChatGPT не должны в сумме превышать {max_tokens}.'
    ' Когда сумма токенов достигнет этого числа,'
    ' cтарые сообщения удаляются.'
    ' Рекомендуется проверять остаток токенов командой /tokens.'
    ' Также можно самостоятельно очищать историю чата командой /reset.'
    ' Кроме того, доступна возможность поиска сообщений в истории чата.'
    ' Для этого нужно выполнить команду /search и ввести'
    ' слово или фразу, которые необходимо найти в истории чата.'
    ' Приятного общения с искусственным интеллектом!'
)

SEARCH_MESSAGE = (
    'Слово {word} найдено в сообщении'
    ' от пользователя {author}: {answer}'
)
