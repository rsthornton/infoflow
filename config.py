"""Configuration settings for InfoFlow."""

import os

# Flask settings
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'

# Model default settings
DEFAULT_NUM_CITIZENS = 50
DEFAULT_NUM_CORPORATE_MEDIA = 3
DEFAULT_NUM_INFLUENCERS = 5
DEFAULT_NUM_GOVERNMENT = 1
DEFAULT_NETWORK_TYPE = "small_world"
