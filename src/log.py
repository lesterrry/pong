#  Copyright (c) Lester Covey (me@lestercovey.ml) & ChernV (@otter18), 2022

import atexit
import logging
import os
import sys

from utils import get_log_string

file_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
logging.basicConfig(filename=os.path.join(file_path, 'log.txt'), encoding='utf-8', level=logging.INFO,
					format='[%(asctime)s] %(levelname)s: %(message)s', datefmt='%a %d %b %H:%M')


def log_response(sender, incoming):
	logging.info(get_log_string(sender, incoming))


def setup_excepthook(config, cronitor):
	def my_except_hook(exc_type, value, traceback=None):
		if exc_type is KeyboardInterrupt:
			sys.__excepthook__(exc_type, value, traceback)
			return

		err_str = f"FATAL: {value}"
		print(err_str, file=sys.stderr)
		logging.exception(err_str)
		if cronitor is not None:
			try:
				cronitor.cronitor_informstate(err_str, "fail")
			except Exception:
				pass

		sys.exit(1)

	sys.excepthook = my_except_hook

	@atexit.register
	def atexit_func():
		cronitor.informstate("Exiting Pong...", "complete")
