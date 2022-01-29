import telebot
from telebot import types
from pony.orm import *
import RussianPostAPI
from RussianPostAPI import RussianPostAPI
import ShipmentInfoParser
from ShipmentInfoParser import ShipmentInfoParser
from time import gmtime, strftime, sleep
import schedule
from threading import Thread


db = Database()
db.bind(provider='sqlite', filename='F:\\papermailbot.db', create_db=False)
set_sql_debug(False)


class Shipment(db.Entity):
    _table_ = "PM_SHIPMENT"
    id = PrimaryKey(int, auto=True)
    barcode = Required(str)
    chat = Required(int)
    last_event = Required(int)
    last_event_result = Required(int)


class Configuration(db.Entity):
    _table_ = "PM_SETTING"
    id = PrimaryKey(int, auto=True)
    param = Required(str)
    value = Required(str)

db.generate_mapping(create_tables=False)

# read configuration parameters from DB
with db_session:

    BOT_ID = Configuration[1].value
    POSTAL_API_KEY = Configuration[2].value
    POSTAL_API_PASS = Configuration[3].value
    AUTO_NOTIFICATION_INTERVAL = Configuration[4].value


def get_shipment_description(shipment_info, last_event):

    desc = f"{shipment_info.type} ({shipment_info.weight} g.) \n" + \
           strftime("%a, %d %b %H:%M", shipment_info.events[-1][3]) + " : "\
           f"{shipment_info.events[-1][2]}, {shipment_info.events[-1][5]}" + \
           "\nDeparted: " + strftime("%a, %d %b %H:%M", shipment_info.events[0][3]) + \
           f" from {shipment_info.departure_index}, {shipment_info.sender}" +\
           f"\nTo: {shipment_info.destination_index}, {shipment_info.receiver}"

    return desc


# Create bot
bot = telebot.TeleBot(BOT_ID)

COMMAND_LIST_READY_FOR_COLLECTION = "Ready for collection"
COMMAND_START_NOTIFICATION = "Start Notification"
COMMAND_STOP_NOTIFICATION = "Stop Notification"

auto_notificated_users = {}

# Start command Handler
@bot.message_handler(commands=["start"])
def start(message, res=False):
    markup = draw_buttons(message.chat.id)
    bot.send_message(message.chat.id, 'Hello, enter mailing id (14 digits) to get info', reply_markup=markup)


def draw_buttons(chat_id):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        # collect my mail button
        item = types.KeyboardButton(COMMAND_LIST_READY_FOR_COLLECTION)
        markup.add(item)
        try:
            with db_session:
                # buttons for all non-delivered shipments
                nonDeliveredShipments = select(shipment for shipment in Shipment if shipment.chat == chat_id and shipment.last_event != 2)

                for nonDeliveredShipment in nonDeliveredShipments:

                    item = types.KeyboardButton(nonDeliveredShipment.barcode)
                    markup.add(item)
        except Exception as e:
            print("Exception in draw buttons procedure", e)

        # show Start/Stop Automated Posting button depending on if user has turned it on or not
        item = types.KeyboardButton(COMMAND_STOP_NOTIFICATION if chat_id in auto_notificated_users.keys() else COMMAND_START_NOTIFICATION)
        markup.add(item)
        return markup


# Handle user messages
@bot.message_handler(content_types=["text"])
def handle_text(message):
    try:
        userEntry = str(message.text.strip())
        markup = None
        answer = None
        with db_session:

            if userEntry == COMMAND_LIST_READY_FOR_COLLECTION:
                # we will request Russian post if the shipments arrived just now
                # we will find shipments that are not marked as arrived in the DB
                shipments_to_check_for_arrival = select(
                    shipment for shipment in Shipment if shipment.chat == message.chat.id and \
                    (shipment.last_event != 2 and not (shipment.last_event == 8 and shipment.last_event_result == 2))
                )
                # and will request Russian post for their up-to-date status
                for shipment_db_record in shipments_to_check_for_arrival:
                    #print("requesting post for update on", shipment_db_record.barcode)
                    shipment_xml = RussianPostAPI.get_shipment_data(shipment_db_record.barcode, POSTAL_API_KEY, POSTAL_API_PASS)
                    shipment_info = ShipmentInfoParser.parse_xml(shipment_xml)
                    shipment_db_record.last_event = shipment_info.events[-1][0]
                    shipment_db_record.last_event_result = shipment_info.events[-1][4]

                arrivedShipments = select(
                    shipment for shipment in Shipment if shipment.chat == message.chat.id and shipment.last_event == 8 and shipment.last_event_result == 2)

                answer = ""
                for shipment_db_record in arrivedShipments:
                    answer += str(shipment_db_record.barcode) + "\n"
                if not answer:
                    answer = "There are no arrived shipments"

            elif userEntry and userEntry.isdigit() and 14 == len(str(int(userEntry))):

                barcode = userEntry
                shipment_db_record = Shipment.get(barcode=barcode, chat=message.chat.id)
                if shipment_db_record:
                    # barcode was found in the DB
                    shipment_xml = RussianPostAPI.get_shipment_data(barcode, POSTAL_API_KEY, POSTAL_API_PASS)
                    shipment_info = ShipmentInfoParser.parse_xml(shipment_xml)
                    shipment_db_record.last_event = shipment_info.events[-1][0]
                    shipment_db_record.last_event_result = shipment_info.events[-1][4]

                    answer = get_shipment_description(shipment_info, 0)

                else:
                    # barcode not found in DD
                    shipment_xml = RussianPostAPI.get_shipment_data(barcode, POSTAL_API_KEY, POSTAL_API_PASS)
                    shipment_info = ShipmentInfoParser.parse_xml(shipment_xml)

                    if shipment_info and shipment_info.events[-1][0] == 2:
                        # Russian post returned error
                        answer = "This shipping has been delivered, try again"

                    elif shipment_info:

                        shipment_db_record = Shipment(
                            barcode=barcode,
                            chat=message.chat.id,
                            last_event=shipment_info.events[-1][0],
                            last_event_result=shipment_info.events[-1][4]
                        )
                        answer = get_shipment_description(shipment_info, 0)

                    else:
                        # Russian post returned error
                        answer = "Can't find mail id, try again"

            elif userEntry == COMMAND_START_NOTIFICATION:
                auto_notificated_users[message.chat.id] = True
                answer = "Automated notification is ON"
            elif userEntry == COMMAND_STOP_NOTIFICATION:
                auto_notificated_users.pop(message.chat.id)
                answer = "Automated notification is OFF"
            else:
                # user entry has invalid format
                answer = "Enter mailing id (14 digits)"

    except Exception as e:
        print("Exception processing user entry", e)
        answer = "Error processing request, try again"

    # Отсылаем юзеру сообщение в его чат
    if not answer:
        answer = "Error processing request, try again"
    markup = draw_buttons(message.chat.id)
    bot.send_message(message.chat.id, answer, reply_markup=markup)


def schedule_checker():
    while True:
        schedule.run_pending()
        sleep(5)


def automated_notification_procedure():
    try:
        with db_session:
            for chat_id in auto_notificated_users.keys():
                nonDeliveredShipments = select(shipment for shipment in Shipment if shipment.chat == chat_id and shipment.last_event != 2)

                for nonDeliveredShipment in nonDeliveredShipments:

                    shipment_xml = RussianPostAPI.get_shipment_data(nonDeliveredShipment.barcode, POSTAL_API_KEY, POSTAL_API_PASS)
                    shipment_info = ShipmentInfoParser.parse_xml(shipment_xml)

                    if (shipment_info.events[-1][0] != nonDeliveredShipment.last_event or shipment_info.events[-1][4] != nonDeliveredShipment.last_event_result):
                        answer = get_shipment_description(shipment_info, 0)
                        nonDeliveredShipments.last_event = shipment_info.events[-1][0]
                        nonDeliveredShipments.last_event_result = shipment_info.events[-1][4]
                        bot.send_message(chat_id, answer)
    except Exception as e:
        print("Exception in Auto Notification Procedure", e)


# Create the job with schedule
schedule.every(int(AUTO_NOTIFICATION_INTERVAL)).minutes.do(automated_notification_procedure)

# Spin up a thread to run the schedule check so it doesn't block your bot.
# This will take the function schedule_checker which will check every second
# to see if the scheduled job needs to be ran.
Thread(target=schedule_checker).start()

while True:
    print("The bot is now running")
    try:
        bot.polling(none_stop=True, interval=0)
    except:
        print("The bot has crashed, restarting")
