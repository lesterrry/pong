#!/usr/bin/env python3
#  Copyright (c) Lester Covey (me@lestercovey.ml) & ChernV (@otter18), 2022

import logging
import sys
from os import path

import toml
from telethon import TelegramClient, events
from telethon.tl.types import PeerUser

from cronitor_logging import Cronitor, cronitor_heartbeat
from log import log_response, setup_excepthook
from utils import Phonebook, UserType

CONFIG_FILE_NAME = "config"  # Your .toml config file name (like 'file')
VERSION = "0.2.3-beta"

if "-v" in sys.argv or "--version" in sys.argv:
    print(f"Pong v{VERSION}")
    sys.exit(0)

file_path = path.dirname(path.dirname(path.realpath(__file__)))
setup_mode = False
config = toml.load(f"{file_path}/{CONFIG_FILE_NAME}.toml")
responded_to = []
times_responded = 0

cronitor = Cronitor(config) if config['service']['cronitor_integrated'] else None
setup_excepthook(config, cronitor)

if "-s" in sys.argv or "--setup" in sys.argv:
    setup_mode = True

if not path.isfile(file_path + "/session.session") and not setup_mode:
    raise FileNotFoundError("Session file was not found. Retry with '-s' or '--setup' to create new")

client = TelegramClient(file_path + "/session", config['api']['id'], config['api']['hash'], app_version=VERSION)
phonebook = Phonebook(config)


@client.on(events.NewMessage(incoming=True))
async def handler(event):
    global times_responded

    if type(event.peer_id) is not PeerUser:
        return

    try:
        sender = await client.get_entity(event.peer_id)
    except:
        return

    try:
        if sender.is_self or sender.bot or sender.support:
            return

        if config['messages']['respond_only_once'] and sender.id in responded_to:
            return

        sender_type = phonebook.get_status(sender)
        if sender_type == UserType.IGNORED:
            return
        elif sender_type == UserType.KNOWN and 'for_known' in config['messages']:
            await event.reply(config['messages']['for_known'] + config['messages']['footer'], link_preview=False)
            responded_to.append(sender.id)
        elif 'for_others' in config['messages']:
            await event.reply(config['messages']['for_others'] + config['messages']['footer'], link_preview=False)
            responded_to.append(sender.id)

        times_responded += 1

        if config['service']['logging_enabled']:
            log_response(sender, event.message.text)

        if config['service']['cronitor_integrated']:
            cronitor.inform(sender, event.message.text, times_responded)

    except Exception as e:
        sys.excepthook(type(e), e)


client.connect()
if not client.is_user_authorized() and not setup_mode:
    raise PermissionError("You are unauthorized. Retry with '-s' or '--setup' to authorize")

log_str = f"Starting Pong v{VERSION}..."
print(log_str)

if config['service']['logging_enabled']:
    logging.info(log_str)

if config['service']['cronitor_integrated']:
    cronitor.informstate(log_str, "run")

loop = client.start().loop
if config['service']['cronitor_integrated']:
    loop.create_task(cronitor_heartbeat(cronitor))
loop.run_forever()
