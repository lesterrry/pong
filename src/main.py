'''''''''''''''''''''''''''''
COPYRIGHT LESTER COVEY (me@lestercovey.ml),
2022

'''''''''''''''''''''''''''''
from os import path
from telethon import TelegramClient, events, sync
from telethon.tl.types import PeerUser
import toml
import sys
import gc

CONFIG_FILE_NAME = "config"  # Your .toml config file name (like 'file')
VERSION = "0.1.0-beta"

if "-V" in sys.argv or "--version" in sys.argv:
	print(f"Pong v{VERSION}")
	exit(0)

def my_except_hook(exctype, value, traceback):
	if exctype is not KeyboardInterrupt:
		print(f"FATAL: {value}")
		exit(1)
sys.excepthook = my_except_hook

file_path = path.dirname(path.dirname(path.realpath(__file__)))
setup_mode = False
config = toml.load(f"{file_path}/{CONFIG_FILE_NAME}.toml")

if "-s" in sys.argv or "--setup" in sys.argv:
	setup_mode = True
if not path.isfile(file_path + "/session.session") and not setup_mode:
	raise Exception("Session file was not found. Retry with '-s' or '--setup' to create new")

client = TelegramClient(file_path + "/session", config['api']['id'], config['api']['hash'])

@client.on(events.NewMessage(incoming=True))
async def handler(event):
	if type(event.peer_id) is not PeerUser:
		return
	sender = await client.get_entity(event.peer_id)
	known_phones = []
	known_ids = []
	known_usernames = []
	for i in config['contacts']['known']:
		if i[0] == '@':
			known_usernames.append(i[1:])
		if i[0] == '+':
			known_phones.append(i[1:])
		else:
			known_ids.append(i)
	ignore_phones = []
	ignore_ids = []
	ignore_usernames = []
	for i in config['contacts']['ignore']:
		if i[0] == '@':
			ignore_usernames.append(i[1:])
		if i[0] == '+':
			ignore_phones.append(i[1:])
		else:
			ignore_ids.append(i)
	if (sender.is_self 
		or sender.bot 
		or sender.support 
		or str(sender.id) in ignore_ids 
		or sender.username in ignore_usernames 
		or sender.phone in ignore_phones):
		print("Will not reply")
		return
	if 'for_known' in config['messages'] and (str(sender.id) in known_ids or sender.username in known_usernames or sender.phone in known_phones):
		print("Will reply with", config['messages']['for_known'])
	elif 'for_others' in config['messages']:
		print("Will reply with", config['messages']['for_others'])
	return
	# await event.reply('yo')
	print(event.peer_id)

client.connect()
if not client.is_user_authorized() and not setup_mode:
	raise Exception("You are unauthorized. Retry with '-s' or '--setup' to authorize")
del CONFIG_FILE_NAME, VERSION, file_path, setup_mode
gc.collect()
client.start().loop.run_forever()