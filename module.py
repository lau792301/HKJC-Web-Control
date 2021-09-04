# %%
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

import time
from setting import ACCOUNT, PASSWORD, QUESTION_DICT, WEBDRIVER_PATH, COOKIES_FILE_NAME
# import pickle

# %%
import logging
logging.basicConfig(level = logging.INFO)

# %%
class HKJC:
    def __init__(self):
        self.driver = webdriver.Firefox(executable_path= WEBDRIVER_PATH)
        self.driver.get('https://bet.hkjc.com/marksix/index.aspx?lang=ch')
        
    def login(self):
        W_account_info = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'divAccInfoLogout')))
        time.sleep(3)
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
        # pickle.dump(self.driver.get_cookies() , open(COOKIES_FILE_NAME,"wb"))
    
    def get_account_balance(self):
        acc_bal = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'valueAccBal'))).text.split(' ')[-1]
        logging.info('Account Balance:' + acc_bal)
        return acc_bal

    def go_gaming(self, gaming_type):
        W_gaming_div = self.driver.find_element_by_id('infoDiv')
        gaming_div_dict = {
            'M6': 'secMenuM6',
            'FB':'secMenuFB',
            'HR': 'secMenuHR'
        }
        W_gaming_div.find_element_by_id(gaming_div_dict[gaming_type]).click()
        time.sleep(2)

    def send_bet(self):
        self.driver.find_element_by_id('bsSendPreviewButton').click()
        # Wait Pop-up to confirm
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, 'previewSend'))).click()
        # Reply Close
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, 'replyClose'))).click()

    def close(self):
        self.driver.close()

# def _load_cookies(driver):
#     for cookie in pickle.load(open(COOKIES_FILE_NAME, "rb")): 
#         driver.add_cookie(cookie) 


class MarkSix(HKJC):
    def __init__(self, driver):
        self.driver = driver
        self.odds_menu = self.driver.find_element_by_id('oddsMenu')
        

    def _update_ball_element(self):
        ball_table = self.driver.find_element_by_id('oddsTable') \
                        .find_elements_by_xpath('table/tbody/tr')[1] \
                        .find_elements_by_xpath('td/table/tbody/tr/td')[0] \
                        .find_elements_by_xpath('table/tbody/tr')[1] \
                        .find_elements_by_xpath('td/table/tbody/tr')
        ball_elements = []
        for table_row in ball_table:
            ball_elements.extend(table_row.find_elements_by_xpath('td'))
        del ball_elements[-1] # only 1-49, 50 is null
        # Map ball element
        self.ball_elements_dict = {number: element for number, element in enumerate(ball_elements, start = 1)}
        # return self.ball_elements_dict
        
    def _add_bet(self):
        self.driver.find_element_by_class_name('rsAddBet').click()

    def _to_half_ratio(self, num = 1):
        self.driver.find_element_by_id(f'radioPartial_{num}').click()
    '''
    Example of multi_tickets
    True:
        number_list = [[1,2,3,4,5,6], [7,8,9,10,11,12], ...]
    False:
        number_list = [1,2,3,4,5,6]
    '''
    def buy_single(self, num_lists:list, multi_tickets = False):
        def _add_single_ticket(num_list:list):
            if len(num_list) == 6:
                [self.ball_elements_dict[num].click() for num in num_list]
                self._add_bet()
                logging.info('Added bet:' + str(num_list))
            else:
                raise ValueError('In single, only 6 balls are available')
        # _load_cookies(self.driver)
        self.odds_menu.find_element_by_id('oMenuSINGLE.ASPX').click()
        self._update_ball_element() # update self.ball_elements_dict
        if multi_tickets == True:
            for ticket_num_list in num_lists:
                _add_single_ticket(ticket_num_list)
        elif multi_tickets == False:
            _add_single_ticket(num_lists)

    def buy_multi(self, num_lists:list, is_full_ratio = False ,multi_tickets = False):
        def _add_single_ticket(num_list:list, is_full_ratio = is_full_ratio):
            if len(num_lists) > 6: # equal to single ball
                _ratio_type = 'Full'
                [self.ball_elements_dict[num].click() for num in num_list]
                if is_full_ratio == False:
                    _ratio_type = 'Half'
                    self._to_half_ratio()
                self._add_bet()
                logging.info(f'Added bet with {_ratio_type} ratio type:' + str(num_list))
            else:
                raise ValueError('In Mulit, must be more than 6 balls')
        self.odds_menu.find_element_by_id('oMenuMULTIPLE.ASPX').click()
        self._update_ball_element()
        if multi_tickets == True:
            for ticket_num_list in num_lists:
                _add_single_ticket(ticket_num_list)
        elif multi_tickets == False:
            _add_single_ticket(num_lists)

    def buy_banker(self, main_list:list, sub_list:list, is_full_ratio = False):
        self.odds_menu.find_element_by_id('oMenuBANKER.ASPX').click()
        self._update_ball_element()
        _ratio_type = 'Full'
        # Main Ball
        for main_ball in main_list:
            actionChains  = ActionChains(self.driver)
            actionChains.double_click(self.ball_elements_dict[main_ball]).perform()
            time.sleep(0.5)
        # Sub Ball
        for sub_ball in sub_list:
            self.ball_elements_dict[sub_ball].click()
            time.sleep(0.5)
        if is_full_ratio == False:
            _ratio_type = 'Half'
            self._to_half_ratio()
        self._add_bet()
        logging.info(f'Added bet with {_ratio_type} ratio type:' + 
                'Main Ball:' + str(main_list) +
                'Sub Ball' + str(sub_list))

    def buy_random(self, gaming_type,  num_bet = 1, is_full_ratio = False,**kwargs):
        WebDriverWait(self.odds_menu, 5).until(EC.element_to_be_clickable((By.ID, 'oMenuRANDOM.ASPX'))).click()
        if gaming_type.lower() == 'single':
            WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.ID, 'radioBetTypeSingle'))).click()
        elif gaming_type.lower() == 'multi':
            self.driver.find_element_by_id('radioBetTypeMultiple').click()
            num_ball_selection =  self.driver.find_element_by_id('selectBall')
            num_ball = kwargs['num_ball'] - 7
            if num_ball < 0:
                raise ValueError('In Multi, must be more than 6 numbers')
            num_ball_selection.find_elements_by_xpath('option')[num_ball].click()   
        elif gaming_type.lower() == 'banker':
            self.driver.find_element_by_id('radioBetTypeBanker').click()
            if (kwargs['main_num_ball'] + kwargs['sub_num_ball'] < 7):
                raise ValueError('Main + Sub must be more than 6')
            main_ball_selection = self.driver.find_element_by_id('selectBanker')
            main_ball_selection.find_elements_by_xpath('option')[kwargs['main_num_ball'] - 1].click()
            sub_ball_selection = self.driver.find_element_by_id('selectLeg')
            sub_num_ball =  kwargs['sub_num_ball'] - (7 - kwargs['main_num_ball'])
            sub_ball_selection.find_elements_by_xpath('option')[sub_num_ball].click()
        # Select number of bet
        bet_selection = self.driver.find_element_by_id('selectTotalBetLine')
        bet_selection.find_elements_by_xpath('option')[num_bet - 1].click()
        # Click AutoPickButton
        self.driver.find_element_by_class_name('msAutoPickButton').click()
        # Ratio Control
        if (gaming_type.lower() != 'single') & (is_full_ratio == False):
            for index in range(num_bet):
                self._to_half_ratio(index + 1)
        # Add bet
        self._add_bet()
    
# %%

# %%
