'''''''''''''''''''''''''''''
COPYRIGHT LESTER COVEY (me@lestercovey.ml),
2022

'''''''''''''''''''''''''''''
from os import path
from telethon import TelegramClient, events, sync
import toml
import sys

CONFIG_FILE_NAME = "config"  # Your .toml config file name (like 'file')
VERSION = "0.1.0-beta"

def my_except_hook(exctype, value, traceback):
	if exctype is not KeyboardInterrupt:
		print(f"FATAL: {value}")
		exit(1)
#sys.excepthook = my_except_hook

file_path = path.dirname(path.dirname(path.realpath(__file__)))
setup_mode = False
config = toml.load(f"{file_path}/{CONFIG_FILE_NAME}.toml")

if not path.isfile(file_path + "/session.session") and not setup_mode:
	raise Exception("Session file does not exist. Retry with '-s' or '--setup' to create new")

client = TelegramClient(file_path + "/session", config['api']['id'], config['api']['hash'])
@client.on(events.NewMessage(incoming=True))
async def handler(event):
	await event.reply('Hello!')
client.connect()
if not client.is_user_authorized() and not setup_mode:
	raise Exception("You are unauthorized. Retry with '-s' or '--setup' to authorize")
client.start().loop.run_forever()