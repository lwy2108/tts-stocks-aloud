"""
tts_stocks_aloud.py: A simple CLI program that speaks aloud selected stock prices at the chosen interval, requires input
for tickers and interval.
"""

from json import dump, load
from tempfile import NamedTemporaryFile
from yahoo_fin.stock_info import get_live_price, get_market_status  # install yahoo_fin
from gtts import gTTS  # Google Text-to-Speech, install gtts
from playsound import playsound  # install playsound, PyObjC
from os import unlink
from time import sleep
from sys import exit


def name_selection():
    name = None
    while True:
        name = input('Please enter your name and press enter: ')
        if name:
            confirm = input('Confirm (y/n)? ')
            if confirm == 'y':
                return name
            else:
                continue


def stock_selection():
    stock = []
    print('Stock selection: please input symbols, followed by enter after each symbol.')
    while True:  # fix empty list
        pick = input('$')
        if pick == '':
            break
        else:
            stock.append(pick)
    return stock


def confirm_selection():
    print(stock)
    confirm = input('Please (c)onfirm or (r)edo: ')
    return confirm


def wait_selection():
    while True:
        try:
            wait = int(input('Please indicate your desired interval in minutes (1-30): '))
        except ValueError:
            continue
        if 1 <= wait <= 30:
            break
    return wait


def backup_config():
    with open('config.json', 'w') as f:
        dump(stock, f)  # fix for name, wait


def restore_config():
    try:
        with open('config.json', 'r') as f:
            config = load(f)
            print('Last run configuration is', config)
            restore = input('Restore (y/n)? ')
            if restore == 'y':
                return config
            else:
                return None
    except FileNotFoundError:
        pass


def request_prices():
    stock_prices = ''
    for ticker in stock:
        ticker_price = str(ticker) + ', $' + str(round(get_live_price(ticker), 2)) + '. '
        stock_prices += ticker_price
    return stock_prices


def speak(message):
    with NamedTemporaryFile() as tf:
        tf.name = 'audio_tf.mp3'
        try:
            audio = gTTS(text=(name + '! Stock update: ' + message), lang='en', slow=False)
        except NameError:
            audio = gTTS(text=message, lang='en', slow=False)
        audio.save(tf.name)
        playsound(tf.name)
        tf.close()
        unlink(tf.name)
    sleep(wait * 60)


def status_check():  # to quit on market close
    status = get_market_status()
    if status != 'REGULAR':
        status_message = 'Market is closed. Exiting now.'
        global wait
        wait = 1 / 12
        speak(status_message)
        exit()


print('This program speaks your selected stock prices at the chosen interval.')

status_check()  # toggle this for testing outside market hours (valid for 1 iteration)

name = name_selection()

stock = restore_config()

while True:  # main loop
    if not stock:
        stock = stock_selection()
        confirm = confirm_selection()
        if confirm == 'c':
            backup_config()
        else:
            stock = None
            continue

    wait = wait_selection()
    while wait:
        stock_prices = request_prices()
        speak(stock_prices)
        status_check()  # toggle this to allow for more iterations for testing outside market hours

# implement clean exit via user input
# parallelization to respect chosen interval
