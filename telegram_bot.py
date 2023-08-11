from typing import List
from main import get_html, get_soup_from_html, get_tags_from_soup, get_data_from_tags, parse_info, get_data_str

from telebot import TeleBot
from telebot import types as t
import webbrowser
from decouple import config

token = config('TOKEN')

bot = TeleBot(token=token)

news_data = []

@bot.message_handler(['site', 'website'])
def site(message):
    webbrowser.open('https://kaktus.media/?lable=8')


@bot.message_handler(['start'])
def start_message(message: t.Message):
    keyboard = t.ReplyKeyboardMarkup(resize_keyboard=True)
    button_get_news = t.KeyboardButton('Получить новости')
    button_say_bye = t.KeyboardButton('На сегодня достаточно новостей, до свидания!')
    keyboard.add(button_get_news, button_say_bye)
    if message.text == 'Получить новости':
        bot.send_message(message.chat.id, f'Здравствуйте, {message.chat.username}!\nНажмите на кнопку «Получить новости» и укажите номер новости, которую хотите получить', reply_markup=keyboard)
    elif message.text == 'На сегодня достаточно новостей, до свидания!':
        bot.send_message(message.chat.id, "До свидания! Бот завершает свою работу.", reply_markup=keyboard)
    stop_bot(message.text)

@bot.message_handler(['quit', 'stop', 'goodbye', 'На сегодня достаточно новостей, до свидания!'])
def stop_bot(message: t.Message):
    # keyboard = t.ReplyKeyboardMarkup(resize_keyboard=True)
    # button_say_bye = t.KeyboardButton('На сегодня достаточно новостей, до свидания!')
    # keyboard.add(button_say_bye)
    bot.send_message(message.chat.id, "До свидания! Бот завершает свою работу.")
    bot.stop_polling()


@bot.message_handler(func=lambda message: message.text == 'Получить новости')
def press_first_button(message: t.Message):
    #ответ кнопки:
    bot.send_message(message.chat.id, parse_titles())


@bot.message_handler(func=lambda message: message.text.isdigit())
def inline_buttons(message: t.Message):
    keyboard = t.InlineKeyboardMarkup(row_width=3)
    get_descr_butt = t.InlineKeyboardButton('Описание', callback_data='call_desc')
    get_img_butt = t.InlineKeyboardButton('Изображение', callback_data='call_img')
    quit_button = t.InlineKeyboardButton('Остановить бот', callback_data='stop_bot')
    keyboard.add(get_descr_butt, get_img_butt).row(quit_button)
    news_num = message.text
    bot.send_message(message.chat.id, f'Выберите, что хотите получить: {news_num}', reply_markup=keyboard)  


@bot.callback_query_handler(func=lambda c: c.data.startswith('call_') or 'stop_bot')
def handle_callback_data(callback: t.CallbackQuery):
    if callback.data == 'call_desc':
        handle_number_input_desc(callback.message)
    elif callback.data == 'call_img':
        handle_number_input_img(callback.message)
    elif callback.data == 'stop_bot':
        stop_bot(callback.message)


def handle_number_input_desc(message: t.Message):
    news_number = int(message.text[-1])
    news_data = get_news_data_by_number(news_number)  # Функция, которая получает данные для конкретной новости
    if news_data and 'description' in news_data:
        news_text = format_desc_data(news_data)  # Форматирование данных новости для вывода
        bot.send_message(message.chat.id, news_text)
    else:
        bot.send_message(message.chat.id, "Новость с таким номером не найдена")


def handle_number_input_img(message: t.Message):
    news_number = int(message.text[-1])
    news_data = get_news_data_by_number(news_number) # Функция, которая получает данные для конкретной новости
    if news_data and 'image' in news_data:  # Проверяем наличие информации об изображении
        news_text = format_img_data(news_data) # Форматирование данных новости для вывода
        image_url = news_data['image']
        bot.send_message(message.chat.id, news_text)
        bot.send_photo(message.chat.id, image_url)  # Отправляем изображение
    else:
        bot.send_message(message.chat.id, "Новость с таким номером не найдена или отсутствует изображение")


def get_news_data_by_number(news_number: int) -> dict:
    url = 'https://kaktus.media/?lable=8'
    html = get_html(url)
    soup = get_soup_from_html(html)
    tags = get_tags_from_soup(soup)
    data = get_data_from_tags(tags)

    if 1 <= news_number <= len(data):
        return data[news_number - 1]  # индексы начинаются с 0, поэтому вычитаем 1
    return None


def format_desc_data(news_data: dict) -> str:
    # форматируем, получаем то, что нам нужно(описание)
    news_text = f"Описание: {news_data['description']}\n"
    return news_text


def format_img_data(news_data: dict) -> str:
    # форматируем, получаем то, что нам нужно(изборажение)
    news_text = f"Изображение: {news_data['image']}\n"
    return news_text


def parse_titles():
    url = 'https://kaktus.media/?lable=8'
    html = get_html(url)
    soup = get_soup_from_html(html)
    tags = get_tags_from_soup(soup)
    global data
    data = get_data_from_tags(tags)
    str_data = get_data_str(data)

    titles = [f"{data_entry['news_number']} {data_entry['title']}" for data_entry in data]
    titles_str = '\n'.join(titles[:20])  # Ограничиваемся первыми 20 заголовками
    

    return titles_str


def main():
    parse_info()


if __name__ == '__main__':
    main()

bot.infinity_polling()