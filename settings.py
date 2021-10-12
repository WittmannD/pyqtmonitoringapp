from os import environ, path

from dotenv import load_dotenv, find_dotenv

ROOT = environ['ROOT'] = path.dirname(__file__)
load_dotenv(find_dotenv())

QTWEBENGINE_REMOTE_DEBUGGING = environ.get('QTWEBENGINE_REMOTE_DEBUGGING')
DOWNLOAD_COVERS = environ.get('DOWNLOAD_COVERS', 'false').lower() == 'true'
GOOGLE_API_KEY = environ.get('GOOGLE_API_KEY')
CONFIG_PATH = environ.get('CONFIG_PATH')
ASSETS_PATH = environ.get('ASSETS_PATH')
PUBLIC_URL = environ.get('PUBLIC_URL')
DEVTOOLS = environ.get('DEVTOOLS', 'false').lower() == 'true'
