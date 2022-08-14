import logging

toto_logger = logging.getLogger("toto")

assert toto_logger.level == logging.NOTSET # new logger has NOTSET level
assert toto_logger.getEffectiveLevel() == logging.WARN # and its effective level is the root logger level, i.e. WARN

# attach a console handler to toto_logger
console_handler = logging.StreamHandler()
FORMATTER = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s")
console_handler.setFormatter(FORMATTER)
toto_logger.addHandler(console_handler)
toto_logger.debug("debug") # nothing is displayed as the log level DEBUG is smaller than toto effective level
toto_logger.setLevel(logging.DEBUG)
toto_logger.debug("debug message")