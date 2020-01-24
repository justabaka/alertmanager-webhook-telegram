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

## Manual installation and running
* `pip install -r requirements.txt`
* `python flaskAlert.py`

## Building a Docker Image 
* `docker build -t alertmanager-webhook-telegram .`

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

Telegram configuration
==================================

### How to register a bot
1) Open your Telegram Client or Telegram Web and talk to `@BotFather`.
2) Type `/start` then type or select `/newbot`
3) Follow the bot instructions. Usually you only need to specify a bot name and username.
4) Copy the bot token and **keep it safe**. Do not post it anywhere and make sure it doesn't appear in a debug log that you want to show someone!

### How to get the chat ID
1) Add bot to some channel
2) Send a message containing @botname to this channel
3) Access the link https://api.telegram.org/botXXX:YYYY/getUpdates (replace XXX:YYYY with your bot token)

### Another way to get the chat ID
1) Sign in to Telegram Web at https://web.telegram.org/
2) Click on the chat in the left pane
3) You can get the chat ID in the URL


Testing alerts
===============
You can use bash snippets inside the `tests` directory.
