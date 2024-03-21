import logging
import requests

class DiscordHandler(logging.Handler):
    """ handler to send log messages to discord channel via webhook """
    def __init__(self, webhook_url):
        super().__init__()
        self.webhook_url = webhook_url

    def emit(self, record: logging.LogRecord):
        log_entry = { "content": self.format(record) }
        try:
            response = requests.post(self.webhook_url, data=log_entry)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print("ERROR: failed to send log to Discord:", e)


class ImportantFilter(logging.Filter):
    """ filter to select only important log messages """
    def filter(self, record):
        return (record.msg.lower().startswith("important"))
