# %%
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
from setting import ACCOUNT, PASSWORD, QUESTION_DICT
import pickle
# %%
class HKJC(object):
    def __init__(self):
        self.driver = webdriver.Firefox(executable_path= "./geckodriver")
        self.driver.get('https://bet.hkjc.com/marksix/index.aspx?lang=ch')
        
        
    def login(self):
        W_account_info = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'divAccInfoLogout')))
        time.sleep(5)
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
        # Save the logged ccokies
        pickle.dump(self.driver.get_cookies() , open("logged-in.pkl","wb"))
    
    def go_gaming(self, gaming_type):
        W_gaming_div = self.driver.find_element_by_id('infoDiv')
        gaming_div_dict = {
            'M6': 'secMenuM6',
            'FB':'secMenuFB',
            'HR': 'secMenuHR'
        }
        W_gaming_div.find_element_by_id(gaming_div_dict[gaming_type]).click()

    def close(self):
        self.driver.close()

def _load_cookies(driver):
    for cookie in pickle.load(open("logged-in.pkl", "rb")): 
        driver.add_cookie(cookie) 


class MarkSix(object):
    def __init__(self, driver):
        self.driver = driver

    def buy_single(self, number_list:list, multi_tickets = False):
        '''
        if multi_tickets == True:
            number_list = [[1,2,3,4,5,6], [7,8,9,10,11,12], ...]
        else:
            number_list = [1,2,3,4,5,6]
        '''
        self.driver.get('https://bet.hkjc.com/marksix/Single.aspx?lang=ch')
        _load_cookies(self.driver)
        pass
    
    
# %%
