# Alertmanager Webhook for Telegram
This is a Flask (Python) implementation.

## Running in Docker
All the configuration is done using environment variables. Basic Authentication is disabled by default, the default loglevel is INFO. There are only two required environment variables: BOT_TOKEN and CHAT_ID. 
  
  Here's an example with every environment variable possible:

    docker run -d --name alertmanager-webhook-telegram \
    	-e "BOT_TOKEN=telegramBotToken" \
    	-e "CHAT_ID=telegramChatID" \
    	-e "FORCE_BASIC_AUTH=True" \
    	-e "LOG_LEVEL=INFO" \
    	-e "BASIC_AUTH_USERNAME=<username>" \
    	-e "BASIC_AUTH_PASSWORD=<password>" \
    	-p 8080:8080 justabaka/alertmanager-webhook-telegram:latest

## Building a Docker Image 
* `docker build -t alertmanager-webhook-telegram .`

## Manual installation and running
* `pip install -r requirements.txt`
* `python flaskalert.py`

## Message template customization
Currently it can only be done by editing the `templates/alert.j2` Jinja2 template.

Alertmanager configuration example
==================================

                receivers:
                - name: 'telegram-webhook'
                  webhook_configs:
                  - url: http://hostname:8080
                    send_resolved: true
                    http_config:
                      basic_auth:
                        username: 'username'
                        password: 'password'

It is possible to route alerts to different chats and users, not only a single predefined one. This can be easily done using query string arguments (e.g. 'http://hostname:8080/?chat_id=-12345').

Please also check the telegram configuration section on how to send messages to individual users.

Telegram configuration
==================================

### How to register a bot
1. Open your Telegram Client or Telegram Web and talk to `@BotFather`.
2. Type `/start` then type or select `/newbot`
3. Follow the bot instructions. Usually you only need to specify a bot name and username.
4. Copy the bot token and **keep it safe**. Do not post it anywhere and make sure it doesn't appear in a debug log that you want to show someone!

### How to get the chat ID
1. Add bot to some channel
2. Send a message containing @botname to this channel
3. Access the link https://api.telegram.org/botXXX:YYYY/getUpdates (replace XXX:YYYY with your bot token)

### Another way to get the chat ID
1. Sign in to Telegram Web at https://web.telegram.org/
2. Click on the chat in the left pane
3. You can get the chat ID in the URL

### Sending alerts to a @username
In order to send alerts an individual user you must obtain the Telegram user ID via https://t.me/userinfobot or a similar service. You may supply the ID as a regular chat id. Sending directly to @username is not supported yet.

Please also note that the user needs to send any message to the bot first.

Testing alerts
===============
You can use bash snippets inside the `tests` directory.
