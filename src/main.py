#!/usr/bin/env python3
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
VERSION = "0.1.2.rev1"
FOOTER = "\n---------------\nSent automatically with [Pong](https://github.com/lesterrry/pong)"

if "-v" in sys.argv or "--version" in sys.argv:
	print(f"Pong v{VERSION}")
	exit(0)

def my_except_hook(exctype, value, traceback):
	if exctype is not KeyboardInterrupt:
		errstr = f"FATAL: {value}"
		print(errstr, file=sys.stderr)
		try:
			log(errstr)
		except:
			()
		exit(1)
sys.excepthook = my_except_hook

file_path = path.dirname(path.dirname(path.realpath(__file__)))
setup_mode = False
config = toml.load(f"{file_path}/{CONFIG_FILE_NAME}.toml")
responded_to = []
times_responded = 0

if "-s" in sys.argv or "--setup" in sys.argv:
	setup_mode = True
if not path.isfile(file_path + "/session.session") and not setup_mode:
	raise Exception("Session file was not found. Retry with '-s' or '--setup' to create new")

client = TelegramClient(file_path + "/session", config['api']['id'], config['api']['hash'], app_version=VERSION)

def log(text):
	file_exists = path.isfile(file_path + "/log.txt")
	with open(file_path + "/log.txt", 'a' if file_exists else 'w') as f:
		dated = datetime.now().strftime("[%a %d %b %H:%M] ")
		f.write(dated + text + "\n")
def get_sender_name(sender):
	sender_name = ""
	if sender.first_name is not None and sender.last_name is not None:
		sender_name = f"{sender.first_name} {sender.last_name}"
	elif sender.username is not None:
		sender_name = "@" + sender.username
	elif sender.phone is not None:
		sender_name = "+" + sender.phone
	else:
		sender_name = f"<{sender.id}>"
	return sender_name
def get_log_string(sender, incoming):
	return f"Responding to {get_sender_name(sender)} who wrote: '{incoming}'"
def log_response(sender, incoming):
	log(get_log_string(sender, incoming))

if config['service']['cronitor_integrated']:
	import requests
	import asyncio
	async def cronitor_heartbeat():
		while True:
			cronitor_ping()
			await asyncio.sleep(300)
	def cronitor_ping():
		requests.get(f"https://cronitor.link/p/{config['service']['cronitor_key']}/{config['service']['cronitor_id']}?host={config['service']['cronitor_hostname']}", timeout=10)
	def cronitor_inform(sender, incoming, tr):
		message = get_log_string(sender, incoming)
		requests.get(f"https://cronitor.link/p/{config['service']['cronitor_key']}/{config['service']['cronitor_id']}?host={config['service']['cronitor_hostname']}&message={message}&metric=count:{tr}", timeout=10)

@client.on(events.NewMessage(incoming=True))
async def handler(event):
	global times_responded
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
		return
	if 'for_known' in config['messages'] and (str(sender.id) in known_ids or sender.username in known_usernames or sender.phone in known_phones):
		await event.reply(config['messages']['for_known'] + FOOTER, link_preview=False)
		responded_to.append(sender.id)
	elif 'for_others' in config['messages']:
		await event.reply(config['messages']['for_others'] + FOOTER, link_preview=False)
		responded_to.append(sender.id)
	times_responded += 1
	if config['service']['logging_enabled']:
		log_response(sender, event.message.text)
	if config['service']['cronitor_integrated']:
		cronitor_inform(sender, event.message.text, times_responded)

client.connect()
if not client.is_user_authorized() and not setup_mode:
	raise Exception("You are unauthorized. Retry with '-s' or '--setup' to authorize")
log_str = f"Starting Pong v{VERSION}..."
print(log_str)
if config['service']['logging_enabled']:
	log(log_str)
del CONFIG_FILE_NAME, VERSION, setup_mode, log_str
gc.collect()
loop = client.start().loop
if config['service']['cronitor_integrated']:
	loop.create_task(cronitor_heartbeat())
loop.run_forever()
