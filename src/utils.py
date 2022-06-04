#  Copyright (c) Lester Covey (me@lestercovey.ml) & ChernV (@otter18), 2022

import enum


def get_sender_name(sender):
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


class UserType(enum.Enum):
	KNOWN = 0
	OTHER = 1
	IGNORED = 2


class Phonebook:
	def __init__(self, config):
		self.known_phones = []
		self.known_ids = []
		self.known_usernames = []

		for i in config['contacts']['known']:
			if i[0] == '@':
				self.known_usernames.append(i[1:])
			if i[0] == '+':
				self.known_phones.append(i[1:])
			else:
				self.known_ids.append(i)

		self.ignore_phones = []
		self.ignore_ids = []
		self.ignore_usernames = []

		for i in config['contacts']['ignore']:
			if i[0] == '@':
				self.ignore_usernames.append(i[1:])
			if i[0] == '+':
				self.ignore_phones.append(i[1:])
			else:
				self.ignore_ids.append(i)

	def get_status(self, sender):
		if str(sender.id) in self.ignore_ids \
				or sender.username in self.ignore_usernames \
				or sender.phone in self.ignore_phones:
			return UserType.IGNORED

		if str(sender.id) in self.known_ids \
				or sender.username in self.known_usernames \
				or sender.phone in self.known_phones:
			return UserType.KNOWN

		return UserType.OTHER
