# Alertmanager Webhook for Telegram
This is a Flask (Python) implementation.

## Running in Kubernetes
### Template && kubectl apply:
1. Edit values.yaml and set up everything in the 'config' section.
2. Run `helm template . -f values.yaml | kubectl apply -n monitoring -f -`

If you know how to use Helm's `--set` arguments, you may use that instead of editing values.yaml: `helm template . -f values.yaml --set config.telegram.bot_token="XXXXX:YYYYYYYY",config.telegram.chat_id=\"-1234567\",config.basic_auth.enabled=false | kubectl apply -n monitoring -f -`

### Helm chart-based installation
Wasn't tested yet.

## Running in Docker
All the configuration is done using environment variables. Basic Authentication is disabled by default, the default loglevel is INFO. There are only two required environment variables: BOT_TOKEN and CHAT_ID. 
  
  Here's an example with every environment variable possible:

    docker run -d --name alertmanager-webhook-telegram \
    	-e "BOT_TOKEN=XXXXX:YYYYYYYY" \
    	-e "CHAT_ID=-1234567" \
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
Kubernetes/Helm installation: edit template in the 'template_files' section of values.yaml and re-deploy the application.
Instead of editing the values.yaml you can simply supply a file to override or add contents during the render phase: `helm template . -f values.yaml --set-file template_files.alert\\.j2=custom_template.j2` . Note the dot escaping.

Docker installation: copy the same file from the git repository and mount it back to /alertmanager-webhook-telegram/templates (it's usually better to mount a directory).

Manual installation: simply edit `templates/alert.j2` Jinja2 template.

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

It is possible to route alerts to different chats and users, not only a single predefined one. This can be easily done using query string arguments (e.g. 'http://hostname:8080/?chat_id=-1234567').

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
