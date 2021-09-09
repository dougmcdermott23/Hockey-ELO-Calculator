from datetime import datetime

from constants import ErrorCode
from account import Account
import dbutils as db

# TO DO: add a Team class to abstract away some of that information. Will be useful for report generation, etc.

class Trade:
    account = None
    team_id = None
    quantity = None

    def __init__(self, account_name, team_abbreviation, quantity):
        self.account = Account()
        self.account.LoadAccountFromDB(account_name)
        self.team_id = db.GetTeamIdFromTeamNameAbbreviation(team_abbreviation)
        self.quantity = quantity

    # Negative quantity is a purchase, positive quantity is a sale
    def CompleteTrade(self):
        if self.account.account_id is None:
            return False, ErrorCode.ACCOUNT_DOES_NOT_EXIST
        if self.team_id is None:
            return False, ErrorCode.TEAM_DOES_NOT_EXIST

        trade_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        team_rating = db.GetTeamRating(self.team_id)
        trade_value = team_rating * self.quantity

        valid, error = self.IsTradeValid(trade_value)
        if not valid:
            return False, error

        trade_information = (self.account.account_id, self.team_id, self.quantity, trade_datetime)
        if not self.CommitTrade(trade_information):
            return False, ErrorCode.DB_LOAD_TRADE_ERROR
        if not self.account.AdjustAccountBalance(trade_value):
            return False, ErrorCode.DB_ADJUST_BALANCE_ERROR

        self.account.LoadAccountFromDB()
        return True, None

    # Validate trade value and trade quantity does not break account balance and account holdings respectively
    def IsTradeValid(self, trade_value):
        if self.account.account_balance + trade_value < 0:
            return False, ErrorCode.ACCOUNT_BALANCE_NOT_VALID
        if self.quantity < 0 and abs(self.quantity) > db.GetAccountHoldingsForTeam(self.account.account_id, self.team_id):
            return False, ErrorCode.ACCOUNT_HOLDINGS_NOT_VALID
        return True, None

    # Commit trade to database
    def CommitTrade(self, trade_information, retries_limit=3):
        success = False
        retries = 0

        while not success and retries < retries_limit:
            success = db.InsertTrade(trade_information)
            retries += 1

        return success