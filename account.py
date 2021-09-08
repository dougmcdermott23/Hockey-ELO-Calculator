from datetime import datetime

from constants import ErrorCode
import dbutils as db

class Account:
    def __init__(self):
        self.ResetAccountInformation()

    def ResetAccountInformation(self):
            self.account_id = None
            self.account_name = None
            self.account_open_datetime = None
            self.account_balance = None
            self.account_email = None
            self.loaded = False

    def LoadAccountFromDB(self, account_name):
        self.ResetAccountInformation()

        account_information = db.GetAccountInformationFromAccountName(account_name)
        if account_information is not None:
            self.account_id = account_information['account_id']
            self.account_name = account_information['account_name']
            self.account_open_datetime = account_information['account_open_datetime']
            self.account_balance = account_information['account_balance']
            self.account_email = account_information['account_email']
            self.loaded = True
        
        return self.account_id

    def CreateAccount(self, account_name, account_balance, account_email=''):
        account_id = self.LoadAccountFromDB(account_name)
        if account_id is not None:
            print(f"[Account] Account with name {self.account_name} already exists")
            return self.account_id, ErrorCode.ACCOUNT_ALREADY_EXISTS

        account_open_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        account_information = (account_name, account_open_datetime, account_balance, account_email)
        db.CreateNewAccount(account_information)

        self.account_id = self.LoadAccountFromDB(account_name)

        return self.account_id, None