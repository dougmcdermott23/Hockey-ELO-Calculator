from datetime import datetime

from constants import ErrorCode
import dbutils as db

class Account:
    account_id = None
    account_name = None
    account_open_datetime = None
    account_balance = None
    account_email = None
    loaded = False

    def __init__(self):
        self.ResetAccountInformation()

    def ResetAccountInformation(self):
            self.account_id = None
            self.account_name = None
            self.account_open_datetime = None
            self.account_balance = None
            self.account_email = None
            self.loaded = False

    # If account exists in database set class fields, else reset class fields to None
    def LoadAccountFromDB(self, account_name=None):
        if account_name is None:
            account_name = self.account_name

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

    # Create a new account if one does not already exist with that account name
    def CreateAccount(self, account_name, account_balance, account_email=''):
        account_id = self.LoadAccountFromDB(account_name)
        if account_id is not None:
            print(f"[Account] Account with name {self.account_name} already exists")
            return self.account_id, ErrorCode.ACCOUNT_ALREADY_EXISTS

        account_open_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        account_information = (account_name, account_open_datetime, account_balance, account_email)
        db.InsertAccount(account_information)

        self.account_id = self.LoadAccountFromDB(account_name)
        return self.account_id, None

    # Update account balance by an amount (new balance = current balance + amount)
    def AdjustAccountBalance(self, amount, retries_limit=3):
        success = False
        retries = 0

        while not success and retries < retries_limit:
            success = db.UpdateAccountBalance(self.account.account_id, amount)
            retries += 1

        return success