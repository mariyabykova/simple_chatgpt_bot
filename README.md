# simple_chatgpt_bot
ChatGPT телеграм-бот

### Описание
Телеграм-бот предназначен для взаимодействия с API ChatGPT. Пользователи отправляют через бот запросы в сервис ChatGPT и получают ответ. Перед началом работы бота необходимо выполнить команду /start и ввести пароль от бота.

Бот использует языковую модель 'gpt-3.5-turbo', для которой максимальное количество токенов при запросах не может превышать 4096. Эта особенность учтена при разработке бота: установлены ограничения на количество символов для запросов и ответов. В проекте введена константа TOTAL_TOKENS = 4000 (немного меньше максимальной суммы). Константа MAX_COMPLETION_LENGTH указывает на максимальное количество токенов, которое может содерджать ответ CharGPT. Токены, которые тратятся пользователем в процессе взаимодействия с ChatGPT, в сумме не могут превышать TOTAL_TOKENS - MAX_COMPLETION_LENGTH. Когда сумма потраченных токенов достигает этого числа, старые сообщения в истории чата очищаются, а бот посылает пользователю соответствующее уведомление. Также установлено ограничение на длину одного сообщения пользователя (константа MAX_PROMPT_LENGTH). Если вопрос пользователя слишком длинный, бот просит сократить запрос.

Чтобы контролировать использованные токены, можно выполнить команду /tokens, которая позволяет получить информацию о том, сколько токенов осталось до очистки истории старых сообщений.

При желании пользователь может самостоятельно очистить историю сообщений командой /reset. В этом случае удаляются все сообщения, включая последние.

Полностью история чата очищается также в случае ошибок со сторовны сервера OpenAI. Бот посылает уведомление об ошибке и очистке истории чата.

Информацию об особенностях работы с ботом пользователи могут узнать, выполнив команду /information.

Предусмотрена возможность поиска в истории чата: выполнив команду /search, пользователь должен ввести слово или фразу, которую нужно найти. Бот последовательно выводит все сообщения из истории чата, где найдена указанная фраза. После этого выполнение команды автоматически завершается и бот переводится в обычный режим работы с ChatGPT. Для следующего поиска надо заново ввести команду /search.

Все указанные команды выведены в виде кнопок, на которые можно нажать и получить соответствующий ответ от бота.

Для бота настроено логирование. Логи записываются в файл.

### Технологии
* python 3.9
* python-telegram-bot 20.3

### Как запустить проект локально:

Клонировать репозиторий и перейти в него в командной строке:

``` git clone git@github.com:mariyabykova/simple_chatgpt_bot.git``` 
``` cd  simple_chatgpt_bot```

Создать в директории проекта файл .env и добавить туда необходимые для работы бота переменные. Пример можно посмотреть в файле .env.example.

Создать виртуальное окружение:

* Если у вас Linux/macOS:
    ``` python3 -m venv venv ``` 

* Если у вас Windows:
    ``` python -3.9 -m venv venv ```

Активировать виртуальное окружение:

* Если у вас Linux/macOS:
    ``` source venv/bin/activate ``` 

* Если у вас Windows:
    ``` source venv/Scripts/activate ```

Обновить pip:

``` python3 -m pip install --upgrade pip ``` 

Установить зависимости из файла requirements:

``` pip install -r requirements.txt ``` 

Запустить проект:

``` python3 simple_chatgpt_bot.py ``` 


### Автор проекта

**Мария Быкова.** 
