from datetime import datetime

from account import Account
import dbutils as db

# TODO: add a Team class to abstract away some of that information. Will be useful for report generation, etc.

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

    def complete_trade(self) -> bool:
        """Complete and check if all trade information is valid. Commit the trade information
        to the database and update the accounts balance to reflect the trade. Negative quantity
        is a purchase, a positive quantity is a sale.

        return: If the trade was a success
        """
        if self.account.account_id is None:
            return False
        if self.team_id is None:
            return False

        trade_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        team_rating = db.get_team_rating(self.team_id)
        trade_value = team_rating * self.quantity

        valid = self.is_trade_valid(trade_value)
        if not valid:
            return False

        trade_information = (self.account.account_id, self.team_id, self.quantity, trade_datetime)
        if not self.commit_trade(trade_information):
            return False
        if not self.account.adjust_account_balance(trade_value):
            return False

        self.account.load_account_from_db()
        return True

    def is_trade_valid(self, trade_value: float) -> bool:
        """Validate the trade value and trade quantity do not break the account balance
        and account holdings respectively.

        trade_value: Equivalent to the trade quantity * current team_rating

        return: If the trade is valid
        """
        if self.account.account_balance + trade_value < 0:
            return False
        if self.quantity < 0 and abs(self.quantity) > db.get_account_holdings_for_team(self.account.account_id, self.team_id):
            return False
        return True

    def commit_trade(self,
                     trade_information: tuple,
                     retries_limit: int=3) -> bool:
        """Commit trade to the database.

        trade_information: Information for trade (Account ID: int, Team ID: int, Quantity: int, Datetime: str)
        retries_limit: Number of attempts to commit the trade

        return: If the trade was successfully commited
        """
        success = False
        retries = 0

        while not success and retries < retries_limit:
            try:
                db.insert_trade(trade_information)
                success = True
            except Exception as error:
                print(f"Error while committing trade... Attempt {retries + 1}")
                retries += 1 

        return success