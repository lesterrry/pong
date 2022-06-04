#  Copyright (c) Lester Covey (me@lestercovey.ml) & ChernV (@otter18), 2022

import asyncio

import requests

from utils import get_log_string


async def cronitor_heartbeat(cronitor_obj):
	await asyncio.sleep(300)
	while True:
		cronitor_obj.cronitor_ping()
		await asyncio.sleep(300)


class Cronitor:
	def __init__(self, config):
		self.config = config

	def ping(self):
		requests.get(
			f"https://cronitor.link/p/{self.config['service']['cronitor_key']}/"
			f"{self.config['service']['cronitor_id']}"
			f"?host={self.config['service']['cronitor_hostname']}",
			timeout=10
		)

	def inform(self, sender, incoming, tr):
		message = get_log_string(sender, incoming)
		requests.get(
			f"https://cronitor.link/p/{self.config['service']['cronitor_key']}/"
			f"{self.config['service']['cronitor_id']}"
			f"?host={self.config['service']['cronitor_hostname']}&"
			f"message={message}&"
			f"metric=count:{tr}",
			timeout=10
		)

	def informstate(self, message, state):
		requests.get(
			f"https://cronitor.link/p/{self.config['service']['cronitor_key']}/"
			f"{self.config['service']['cronitor_id']}"
			f"?host={self.config['service']['cronitor_hostname']}"
			f"&message={message}"
			f"&state={state}",
			timeout=10
		)
