token="Your_API_bot_token"
login="your_site_login"
passw="your_passw_login"
admin_id="your_telegram_id"#id админа (кому отправляется в ЛС информация)


time_1 = '16:00'
time_2 = '07:00'

languages = ['English(Английский)', 'Russian(Русский)']

incorrect_lang_choice = """Нет такого варианта ответа. Повторите ввод
Incorrect answer. Re-enter answer below"""


text_buy_rus= "Description to buy"
text_question_rus ="Text_question_buy"

text_buy_eng = "text_buy_eng"
text_question_eng = "text_question_eng"

choose_lang = """Choose a language to continue
Выберите язык, чтобы продолжить"""

choose_lang_repeat = """Choose a language to continue
The bot has been restarted recently, please start choosing cars again. Type 'Car search' after choosing a language
Выберите язык, чтобы продолжить
Недавно бот был перезапущен, пожалуйста начните заново выбор машин. Напишите 'Подбор авто' после выбора языка"""


eng_rus_menu = {languages[0]: ['Car search', 'How to buy', 'FAQ', 'Choose the action'], languages[1]: ['Подбор авто', 'Как купить', 'Частые вопросы', 'Сменить язык', 'Выберите действие']}

hello_msg = """Здравствуйте!
Это бот по продаже машин из аукционов США
Hello!
I am a bot for selling cars from USA actions"""