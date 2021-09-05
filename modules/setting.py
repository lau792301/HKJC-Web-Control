# %%
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
import platform

import logging
logging.basicConfig(level = logging.INFO)

# %%
# System Operation
system_operation = platform.system()

WEBDRIVER_PATH = os.path.dirname(__file__) + '/webdriver/geckodriver'
logging.info('Reading Webdriver Path:' + WEBDRIVER_PATH)
logging.info(os.getcwd())
WEBDRIVER_PATH = WEBDRIVER_PATH + '.exe' if system_operation == 'Windows' else WEBDRIVER_PATH

# %%
ACCOUNT = os.environ['ACCOUNT']
PASSWORD = os.environ['PASSWORD']
QUESTION_DICT = {
    '你第一份工作是屬於甚麼行業':'行業',
    '你第一個旅遊目的地是哪個城市':'哪個城市',
    '你最喜愛的城市?': '城市'
}

# %%
COOKIES_FILE_NAME = 'cookies.pkl'