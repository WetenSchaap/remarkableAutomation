"""
Very tiny module to be able to send messages to
for Telegram (may add more later).
"""
#%%
import urllib
import urllib.request
import urllib.parse

def telegram_message(message, baseURL):
    """
    Send a message using a TelegramBot
    This is so simple it hardly deserves a function.
    """
    message_e = urllib.parse.quote_plus(message)
    code = urllib.request.urlopen(baseURL + message_e).getcode()
    return code