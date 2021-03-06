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
from jinja2.runtime import Undefined

LOG_LEVEL = logging.getLevelName(os.getenv('LOG_LEVEL', 'INFO').upper())
logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

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
app.use_basic_auth = get_env_var('FORCE_BASIC_AUTH', default='no', required=False)
app.time_format = get_env_var('DATE_TIME_FORMAT', default='%H:%M:%S %a %d.%m.%Y')

if app.use_basic_auth.lower() in ['1', 't', 'true', 'yes', 'on']:
    app.config['BASIC_AUTH_FORCE'] = True
    app.config['BASIC_AUTH_USERNAME'] = get_env_var('BASIC_AUTH_USERNAME', required=True)
    app.config['BASIC_AUTH_PASSWORD'] = get_env_var('BASIC_AUTH_PASSWORD', required=True)
    app.basic_auth = BasicAuth(app)
    app.logger.info('Basic Auth is enabled')
else:
    app.config['BASIC_AUTH_FORCE'] = False
    app.logger.info('Basic Auth is disabled')


@app.template_filter()
def escape_telegram_markdown(item):
    """
    Escapes characters in text as Telegram Bot API requires.
    Info:
      * https://core.telegram.org/bots/api#markdownv2-style
      * https://python-telegram-bot.readthedocs.io/en/stable/telegram.utils.helpers.html#telegram.utils.helpers.escape_markdown
    """
    return telegram.utils.helpers.escape_markdown(text=str(item), version=2)


@app.route('/', methods=['POST'])
def post_alertmanager():
    """
    Processes a webhook POST request with a JSON paylod, renders a message using a template and sends it via Telegram.
    You can supply a 'CHAT_ID' environment variable that will be used by default and/or a 'chat_id' query string argument
    to override the default behaviour and achieve dynamic alert routing.
    """
    app.logger.debug("Received a request: {}".format(pformat(request.get_data())))

    # TODO: Implement @username support https://stackoverflow.com/a/31081941
    if 'chat_id' in request.args:
        chat_id = request.args.get('chat_id')
        app.logger.debug("Using CHAT_ID from the request query string arguments")
    else:
        app.logger.debug("CHAT_ID wasn't supplied in the request query string, switching to environment variables")
        chat_id = get_env_var('CHAT_ID', required=True)

    app.logger.debug('Using chat_id={}'.format(chat_id))

    try:
        content = json.loads(request.get_data())
    except Exception as exc:
        app.logger.error("Cannot parse JSON data: {}.\n  Error message: {}".format(pformat(request.get_data()), pformat(str(exc))))
        return "Alert FAIL", 500

    try:
        for alert in content['alerts']:
            alert['startsAt'] = parse(alert['startsAt'])

            if alert['status'] == 'resolved':
                alert['endsAt'] = parse(alert['endsAt'])
                timediff = alert['endsAt'] - alert['startsAt']

                alert['endsAt'] = alert['endsAt'].strftime(app.time_format)
            else:
                timediff = None

            alert['startsAt'] = alert['startsAt'].strftime(app.time_format)
    except Exception as exc:
        app.logger.error("Cannot parse date/time in the message:\n message={}".format(pformat(str(exc))), pformat(alert))
        return "Alert FAIL", 500

    try:
        message = render_template("alert.j2", alert=alert, duration=timediff)
        app.logger.debug('Rendered the message: {}'.format(pformat(message)))
    except Exception as exc:
        app.logger.error("Cannot render a message:\n message={}\n".format(pformat(alert), pformat(str(exc))))
        return "Alert FAIL", 500

    try:
        app.bot.sendMessage(chat_id=chat_id, text=message, parse_mode=telegram.ParseMode.MARKDOWN_V2)
        return "Alert OK", 200
    except Exception as exc:
        app.logger.error("Cannot send the message:\n  chat_id={}\n  message={}".format(chat_id, pformat(str(exc))))
        return "Alert FAIL", 500


@app.route('/health', methods=['GET'])
@app.route('/healthz', methods=['GET'])
def healthcheck():
    """ Naive health check that works more like a liveness probe """
    return "OK", 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=LOG_LEVEL == logging.DEBUG)
