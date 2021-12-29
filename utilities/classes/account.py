from datetime import datetime

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

    def load_account_from_db(self, account_name: str=None) -> int:
        """
        Given an account_name, load the account information from the database and
        store in the object. If the account does not exist, class fields remain
        None and return None.

        account_name: String for account name in the database

        return: int representing the account ID from the database
        """
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

    def create_account(self,
                       account_name: str,
                       account_balance: float,
                       account_email: str="") -> int:
        """
        Check if the account already exists in the database. If the account does not exist,
        create the new account and load to the database.

        account_name: string for the account_name
        account_balance: float value for the balance of the account
        account_email: string for the email associated with the account

        return: Account ID from database
        """
        account_id = self.load_account_from_db(account_name)
        if account_id is not None:
            print(f"[Account] Account with name {self.account_name} already exists")
            return self.account_id

        account_open_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        account_information = (account_name, account_open_datetime, account_balance, account_email)
        db.insert_account(account_information)

        self.account_id = self.load_account_from_db(account_name)
        return self.account_id
        
    def adjust_account_balance(self,
                               amount: float,
                               retries_limit: int=3) -> bool:
        """Update account balance by an amount (new balance = current balance + amount).

        amount: float value to adjust account balance by in the database
        retries_limit: Number of attempts to update account balance in database

        return: bool if operation was a success
        """
        success = False
        retries = 0

        while not success and retries < retries_limit:
            try:
                db.update_account_balance(self.account.account_id, amount)
                success = True
            except Exception as error:
                print(f"Error while adjusting account balance... Attempt {retries + 1}")
                retries += 1

        return success