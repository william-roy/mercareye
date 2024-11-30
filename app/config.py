# config.py

import os
import configparser
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler

config = configparser.ConfigParser()

# Search defaults
config['SEARCH'] = {
    'Interval':     1800,
    'Jitter':       120
}

# Web UI settings
config['WEBUI'] = {
    'Port':         6322
}

# Notification settings
config['NOTIFICATIONS'] = {
    'DiscordWebhookURL':    '',
    'CustomFormatting':     '',
    'CustomIcon':           ''
}

# Misc options
config['OPTIONS'] = {
    'DataDir':      'data',
    'LogLevel':     logging.getLevelName(logging.INFO)
}

# Set path to config file
load_dotenv()
if os.getenv('DATA_DIR'):
    config['OPTIONS']['DataDir'] = os.getenv('DATA_DIR')

config_path = os.path.join(config['OPTIONS']['DataDir'], 'config.ini')

def load():
    print(f'Loading config from \'{config_path}\'')

    if os.path.isfile(config_path):
        with open(config_path, 'r') as f:
            try:
                config.read(config_path)
                print(f'Config loaded\n\n')
            except (IOError, OSError) as e:
                print(f'Error reading config file:\n{e}')
    else:
        print('No config file found, writing file with defaults')
        save()

    # Setup logging
    logfile = os.path.join(config['OPTIONS']['DataDir'], 'mercareye.log')
    rotatingHandler = RotatingFileHandler(
        logfile, maxBytes=1024*1024, backupCount=2)

    logging.basicConfig(
        level=config['OPTIONS']['LogLevel'],
        format='%(asctime)s - [%(name)s][%(levelname)s] - %(message)s',
        handlers=[rotatingHandler])
    logging.getLogger().addHandler(logging.StreamHandler())


def save():
    print(f'Saving config file to \'{config_path}\'')

    with open(config_path, 'w') as f:
        try:
            config.write(f)
        except (IOError, OSError) as e:
            print(f'Error writing config file:\n{e}')

    print('Config file saved')