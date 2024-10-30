import json
import telebot
import requests
from monoapi import cr
import os


class Keep:
    def __init__(self,filename='requests.json', words=10):
        self.filename=filename
        self.max_words = words
        self.history = self.load()

    def load(self):
        if os.path.exists(self.filename):
            with open('filename.txt', 'r') as file:
                return json.load(file)

    def save_history(self):
        with open(self.filename, 'w'):
            json.dumps(self.history)

    def work(self, q):
        if len(self.history) >= self.max_words:
            self.history.pop(0)
        self.history.append(q)
        self.save_history()
        return self.history

TOKEN = '7674249727:AAFlBxKs0mLKXa3CePwVHryck6Qq-UAuwLs'
bot = telebot.TeleBot(TOKEN)
money = 0


def convert_uah_to(currency, amount):
    url = 'https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=5'
    response = requests.get(url)
    data = response.json()

    for item in data:
        if item["ccy"] == currency:
            rate = float(item['buy'])
            return round(amount / rate, 2)
    return None


@bot.message_handler(commands=['start'])
def start(message: telebot.types.Message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = telebot.types.KeyboardButton('📃-> Курс Валют')
    button2 = telebot.types.KeyboardButton('📨-> Конвертація валют')
    markup.add(button1, button2)
    bot.send_message(
        message.chat.id,
        'Вітаю тебе! Я бот, який відстежує курс валют за стандартами України. '
        'Від мене ви завжди зможете отримати актуальну інформацію щодо курсів основних валют, '
        'а також виконати швидку конвертацію гривні в іншу валюту.',
        reply_markup=markup
    )


@bot.message_handler(func=lambda message: message.text in ['📃-> Курс Валют', '📨-> Конвертація валют'])
def handle_menu(message):
    if message.text == '📃-> Курс Валют':
        bot.send_message(message.chat.id, cr())
    elif message.text == '📨-> Конвертація валют':
        bot.send_message(message.chat.id, 'Введите сумму для конвертации:')
        bot.register_next_step_handler(message, get_money)


def get_money(message: telebot.types.Message):
    global money
    try:
        money = float(message.text.strip())
    except ValueError:
        bot.send_message(message.chat.id, '<b>Неверный формат суммы! Попробуйте снова.</b>', parse_mode='HTML')
        bot.register_next_step_handler(message, get_money)
        return

    if money >= 0:
        inlinemarkup = telebot.types.InlineKeyboardMarkup(row_width=2)
        bt1 = telebot.types.InlineKeyboardButton('💵 USD', callback_data='USD')
        bt2 = telebot.types.InlineKeyboardButton('💶 EUR', callback_data='EUR')
        inlinemarkup.add(bt1, bt2)
        bot.send_message(message.chat.id, '<u>Оберіть валюту для конвертації:</u>🪙', reply_markup=inlinemarkup, parse_mode='HTML')
    else:
        bot.send_message(message.chat.id, 'Сума повинна бути больше 0. Спробуйте еще раз.')
        bot.register_next_step_handler(message, get_money)


@bot.callback_query_handler(func=lambda call: True)
def sel(call):
    global money
    target = call.data
    try:
        result = convert_uah_to(target, money)
        if result is not None:
            bot.send_message(call.message.chat.id, f'Конвертована сума: {result} {target}')
            q = {"amount": money, "from": "UAH", "to": target, "result": result}
        else:
            bot.send_message(call.message.chat.id, 'Ошибка: не удалось получить курс валюты.')
    except Exception as e:
        bot.send_message(call.message.chat.id, f'Ошибка конвертации: {e}')

if __name__ == '__main__':
    bot.infinity_polling()
