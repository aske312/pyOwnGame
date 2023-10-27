import telebot
from telebot.types import *
from datetime import datetime
from common.config import config, SqlDataBase

token = config(filename='common/config.ini', section='tg')['token']
db = config(filename='common/config.ini', section='pg3')

user, base = {}, {}
date_now = datetime.now()
bot = telebot.TeleBot(token)


# def keyboard_line(key):
#     markup = ReplyKeyboardMarkup(resize_keyboard=True)
#     if key == 'start_game':
#         # counts = []
#         # for i in range(1, 9):
#         #     counts.append(InlineKeyboardButton(f'{i}', callback_data=f'{i}'))
#         # markup = InlineKeyboardMarkup()
#         # for count in counts:
#         #     markup.row(count)
#     return markup

# -4066185756
@bot.message_handler(commands=['start'])
def start(message):
    sql = f'''SELECT user_id FROM users WHERE user_id = {message.from_user.id}'''
    if not SqlDataBase(db, sql).raw():
        user['user_id'] = str(message.from_user.id)
        user['date'] = f"'{str(date_now)}'"
        user['username'] = f"'{str(message.from_user.username)}'"
        user['first_name'] = f"'{str(message.from_user.first_name)}'"
        user['language_code'] = f"'{str(message.from_user.language_code)}'"
        base['users'] = user
        SqlDataBase(base=db, request=base).insert()
        bot.send_message(message.chat.id, f"Привет @{message.from_user.first_name}! Добро пожаловать в Свою игру!")
    else:
        bot.send_message(message.chat.id, f"Рад тебя снова видеть, {message.from_user.first_name}!")
    bot.delete_message(message.chat.id, message.message_id)
    base.clear()


# /new_game {name_game user_1 user_2 ... user_n} corrected
@bot.message_handler(commands=['new_game'])
def new_game(message):
    new = message.text.split()[1:]
    sql = f'''SELECT name FROM game WHERE name = 'game_{new[0]}' '''
    if not SqlDataBase(db, sql).raw():
        user['date'] = f"'{str(date_now)}'"
        user['gm_id'] = f"'{str(message.from_user.id)}'"
        user['name'] = f"'game_{str(new[0])}'"
        user['count_users'] = f"'{str(len(new[1:]))}'"
        user['step_game'] = "'create_session'"
        base['game'] = user
        SqlDataBase(base=db, request=base).insert()

        base.clear(), user.clear()
        new_table = {'game_' + str(new[0]): {
            'id SERIAL PRIMARY KEY': '',
            'date_start TIMESTAMP': '',
            'date_udp TIMESTAMP': '',
            'name_user TEXT': '',
            'balls TEXT': ''
        }}
        SqlDataBase(base=db, request=new_table).create()
        date_start = str(date_now)
        for name_user in new[1:]:
            user['date_start'] = f"'{str(date_start)}'"
            user['date_udp'] = f"'{str(date_now)}'"
            user['name_user'] = f"'{str(name_user)}'"
            user['balls'] = f"'{str(0)}'"
            base['game_' + str(new[0])] = user
            SqlDataBase(base=db, request=base).insert()
            base.clear(), user.clear()
        bot.send_message(message.chat.id, f"Игра {new[0]} создана, на {len(new[1:])} игрока(-ов).")
    else:
        bot.send_message(message.chat.id, f"Игра с именем {new[0]} уже существует!\n"
                                          f"Или вам не достаточно прав :с")
    bot.delete_message(message.chat.id, message.message_id)


@bot.message_handler(commands=['start_game'])
def start_game(message):
    name_game = message.text.split()[1:]
    get_gm_id = f'''SELECT gm_id FROM game WHERE name = 'game_{name_game[0]}' '''
    res = SqlDataBase(base=db, request=get_gm_id).raw()
    bot.send_message(res[0]['gm_id'], 'Ваша игра началась!')


GAME_NEW = {'game': {
    'id_game SERIAL PRIMARY KEY': ' ',
    'date TIMESTAMP': ' ',
    'gm_id TEXT': ' ',
    'name TEXT': ' ',
    'count_users TEXT': ' ',
    'step_game TEXT': ' '
}}
SqlDataBase(base=db, request=GAME_NEW).create()
bot.polling()
