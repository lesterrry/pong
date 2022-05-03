'''''''''''''''''''''''''''''
COPYRIGHT LESTER COVEY (me@lestercovey.ml),
2022

'''''''''''''''''''''''''''''
from os import path
from telethon import TelegramClient, events, sync
from telethon.tl.types import PeerUser
from datetime import datetime
import toml
import sys
import gc

CONFIG_FILE_NAME = "config"  # Your .toml config file name (like 'file')
VERSION = "0.1.0-beta"
FOOTER = "\n---------------\nSent automatically with [Pong](https://github.com/lesterrry/pong)"

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
responded_to = []

if "-s" in sys.argv or "--setup" in sys.argv:
	setup_mode = True
if not path.isfile(file_path + "/session.session") and not setup_mode:
	raise Exception("Session file was not found. Retry with '-s' or '--setup' to create new")

client = TelegramClient(file_path + "/session", config['api']['id'], config['api']['hash'])

def log(text):
	file_exists = path.isfile(file_path + "/log.txt")
	with open(file_path + "/log.txt", 'a' if file_exists else 'w') as f:
		dated = datetime.now().strftime("[%a %d %b %H:%M] ")
		f.write(dated + text + "\n")
def log_response(sender, incoming):
	sender_name = ""
	if sender.first_name is not None and sender.last_name is not None:
		sender_name = f"{sender.first_name} {sender.last_name}"
	elif sender.username is not None:
		sender_name = "@" + sender.username
	elif sender.phone is not None:
		sender_name = "+" + sender.phone
	else:
		sender_name = f"<{sender.id}>"
	log(f"Responding to {sender_name} who wrote: '{incoming}'")

@client.on(events.NewMessage(incoming=True))
async def handler(event):
	if type(event.peer_id) is not PeerUser:
		return
	sender = await client.get_entity(event.peer_id)
	# FIXME:
	# Dumbass approach
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
		or sender.phone in ignore_phones
		or (config['messages']['respond_only_once'] and sender.id in responded_to)):
		print("Will not reply")
		return
	if 'for_known' in config['messages'] and (str(sender.id) in known_ids or sender.username in known_usernames or sender.phone in known_phones):
		# await event.reply(config['messages']['for_known'] + FOOTER, link_preview=False)
		responded_to.append(sender.id)
	elif 'for_others' in config['messages']:
		if config['service']['logging_enabled']:
			log_response(sender, event.message.text)
		print("Will reply with", config['messages']['for_others'])
		# await event.reply(config['messages']['for_others'] + FOOTER, link_preview=False)
		responded_to.append(sender.id)

client.connect()
if not client.is_user_authorized() and not setup_mode:
	raise Exception("You are unauthorized. Retry with '-s' or '--setup' to authorize")
log_str = f"Starting Pong v{VERSION}..."
print(log_str)
if config['service']['logging_enabled']:
	log(log_str)
del CONFIG_FILE_NAME, VERSION, setup_mode, log_str
gc.collect()
client.start().loop.run_forever()