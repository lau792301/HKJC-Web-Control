# %%
import os
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
# %%
ACCOUNT = os.environ['ACCOUNT']
PASSWORD = os.environ['PASSWORD']
QUESTION_DICT = {
    '你第一份工作是屬於甚麼行業':'行業',
    '你第一個旅遊目的地是哪個城市':'哪個城市',
    '你最喜愛的城市?': '城市'
}
