from telebot import types
import telebot
import openai
import time


# notes
# add a dictantioary where the language settings will be stored
# add some more features like input from voice or other ai
bot = telebot.TeleBot(
    "5958565491:AAEcKeuUwy8LJ6K3B9e2r2JxrzQ-EYACUuQ", parse_mode=None)
openai.api_key = "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"

# text ua

# translations for the text in english and ukrainian
languages = {
    'ua': {
        'error': 'Будь ласка відправте тест, фотографії додам згодом',
        'send_req': f'Обробка запиту',
        'uploading': 'Надсилання',
        'help': 'Привіт це бот який використовує бібліотеку GPT-3 для надання відповідей.Також, бот не показує рекламу та надає відповіді в реальному часі без затримки ,яка є в самому GPT-3. Created by Artur Bertash',
        'choose_lan': 'Виберіть мову:',
        'sorry': 'Вибачте за час сервера перегружені'


    },
    'en': {
        'error': 'Please send a text, pics with be added soon',
        'send_req': 'Processing the request',
        'uploading': 'Uplodaing',
        'help': 'Hello, this is a bot that uses the GPT-3 library to provide answers. Also, the bot does not show ads and provides answers in real time without the delay that is in GPT-3 itself. Created by Artur Bertash',
        'choose_lan': 'Choose the language:',
        'sorry': 'Servers at the capacity'
    }
}
# user settings for the language
user_settings = {

}


# default command handler explains how the bot works and sends the greeting


@bot.message_handler(commands=['start'])
def handle_start(message):

    welcome_msg = bot.send_message(
        message.chat.id, 'Thank you for choosing this bot' + ' ' + '\N{upside-down face}')
    print(message.from_user.username)
    time.sleep(2)
    bot.edit_message_text(text='Here is how everything works. You send the message the bot sends it to the server and gives you the answear. \nHere is the example ' + '\N{nerd face}',
                          message_id=welcome_msg.message_id, chat_id=message.chat.id)
    response_greet = openai.Completion.create(
        model="text-davinci-003",
        prompt=f'Chat Gpt-3 genarate a welcome message to {message.from_user.first_name} and tell about yourself',
        temperature=0.5,
        max_tokens=1500,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    bot.send_message(message.chat.id, 'UPD: GPT-3 understands all the languages and can translate the answers.\nChange the language -  /language\nЮПД: Чат розуміює всі мови та перекладає всі відповіді на вибрану мову. Для зміни мови -  /language')
    time.sleep(0.2)
    bot.send_message(
        message.chat.id, f'Chat GPT-3 genarate a welcome message to a new user =>' + response_greet['choices'][0]['text'])


@bot.message_handler(commands=['help'])  # default command handler help
def handle_help(message):
    default = 'en'
    if message.from_user.id in user_settings.keys():

        bot.send_message(
            message.chat.id, languages[user_settings[message.from_user.id]]['help'])
    else:
        bot.send_message(
            message.chat.id, languages[default]['help'])


# inline keyboard buttons hadnler to choose the language


@bot.message_handler(commands=['language'])
def language_selector(message_telegram):

    default = 'en'  # sets the default language as english

    choose_lan_inline = types.InlineKeyboardMarkup()
    # creates the buttons for the languages
    lan_ua = types.InlineKeyboardButton(text='Українська', callback_data='ua')
    lan_en = types.InlineKeyboardButton(text='English', callback_data='en')
    choose_lan_inline.add(lan_ua, lan_en)
    if message_telegram.from_user.id in user_settings.keys():  # defalut language is used
        bot.send_message(message_telegram.chat.id,
                         languages[user_settings[message_telegram.from_user.id]]['choose_lan'], reply_markup=choose_lan_inline)
    else:
        bot.send_message(message_telegram.chat.id,
                         languages[default]['choose_lan'], reply_markup=choose_lan_inline)


@bot.callback_query_handler(func=lambda call: True)
def lan_anwr(call):
    print(user_settings)
    user_id_call = call.from_user.id

    if call.data == 'ua':  # creates the key and the value the key is id
        # the values is the chose english
        user_settings[user_id_call] = 'ua'
        bot.send_message(call.message.chat.id, 'Мова змінена на українську')

    elif call.data == 'en':

        user_settings[user_id_call] = 'en'
        bot.send_message(
            call.message.chat.id, 'The set language is English')
    print(user_settings)


@bot.message_handler(content_types=['document', 'audio', 'photo', 'sticker', 'video', 'voice', 'location', 'contact'])
# handles all other inputs which are not text
def handle_everything_else_apart_from_pic(message):
    default = 'en'
    if message.from_user.id in user_settings.keys():
        bot.reply_to(
            message, languages[user_settings[message.from_user.id]]['error'])
    else:
        bot.reply_to(
            message, languages[default]['error'])


@bot.message_handler(func=lambda message_: True)  # gpt-3 input handler
def send_welcome(message_telegram):
    print(
        f'send to request to the server - {message_telegram.text} chat id - {message_telegram.chat.id} username - {message_telegram.from_user.first_name}')

    start = time.time()
    if message_telegram.from_user.id in user_settings.keys():
        language_set = user_settings[message_telegram.from_user.id]
    else:
        language_set = 'en'
    messagetoedit = bot.send_message(
        message_telegram.chat.id, languages[language_set]['send_req'] + ' ' + '\N{smiling face with sunglasses}')

    response = openai.Completion.create(    # sends the msg to the server with the amout of chars
        # which is 1500 doesnt work properly if change max tokens
        model="text-davinci-003",
        prompt=message_telegram.text,       # have to change other parameters
        temperature=0.5,
        max_tokens=1500,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    end = time.time()
    time_execution = end-start
    print('excecution time', time_execution)
    print('The message was generated')
    if time_execution > 5:                  # if the excecution time is more than 5 seconds that send sorry and then the answer
        time.sleep(0.5)
        time_sor = bot.edit_message_text(chat_id=message_telegram.chat.id,
                                         message_id=messagetoedit.message_id, text=languages[language_set]['sorry'] + ' ' + '\N{thinking face}')
        time.sleep(0.2)

        proccesing = bot.edit_message_text(chat_id=message_telegram.chat.id,
                                           message_id=time_sor.message_id, text=languages[language_set]['uploading'] + ' ' + '\N{rocket}')
    else:  # if not exceeds edit the msg to proccesing
        time.sleep(0.2)

        proccesing = bot.edit_message_text(chat_id=message_telegram.chat.id,
                                           message_id=messagetoedit.message_id, text=languages[language_set]['uploading'] + ' ' + '\N{rocket}')
    time.sleep(0.2)

    bot.edit_message_text(chat_id=message_telegram.chat.id,
                          message_id=proccesing.message_id, text=response['choices'][0]['text'])


bot.infinity_polling()
