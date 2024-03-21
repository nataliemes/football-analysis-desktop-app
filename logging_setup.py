import logging
from custom_logging import DiscordHandler, ImportantFilter

discord_webhook_url = "https://discord.com/api/webhooks/1219985617304158271/_Vm5B4eACDVMrl2qqMY5zex524P47z4iiKEz10c0wDBs4FmlHZARHE2xudKCqst-p5-m"

logging.basicConfig(
    level = logging.DEBUG,
    filename = "app_logs.log",
    filemode = "w"
)

short_formatter = logging.Formatter("%(levelname)s // %(message)s")
long_formatter = logging.Formatter("%(asctime)s // %(name)s // %(levelname)s // %(message)s")

logger = logging.getLogger("my_app")

# console handler === logs WARNING, ERROR, CRITICAL level messages
console = logging.StreamHandler()
console.setLevel(logging.WARNING)
console.setFormatter(short_formatter)
logger.addHandler(console)

# file handler === logs CRITICAL level messages
file = logging.FileHandler(filename="important_logs.txt")
file.setLevel(logging.CRITICAL)
file.setFormatter(long_formatter)
logger.addHandler(console)

# discord handler for discord_logger === logs all level messages with a custom filter
discord_handler = DiscordHandler(discord_webhook_url)
discord_handler.setLevel(logging.DEBUG)
discord_handler.setFormatter(long_formatter)
discord_handler.addFilter(ImportantFilter())
logger.addHandler(discord_handler)
