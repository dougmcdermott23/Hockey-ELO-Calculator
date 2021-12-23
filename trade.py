from datetime import datetime

from constants import ErrorCode
from account import Account
import dbutils as db

# TO DO: add a Team class to abstract away some of that information. Will be useful for report generation, etc.

class Trade:
    account_name: str
    team_abbreviation: str
    quantity: int

    def __init__(self,
                 account_name: str,
                 team_abbreviation: str, 
                 quantity: int) -> None:
        self.account = Account(account_name=account_name)
        self.team_id = db.get_team_id_from_team_name_abbrevation(team_abbreviation)
        self.quantity = quantity

    # Negative quantity is a purchase, positive quantity is a sale
    def complete_trade(self):
        if self.account.account_id is None:
            return False, ErrorCode.ACCOUNT_DOES_NOT_EXIST
        if self.team_id is None:
            return False, ErrorCode.TEAM_DOES_NOT_EXIST

        trade_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        team_rating = db.get_team_rating(self.team_id)
        trade_value = team_rating * self.quantity

        valid, error = self.is_trade_valid(trade_value)
        if not valid:
            return False, error

        trade_information = (self.account.account_id, self.team_id, self.quantity, trade_datetime)
        if not self.commit_trade(trade_information):
            return False, ErrorCode.DB_LOAD_TRADE_ERROR
        if not self.account.adjust_account_balance(trade_value):
            return False, ErrorCode.DB_ADJUST_BALANCE_ERROR

        self.account.load_account_from_db()
        return True, None

    # Validate trade value and trade quantity does not break account balance and account holdings respectively
    def is_trade_valid(self, trade_value: float):
        if self.account.account_balance + trade_value < 0:
            return False, ErrorCode.ACCOUNT_BALANCE_NOT_VALID
        if self.quantity < 0 and abs(self.quantity) > db.get_account_holdings_for_team(self.account.account_id, self.team_id):
            return False, ErrorCode.ACCOUNT_HOLDINGS_NOT_VALID
        return True, None

    # Commit trade to database
    def commit_trade(self, trade_information: tuple(int, int, int, str), retries_limit: int=3) -> bool:
        success = False
        retries = 0

        while not success and retries < retries_limit:
            success = db.insert_trade(trade_information)
            retries += 1

        return success