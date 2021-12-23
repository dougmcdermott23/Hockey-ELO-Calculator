from datetime import datetime

from constants import ErrorCode
import dbutils as db

class Account:
    account_id: int
    account_name: str
    account_open_datetime: str
    account_balance: float
    account_email: str
    loaded: bool 

    def __init__(self) -> None:
        self.reset_account_information()

    def __init(self, account_name: str) -> None:
        self.reset_account_information()
        self.load_account_from_db(account_name)

    def reset_account_information(self) -> None:
        self.account_id: int = None
        self.account_name: str = None
        self.account_open_datetime: str = None
        self.account_balance: float = None
        self.account_email: str = None
        self.loaded: bool = False

    # If account exists in database set class fields, else reset class fields to None
    def load_account_from_db(self, account_name: str=None) -> int:
        if account_name is None:
            account_name = self.account_name

        self.reset_account_information()

        account_information = db.get_account_information_from_account_name(account_name)
        if account_information is not None:
            self.account_id = account_information['account_id']
            self.account_name = account_information['account_name']
            self.account_open_datetime = account_information['account_open_datetime']
            self.account_balance = account_information['account_balance']
            self.account_email = account_information['account_email']
            self.loaded = True
        
        return self.account_id

    # Create a new account if one does not already exist with that account name
    def create_account(self, account_name: str, account_balance: float, account_email: str=""):
        account_id = self.load_account_from_db(account_name)
        if account_id is not None:
            print(f"[Account] Account with name {self.account_name} already exists")
            return self.account_id, ErrorCode.ACCOUNT_ALREADY_EXISTS

        account_open_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        account_information = (account_name, account_open_datetime, account_balance, account_email)
        db.insert_account(account_information)

        self.account_id = self.load_account_from_db(account_name)
        return self.account_id, None

    # Update account balance by an amount (new balance = current balance + amount)
    def adjust_account_balance(self, amount: float, retries_limit: int=3):
        success = False
        retries = 0

        while not success and retries < retries_limit:
            success = db.update_account_balance(self.account.account_id, amount)
            retries += 1

        return success