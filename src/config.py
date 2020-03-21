import configparser

CONFIG_PATH = 'conf/config.cfg'

_config = configparser.ConfigParser()
_config.read(CONFIG_PATH)
consumer_key = _config.get('TWITTER_API', 'CONSUMER_KEY')
consumer_secret = _config.get('TWITTER_API', 'CONSUMER_SECRET')
access_token = _config.get('TWITTER_API', 'ACCESS_TOKEN')
access_token_secret = _config.get('TWITTER_API', 'ACCESS_TOKEN_SECRET')
mail_smtp = _config.get('EMAIL', 'MAIL_SMTP')
ssl_port = int(_config.get('EMAIL', 'SSL_PORT'))
sender_mail_address = _config.get('EMAIL', 'SENDER_MAIL_ADDRESS')
sender_mail_password = _config.get('EMAIL', 'SENDER_MAIL_PASSWORD')
