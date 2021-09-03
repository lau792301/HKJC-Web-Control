import logging
import ast
import calendar
import requests
import json
import datetime

from bs4 import BeautifulSoup
from typing import Dict, List, Any


class AutobetAgent(object):
    def __init__(self, username, password, hint_response, race_date, race_course):
        self.race_date = race_date
        self.dow = calendar.day_abbr[datetime.datetime.strptime(self.race_date, '%d-%m-%Y').weekday()].upper()
        self.race_course = race_course.upper()

        # For betting API
        self.username = username
        self.password = password
        self.hint_response = hint_response

        self.URL_DoGetSID = "https://txn02.hkjc.com/BetSlipIB/services/Sid.svc/DoGetSID"
        self.URL_DoAuthentAccPwd = "https://txn02.hkjc.com/BetSlipIB/services/Login.svc/DoAuthentAccPwd"
        self.URL_DoAuthentEKBA = "https://txn02.hkjc.com/BetSlipIB/services/LoginEkba.svc/DoAuthentEKBA"
        self.URL_DoSendBet = "https://txn02.hkjc.com/BetSlipIB/services/SendBet.svc/DoSendBet"
        self.URL_ExtendSession = "https://txn02.hkjc.com/BetSlipIB/services/Session.svc/ExtendSession"
        self.URL_DoBalance = "https://txn02.hkjc.com/BetSlipIB/services/Balance.svc/DoBalance"
        self.headers = {
            "Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/61.0.3163.100 Safari/537.36",
            "Content-Type": "application/json",
            "Accept": "application/json, text/javascript, */*; q=0.01"
        }
        self.account = None
        self.guid = None
        self.sid = None
        self.seq_no = None
        self.ekbaID = None
        self.hWebID = None
        self.sso_guid = None
        self.account_balance = None
        self.session = None

    def init_session(self):
        """ Establish connection to HKJC betting API
        """
        self.session = requests.Session()
        self.session.headers.update(self.headers)

        # -------------------------------------------------
        # DoGetSID
        # -------------------------------------------------
        sid = self.session.post(self.URL_DoGetSID)

        soup = BeautifulSoup(sid.content, "lxml")
        sid_return = soup.find('p').getText()
        sid_return = json.loads(sid_return)

        self.guid = sid_return['DoGetSIDResult'][2]['Value']
        self.sid = sid_return['DoGetSIDResult'][1]['Value']

        # -------------------------------------------------
        # DoAuthentAccPwd
        # -------------------------------------------------
        data_payload = {
            "acc": self.username,
            "guid": self.guid,
            "lang": 0,
            "pass": self.password,
            "sid": self.sid,
            "toVerifyPassword": False
        }

        authentpwd = self.session.post(self.URL_DoAuthentAccPwd,
                                       data=json.dumps(data_payload))
        soup = BeautifulSoup(authentpwd.content, "lxml")
        doauth_return = soup.find('p').getText()
        doauth_return = json.loads(doauth_return)

        ekbaQ = None
        for v in doauth_return['DoAuthentAccPwdResult']:
            if v["Key"] == "ekbaID":
                self.ekbaID = v["Value"]
            elif v["Key"] == "account":
                self.account = v["Value"]
            elif v["Key"] == "hWebID":
                self.hWebID = v["Value"]
            elif v["Key"] == "ekbaQ":
                ekbaQ = v["Value"]

        ekba_ans = self.hint_response.get(ekbaQ)

        # -------------------------------------------------
        # DoAuthentEKBA
        # -------------------------------------------------
        do_auth_ekba_payload = {
            "lang": 0,
            "answer": ekba_ans,
            "os": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/61.0.3163.100 Safari/537.36",
            "ekbaLang": "TradChi",
            "ekbaId": self.ekbaID,
            "sid": self.sid,
            "guid": self.guid,
            "acc": self.account,
            "webId": self.username,
            "knownSSOGUID": "",
            "hWebId": self.hWebID,
            "seq": None
        }

        authentekba = self.session.post(self.URL_DoAuthentEKBA, data=json.dumps(do_auth_ekba_payload))

        soup = BeautifulSoup(authentekba.content, "lxml")
        doauthekba_return = soup.find('p').getText()
        doauthekba_return = ast.literal_eval(doauthekba_return)

        all_keys = {item["Key"] for item in doauthekba_return['DoAuthentEKBAResult']}
        if "sso_guid" not in all_keys:
            return False

        for item in doauthekba_return['DoAuthentEKBAResult']:
            if item['Key'] == 'seq_no':
                self.seq_no = int(item['Value'])
            elif item['Key'] == 'sso_guid':
                self.sso_guid = item['Value']

        if sid.status_code == 200 and authentekba.status_code == 200 and authentekba.status_code == 200:
            logging.info('Login successful')
            return True
        else:
            logging.error("Login failed")
            return False

    def make_bet(self, bet_line: str) -> bool:
        """ Making bet_utils

        Args:
            bet_line: Form data required by HKJC API

        Returns:
            Boolean execution status

        """
        bet_input = {
            "betlines": bet_line,
            "lang": 0,
            "delayReq": 0,
            "password": "",
            "sid": self.sid,
            "guid": self.guid,
            "acc": self.account,
            "knownSSOGUID": self.sso_guid,
            "knownWebID": self.username,
            "seqNo": self.seq_no + 1
        }
        self.seq_no += 1

        r = self.session.post(self.URL_DoSendBet, data=json.dumps(bet_input))
        if r.status_code == 200:
            logging.info("Bet made successfully")
            return True
        else:
            logging.error("Bet failed")
            return False

    def extend_session(self):
        """ Extending current session
        """
        extend_session_input = {"acc": self.account, "seqNo": self.seq_no}
        r = self.session.post(self.URL_ExtendSession, data=json.dumps(extend_session_input))
        self.seq_no += 1
        if r.status_code == 200:
            logging.info("Successfully extended session")
            return True
        else:
            logging.error("Error in extending session")
            return False

    def generate_betline(self,
                         bets_dict: Dict[str, List[Any]],
                         current_race: int,
                         bet_size: int = 10,
                         delimiter: str = '-'
                         ) -> List[str]:
        """ Generate bet-line format required by HKJC API

        Args:
            bets_dict: Betting allocated
                Format is {"bet_size": [], "combinations": [], "pools": []}
            current_race: Current race no
            bet_size: Betting size, default to be $10 per bet
            delimiter: Separator of horse number

        Returns:
            List of betlines

        """
        betline_list = list()

        for c, b, p in zip(bets_dict["combinations"],
                           bets_dict["bet_size"],
                           bets_dict["pools"]):
            if b < 1:
                continue
            bet_placed = int(b * bet_size)
            if p in ["QIN", "QPL"]:
                horse_1, horse_2 = c.split(delimiter)
                betline = f"{self.race_course} {self.dow} {p} " \
                          f"{current_race}*{horse_1}+{horse_2} ${bet_placed}\\"
            elif p in ["WIN", "PLA"]:
                betline = f"{self.race_course} {self.dow} {p} " \
                          f"{current_race}*{c} ${bet_placed}\\"
            elif p == "TRI":
                horse_1, horse_2, horse_3 = c.split(delimiter)
                betline = f"{self.race_course} {self.dow} {p} " \
                          f"{current_race}*{horse_1}+{horse_2}+{horse_3} ${bet_placed}\\"
            elif p == "FOUR":
                horse_1, horse_2, horse_3, horse_4 = c.split(delimiter)
                betline = f"{self.race_course} {self.dow} {p} " \
                          f"{current_race}*{horse_1}+{horse_2}+{horse_3}+{horse_4} ${bet_placed}\\"
            else:
                raise ValueError('Pool not supported')
            betline_list.append(betline)
        return betline_list