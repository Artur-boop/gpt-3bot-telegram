import telebot
import openai
import time


from telebot import types

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
# text en


# default command handler explains how the bot works and sends the greeting
@bot.message_handler(commands=['start'])
def handle_start(message):
    welcome_msg = bot.send_message(
        message.chat.id, 'Thank you for using this bot' + ' ' + '\N{upside-down face}')
    print(message.from_user.username)
    time.sleep(2)
    bot.edit_message_text(text='Here is how everything works. You send the message the bot sends it to the server and gives you the answear. \nHere is the example ' + '\N{nerd face}',
                          message_id=welcome_msg.message_id, chat_id=message.chat.id)
    response_greet = openai.Completion.create(
        model="text-davinci-003",
        prompt=f'Chat Gpt-3 genarate a welcome message to {message.from_user.first_name}',
        temperature=0.5,
        max_tokens=1500,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    bot.send_message(
        message.chat.id, f'Chat GPT-3 genarate a welcome message to a new user =>' + response_greet['choices'][0]['text'])


@bot.message_handler(commands=['help'])  # default command handler help
def handle_help(message):
    bot.send_message(
        message.chat.id, languages[lan[-1]]['help'])


# inline keyboard buttons hadnler to choose the language
@bot.message_handler(commands=['language'])
def language_selector(message_telegram):
    choose_lan_inline = types.InlineKeyboardMarkup()
    lan_ua = types.InlineKeyboardButton(text='Українська', callback_data='ua')
    lan_en = types.InlineKeyboardButton(text='English', callback_data='en')
    choose_lan_inline.add(lan_ua, lan_en)
    bot.send_message(message_telegram.chat.id,
                     languages[lan[-1]]['choose_lan'], reply_markup=choose_lan_inline)


# sets the default language as english
lan = []
if len(lan) == 0:
    lan = ['en']


@bot.callback_query_handler(func=lambda call: True)
def lan_anwr(call):

    if call.data == 'ua':

        # appends to the list on languages the chosen ones ukrainian
        lan.append('ua')
        print(lan)

    elif call.data == 'en':

        # appends to the list on languages the chosen ones english
        lan.append('en')
        print(lan)


# handles all other inputs which are not text
@bot.message_handler(content_types=['document', 'audio', 'photo', 'sticker', 'video', 'voice', 'location', 'contact'])
def handle_everything_else_apart_from_pic(message):
    bot.reply_to(
        message, languages[lan[-1]]['error'])


@bot.message_handler(func=lambda message_: True)
def send_welcome(message_telegram):
    print(
        f'send to request to the server - {message_telegram.text} chat id - {message_telegram.chat.id} username - {message_telegram.from_user.first_name}')
    start = time.time()
    messagetoedit = bot.send_message(
        message_telegram.chat.id, languages[lan[-1]]['send_req'] + ' ' + '\N{smiling face with sunglasses}')

    response = openai.Completion.create(  # sends the msg to the server with the amout of chars
        model="text-davinci-003",  # which is 1500 doesnt work properly if change max tokens
        prompt=message_telegram.text,  # have to change other parameters
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
    if time_execution > 5:  # if the excecution time is more than 5 seconds that send sorry
        time.sleep(0.5)
        time_sor = bot.edit_message_text(chat_id=message_telegram.chat.id,
                                         message_id=messagetoedit.message_id, text=languages[lan[-1]]['sorry'] + ' ' + '\N{thinking face}')
        time.sleep(0.2)

        proccesing = bot.edit_message_text(chat_id=message_telegram.chat.id,
                                           message_id=time_sor.message_id, text=languages[lan[-1]]['uploading'] + ' ' + '\N{rocket}')
    else:  # if not exceeds edit the msg to proccesing
        time.sleep(0.2)

        proccesing = bot.edit_message_text(chat_id=message_telegram.chat.id,
                                           message_id=messagetoedit.message_id, text=languages[lan[-1]]['uploading'] + ' ' + '\N{rocket}')
    time.sleep(0.2)

    bot.edit_message_text(chat_id=message_telegram.chat.id,
                          message_id=proccesing.message_id, text=response['choices'][0]['text'])


bot.infinity_polling()
