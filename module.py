# %%
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
from setting import ACCOUNT, PASSWORD, QUESTION_DICT
# %%

# %%
class HKJC(object):
    def __init__(self):
        self.driver = webdriver.Firefox(executable_path= "./geckodriver")
        self.driver.get('https://bet.hkjc.com/marksix/index.aspx?lang=ch')
        
    def login(self):
        W_account_info = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'divAccInfoLogout')))
        ## Account Information ##
        # Account
        W_account = W_account_info.find_element_by_id('account')
        W_account.clear()
        W_account.send_keys(ACCOUNT)
        # Password
        W_password = W_account_info.find_element_by_id('passwordInput1')
        W_password.click()
        W_password = W_account_info.find_element_by_id('password')
        W_password.clear()
        W_password.send_keys(PASSWORD)
        # Login
        W_loginbutton = W_account_info.find_element_by_id('loginButton')
        W_loginbutton.click()
        ## ------------------------
        ## Safety Question and Answer
        self.driver.find_element_by_class_name('ekbaContainer')
        W_verfiy_element = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'ekbaContainer')))
        W_verify_question = W_verfiy_element.find_element_by_id('ekbaSeqQuestion')
        _count_question_try = 0 # Monitor the question
        for question, answer in QUESTION_DICT.items():
            if question in W_verify_question.text:
                W_verfiy_element.find_element_by_id('ekbaDivInput').send_keys(answer)
                W_verfiy_element.find_element_by_id('pic_confirm').click()
                break
            _count_question_try += 1
        # Return error since no related question
        if _count_question_try == len(QUESTION_DICT):
            raise RuntimeError('No related question, please add the information in setting.py')
        # Clean the pop-up
        W_notice = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, 'divDisclaimer')))
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, 'disclaimerProceed')))
        time.sleep(2) # seconds
        W_notice.find_element_by_id('disclaimerProceed').click()
        
    def close(self):
        self.driver.close()
