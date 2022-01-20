import os
import requests
import telebot


bot = telebot.TeleBot(os.environ['TOKEN'], parse_mode=None)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, 'Драсте \n'
                          'если хочешь посмотреть курс пиши команду /rate \n'
                          'если хочешь посмотреть сколько стоит твоя сума пиши /calculator')


@bot.message_handler(commands=['rate'])
def rate(message):
    markup = telebot.types.InlineKeyboardMarkup()
    for name in all_money_name:
        markup.add(telebot.types.InlineKeyboardButton(text=f'{name}', callback_data=f'{name}'))
    bot.send_message(message.chat.id, 'Выберете валюту для сравнения', reply_markup=markup)


@bot.message_handler(commands=['calculator'])
def calculator(message):
    markup = telebot.types.InlineKeyboardMarkup()
    for name in all_money_name:
        markup.add(telebot.types.InlineKeyboardButton(text=f'{name}', callback_data=f'{name}'))
    bot.send_message(message.chat.id, 'Выберете валюту', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.message.text == 'Выберете валюту')
def query_handler(call: telebot.types.CallbackQuery):
    global money_name
    money_name += [call.data]
    bot.answer_callback_query(callback_query_id=call.id, text='Отличный выбор')
    if len(number) == 0:
        answer = 'Введите ссуму для расчёта'
        msg = bot.send_message(call.message.chat.id, answer)
        bot.register_next_step_handler(msg, user_currency_calculator)
    else:
        user_currency_calculator(call.message)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)


@bot.callback_query_handler(func=lambda call: call.message.text == 'Выберете валюту для сравнения')
def query_handler(call: telebot.types.CallbackQuery):
    global money_name
    money_name += [call.data]
    bot.answer_callback_query(callback_query_id=call.id, text='Отличный выбор')
    user_currency_rate(call.message)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)


def user_currency_rate(message):
    global number
    if len(number) < 1:
        number += [1]
        calculator(message)


def user_currency_calculator(message):
    global number
    if len(number) < 1:
        number += [message.text]
        calculator(message)
    else:
        if money_name[0] == 'Гривня':
            result = int(number[0]) / cashe[money_name[1]]['rate']
            bot.send_message(message.chat.id, f'Переводя {number[0]} {money_name[0]} в {money_name[1]} ты получишь {round(result, 3)} {money_name[1]}')
        elif money_name[1] == 'Гривня':
            result = cashe[money_name[0]]['rate']
            bot.send_message(message.chat.id, f'Переводя {number[0]} {money_name[0]} в {money_name[1]} ты получишь {round(result, 3)} {money_name[1]}')
        else:
            result = cashe[money_name[0]]['rate'] / cashe[money_name[1]]['rate']
            bot.send_message(message.chat.id, f'Переводя {number[0]} {money_name[0]} в {money_name[1]} ты получишь {round(result, 3)} {money_name[1]}')
        number.clear()
        money_name.clear()
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(telebot.types.KeyboardButton('Калькулятор'), telebot.types.KeyboardButton('Сравнение валют'))
        msg = bot.send_message(message.chat.id, 'Выбери действие', reply_markup=markup)
        bot.register_next_step_handler(msg, some_func)


def some_func(message):
    if message.text == 'Калькулятор':
        calculator(message)
    elif message.text == 'Сравнение валют':
        rate(message)


def main():
    bot.enable_save_next_step_handlers()
    bot.load_next_step_handlers()
    bot.polling()


if __name__ == '__main__':
    response = requests.get('https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json')
    new_json = response.json()
    all_money_name = ['Гривня']
    cashe = {'Гривня': {'txt': 'Гривня', 'rate': 1}}
    for name in enumerate(new_json):
        all_money_name += [name[1]['txt']]
        cashe[name[1]['txt']] = name[1]
    number = []
    money_name = []
    main()
