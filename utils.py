import logging
import os
import sys
import time
from datetime import timedelta
from logging.handlers import RotatingFileHandler

if not os.path.exists("logs"):
    os.makedirs("logs")

FORMATTER = logging.Formatter("%(message)s")
LOG_FILE = "logs/evosim.log"

def get_console_handler():
   console_handler = logging.StreamHandler(sys.stdout)
   console_handler.setFormatter(FORMATTER)
   return console_handler
def get_file_handler():
   file_handler = RotatingFileHandler(LOG_FILE, maxBytes=64000, backupCount=10)
   file_handler.setFormatter(FORMATTER)
   return file_handler
def get_logger(logger_name):
   logger = logging.getLogger(logger_name)
   logger.setLevel(logging.DEBUG) # better to have too much log than not enough
   logger.addHandler(get_console_handler())
   logger.addHandler(get_file_handler())
   # with this pattern, it's rarely necessary to propagate the error up to parent
   logger.propagate = False
   adapter = CustomAdapter(logger)
   return adapter

class CustomFormatter:
   def __init__(self):
      self.start_time = time.time()

   def format(self, record):
      elapsed_seconds = record.created - self.start_time
      #using timedelta here for convenient default formatting
      elapsed = timedelta(seconds = elapsed_seconds)
      return "{} | {}".format(elapsed, record.getMessage())

class CustomAdapter(logging.LoggerAdapter):
   """
   Adds the elapsed time since start of script
   """
   def __init__(self, logger, extra={}):
      super().__init__(logger, extra)
      self.start_time = time.time()

   def process(self, msg, kwargs):
      elapsed = time.time() - self.start_time
      parsed_time = f"{elapsed//3600:02.0f}:{elapsed%3600//60:02.0f}:{elapsed%60:02.0f}"
      return f'{parsed_time} | {msg}', kwargs
