import telebot
import psycopg2
from time import sleep

conn = psycopg2.connect(database="sirius_2023", user="sirius_2023", password="change_me", host="127.0.0.1", port="38746")
print("Database opened successfully")

bot = telebot.TeleBot("5675351738:AAFheCIDHRzpVDw6MPpk7zjrfaZSrgIfpI0")

model = None
manufacturer = None
year = None
expenses = None
electricity = None
years = None
equipment = []

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я бот для расчета стоимости серверного оборудования. Какую функцию вы бы хотели использовать?", reply_markup=get_main_menu_keyboard())

def get_main_menu_keyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    button1 = telebot.types.KeyboardButton(text='Ввести данные')
    button2 = telebot.types.KeyboardButton(text='Рассчитать стоимость')
    keyboard.add(button1, button2)
    return keyboard


@bot.message_handler(func=lambda message: message.text == 'Ввести данные')
def add_equipment(message):
    bot.send_message(message.from_user.id, 'Введите модель оборудования')
    bot.register_next_step_handler(message, add_equipment_model)

def add_equipment_model(message):
    global model
    model = message.text
    bot.send_message(message.from_user.id, 'Введите производителя')
    bot.register_next_step_handler(message, add_equipment_manufacturer)

def add_equipment_manufacturer(message):
    global manufacturer
    manufacturer = message.text
    bot.send_message(message.from_user.id, 'Введите год выпуска')
    bot.register_next_step_handler(message, add_equipment_year)

def add_equipment_year(message):
    global year
    year = message.text
    if message.text.isdigit():
        bot.send_message(message.from_user.id, 'Введите затраты на эксплуатацию')
        bot.register_next_step_handler(message, add_equipment_expenses)
    else:
        bot.send_message(message.from_user.id, 'Введите год числом')
        bot.register_next_step_handler(message, add_equipment_year)

def add_equipment_expenses(message):
    global expenses
    expenses = message.text
    if message.text.isdigit():
        bot.send_message(message.from_user.id, 'Введите затраты на электроэнергию')
        bot.register_next_step_handler(message, add_equipment_electricity)
    else:
        bot.send_message(message.from_user.id, 'Введите затраты числом')
        bot.register_next_step_handler(message, add_equipment_expenses)

def add_equipment_electricity(message):
    global electricity
    electricity = message.text
    if message.text.isdigit():
        add_equipment_db()
        bot.send_message(message.from_user.id, 'Данные оборудования сохранены в базу данных')
        sleep(2)
        send_welcome(message)
    else:
        bot.send_message(message.from_user.id, 'Введите затраты числом')
        bot.register_next_step_handler(message, add_equipment_electricity)


def add_equipment_db():
    global conn
    cursor = conn.cursor()
    query = f"INSERT INTO equipment (model, manufacturer, year_of_issue, service_cost, electricity_cost) \
        VALUES ('{model}', '{manufacturer}', '{year}', '{expenses}', '{electricity}');"
    cursor.execute(query)
    conn.commit()
    cursor.close()


@bot.message_handler(func=lambda message: message.text == 'Рассчитать стоимость')
def input_years(message):
    bot.reply_to(message, "Введите количество лет в течении которых вы планируете использовать оборудование")
    bot.register_next_step_handler(message, choose_equipment)


def choose_equipment(message):
    global years
    if message.text.isdigit():
        years = int(message.text)
        keyboard_equipment = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        button1 = telebot.types.KeyboardButton(text='Конкретное')
        button2 = telebot.types.KeyboardButton(text='Наиболее выгодное')
        keyboard_equipment.add(button1, button2)
        bot.reply_to(message, "Хотите рассчитать цену для конкретного оборудования, или вывести самое выгодное?", reply_markup=keyboard_equipment)
    else:
        bot.send_message(message.from_user.id, 'Введите количество лет числом')
        bot.register_next_step_handler(message, input_years)


@bot.message_handler(func=lambda message: message.text == 'Наиболее выгодное')
def calculate_cost_for_one(message):
    global conn, years
    equipment_to_cost = {}
    costs = []
    minimal = 0
    cursor = conn.cursor()
    query = f"SELECT (model, manufacturer, service_cost, electricity_cost) from equipment;"
    cursor.execute(query)
    equipment = cursor.fetchall()
    if len(equipment) >= 1:
        for i in equipment:
            data = i[0].replace("(", "").replace(")", "").split(",")
            total = (int(data[2]) + int(data[3])) * years
            costs.append(total)
            equipment_to_cost[data[0] + " " + data[1]] = total
        minimal = min(costs)
        for i in equipment_to_cost.keys():
            if equipment_to_cost[i] == minimal:
                bot.reply_to(message, f"Самый выгодный вариант: {i}, затраты составят {minimal} рублей")
                break
    else:
        bot.reply_to(message, "Нет оборудования в базе данных")
    sleep(2)
    send_welcome(message)


@bot.message_handler(func=lambda message: message.text == 'Конкретное')
def calculate_cost_for_one(message):
    global conn, equipment
    cursor = conn.cursor()
    query = f"SELECT (model, manufacturer, service_cost, electricity_cost) from equipment;"
    cursor.execute(query)
    equipment = cursor.fetchall()
    if len(equipment) >= 1:
        keyboard_equipment = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
        for i in equipment:
            data = i[0].replace("(", "").replace(")", "").split(",")
            button = telebot.types.KeyboardButton(text=data[0] + " " + data[1])
            keyboard_equipment.add(button)
        bot.reply_to(message, "Выберите оборудование для расчета стоимости:", reply_markup=keyboard_equipment)
        bot.register_next_step_handler(message, print_cost)
    else:
        bot.reply_to(message, "Нет оборудования в базе данных")
    sleep(2)
    send_welcome(message)


def print_cost(message):
    global equipment, years
    for i in equipment:
        data = i[0].replace("(", "").replace(")", "").split(",")
        print(data)
        if data[0] + " " + data[1] == message.text:
            bot.reply_to(message, f"Затраты на {message.text} составят {(int(data[2]) + int(data[3])) * years}")
    sleep(2)
    send_welcome(message)


@bot.message_handler(func=lambda message: True)
def handle_unknown_message(message):
    bot.reply_to(message, "Незнакомая команда, для перезапуска бота используйте команду /start")


# Запуск бота
bot.polling()
