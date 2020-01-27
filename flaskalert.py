#!/usr/bin/env python3.7
# pylint: disable=line-too-long, no-member, broad-except
"""
A simple script that receives Alertmanager webhooks and sends an alert message via Telefram to a pre-configured chat group.
"""
import logging
import json
import os
import sys
from pprint import pformat
from dateutil.parser import parse
import telegram
from flask import Flask
from flask import request
from flask import render_template
from flask import current_app as app
from flask_basicauth import BasicAuth

LOG_LEVEL = logging.getLevelName(os.getenv('LOG_LEVEL', 'INFO'))
logging.basicConfig(level=LOG_LEVEL)

app = Flask(__name__)
app.secret_key = 'aYT>.L$kk2h>!'


def get_env_var(env_variable_name='', default='', required=False):
    """ Get an environment variable value. Supports default values and exiting when missing a required variable. """
    if required and env_variable_name not in os.environ:
        app.logger.critical("In order to get the application working you must configure the {} environment variable.".format(env_variable_name))
        sys.exit(4)
    else:
        return str(os.getenv(env_variable_name, default))


app.bot = telegram.Bot(token=get_env_var('BOT_TOKEN', required=True))
app.chat_id = get_env_var('CHAT_ID', required=True)
app.use_basic_auth = get_env_var('FORCE_BASIC_AUTH', default='no', required=False)

if app.use_basic_auth.lower() in ['1', 't', 'true', 'yes', 'on']:
    app.config['BASIC_AUTH_FORCE'] = True
    app.config['BASIC_AUTH_USERNAME'] = get_env_var('BASIC_AUTH_USERNAME', required=True)
    app.config['BASIC_AUTH_PASSWORD'] = get_env_var('BASIC_AUTH_PASSWORD', required=True)
    app.basic_auth = BasicAuth(app)
    app.logger.info('Basic Auth is enabled')
else:
    app.config['BASIC_AUTH_FORCE'] = False
    app.logger.info('Basic Auth is disabled')


@app.route('/', methods=['POST'])
def post_alertmanager():
    """ Processes a webhook POST request with a JSON paylod, renders a message using a template and sends it via Telegram """
    app.logger.debug("Received a request: %s" % pformat(request.get_data()))

    try:
        content = json.loads(request.get_data())
    except Exception as exc:
        app.logger.error("Cannot parse JSON data: %s.\nError message: %s" % (pformat(request.get_data()), str(exc)))
        app.bot.sendMessage(chat_id=app.chat_id, text="Cannot parse JSON data: %s.\nError message: %s" % (request.get_data(), str(exc)))

    try:
        for alert in content['alerts']:
            timediff = parse(alert['endsAt']) - parse(alert['startsAt'])

            message = render_template("alert.j2", alert=alert, duration=timediff)
            app.logger.debug('Rendered a message: %s' % pformat(message))

            app.bot.sendMessage(chat_id=app.chat_id, text=message, parse_mode=telegram.ParseMode.MARKDOWN)
            return "Alert OK", 200
    except Exception as exc:
        app.logger.debug("Cannot send a message: %s" % pformat(exc))
        app.bot.sendMessage(chat_id=app.chat_id, text="Cannot send a message: %s" % str(exc))
        return "Alert FAIL", 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=LOG_LEVEL == logging.DEBUG)
