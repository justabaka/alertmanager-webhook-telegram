#!/usr/bin/env python3.7
import logging
import json
import os
import sys
import telegram
from dateutil.parser import parse
from pprint import pformat
from flask import Flask
from flask import request
from flask import render_template
from flask_basicauth import BasicAuth

log_level = os.getenv('LOG_LEVEL', 'INFO')
if log_level == 'DEBUG':
    debug = True
else:
    debug = False

level = logging.getLevelName(log_level)
logging.basicConfig(level=level)

app = Flask(__name__)
app.secret_key = 'aYT>.L$kk2h>!'
app.config['BASIC_AUTH_USERNAME'] = os.getenv('BASIC_AUTH_USERNAME', '')
app.config['BASIC_AUTH_PASSWORD'] = os.getenv('BASIC_AUTH_PASSWORD', '')

if os.getenv('FORCE_BASIC_AUTH', 'False').lower() in [1, 't', 'true', 'yes', 'on']:
    app.logger.info('Basic Auth is enabled')

    if not app.config['BASIC_AUTH_USERNAME'] or not app.config['BASIC_AUTH_PASSWORD']:
        app.logger.critical('Please specify BASIC_AUTH_USERNAME and BASIC_AUTH_PASSWORD if you want to use Basic Authentication.\n' \
                         'Alternatively you can set FORCE_BASIC_AUTH to false to disable the protection.'
        )
        sys.exit(4)

    app.config['BASIC_AUTH_FORCE'] = True
else:
    app.logger.info('Basic Auth is disabled')
    app.config['BASIC_AUTH_FORCE'] = False

if not os.getenv('BOT_TOKEN'):
    app.logger.critical('Please specify the Telegram Bot Token in the BOT_TOKEN environment variable.')
    sys.exit(4)
else:
    bot = telegram.Bot(token=os.getenv('BOT_TOKEN', ''))

if not os.getenv('CHAT_ID'):
    app.logger.critical('Please specify the Telegram Chat ID in the CHAT_ID environment variable.')
    sys.exit(4)
else:
    chat_id = os.getenv('CHAT_ID', '')

basic_auth = BasicAuth(app)

@app.route('/', methods = ['POST'])
def postAlertmanager():
    app.logger.debug("Received a request: %s" % pformat(request.get_data()))

    try:
        content = json.loads(request.get_data())
    except Exception as e:
        app.logger.error("Cannot parse JSON data: %s.\nError message: %s" % (pformat(request.get_data()), str(e)))
        bot.sendMessage(chat_id=chat_id, text="Cannot parse JSON data: %s.\nError message: %s" % (request.get_data(), str(e)))

    try:
        for alert in content['alerts']:
            timediff = parse(alert['endsAt']) - parse(alert['startsAt'])

            message = render_template("alert.j2", alert=alert, duration=timediff)
            app.logger.debug('Rendered a message: %s' % pformat(message))
            
            bot.sendMessage(chat_id=chat_id, text=message, parse_mode=telegram.ParseMode.MARKDOWN)
            return "Alert OK", 200
    except Exception as e:
        app.logger.debug("Cannot send a message: %s" % pformat(e))
        bot.sendMessage(chat_id=chat_id, text="Cannot send a message: %s" % str(e))
        return "Alert FAIL", 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=debug)
