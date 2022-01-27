import telebot
import random
from telebot import types
# Запускаем бота
from pony.orm import *

db = Database()

class Shipment(db.Entity):
    _table_ = "PM_SHIPMENT"
    id = PrimaryKey(int, auto=True)
    barcode = Required(str)
    chat = Required(int)
db.bind(provider='sqlite', filename='F:\\papermailbot.db', create_db=False)
db.generate_mapping(create_tables=False)
set_sql_debug(False)

@db_session
def find_shipment(barcode):

    print(shipment)

# Загружаем список интересных фактов
f = open('facts.txt', 'r', encoding='UTF-8')
facts = f.read().split('\n')
f.close()
# Загружаем список поговорок
f = open('thinks.txt', 'r', encoding='UTF-8')
thinks  = f.read().split('\n')
f.close()
# Создаем бота
bot = telebot.TeleBot()
# Команда start
@bot.message_handler(commands=["start"])
def start(m, res=False):
        # Добавляем две кнопки
        markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1=types.KeyboardButton("My Mail")
        item2=types.KeyboardButton("Arrived Mailings")
        markup.add(item1)
        markup.add(item2)
        bot.send_message(m.chat.id, 'Нажми: \nФакт для получения интересного факта\nПоговорка — для получения мудрой цитаты ',  reply_markup=markup)

# Получение сообщений от юзера
@bot.message_handler(content_types=["text"])
def handle_text(message):
    try:
        print(message.chat.id)
        userEntry = str(message.text.strip())

        with db_session:

            if userEntry and userEntry.isdigit():
                barcode = userEntry
                shipment = Shipment.get(barcode=barcode, chat=message.chat.id)
                if shipment:
                    print(f"Fond {barcode} in DB")
                else:
                    print(f"Not fond {barcode} in DB")
                    shipment = Shipment(barcode=barcode, chat=message.chat.id)
                    print("Created record in DB")
                    commit()
                answer = shipment.id

            else:
                answer = "Please enter mailing id to look for it"

    except Exception as e:
        print("Exception processing user entry", e)
        answer = "Error"

    # Отсылаем юзеру сообщение в его чат
    print("ANSWER:", answer)
    bot.send_message(message.chat.id, answer)

while True:
    print("The bot is now running")
    try:
        bot.polling(none_stop=True, interval=0)
    except:
        print("bot crashed")
print("The bot is now running")

'''
        # Если юзер прислал 1, выдаем ему случайный факт
        if message.text.strip() == 'Факт' :
                answer = random.choice(facts)
        # Если юзер прислал 2, выдаем умную мысль
        elif message.text.strip() == 'Поговорка':
                answer = random.choice(thinks)

'''