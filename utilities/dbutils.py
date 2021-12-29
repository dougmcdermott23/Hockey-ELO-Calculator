import psycopg2
import threading

from .config import config

db_lock = threading.Lock()

def execute_and_fetch_all(command: str, args=None) -> list:
    """Execute a SQL command and fetch all the results.

    command: SQL command string
    args: Parameters for SQL command string

    return: list of results
    """
    result = None
    conn = None
    try:
        db_lock.acquire()

        params = config()
        conn = psycopg2.connect(**params)
        
        with conn.cursor() as cur:
            cur.execute(command, args)
            result = cur.fetchall()
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
        db_lock.release()
    return result

def execute_and_fetch_one(command: str, args=None) -> tuple:
    """Execute a SQL command and fetch all the result.

    command: SQL command string
    args: Parameters for SQL command string

    return: tuple containing first result
    """
    result = None
    conn = None
    try:
        db_lock.acquire()

        params = config()
        conn = psycopg2.connect(**params)
        
        with conn.cursor() as cur:
            cur.execute(command, args)
            result = cur.fetchone()
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
        db_lock.release()
    return result

def execute_one(command: str, args=None) -> bool:
    """Execute a SQL command.

    command: SQL command string
    args: Parameters for SQL command string

    return: Return if operation was successful
    """
    success = True

    conn = None
    try:
        db_lock.acquire()

        params = config()
        conn = psycopg2.connect(**params)

        with conn.cursor() as cur:
            cur.execute(command, args)
            conn.commit()
        
    except (Exception, psycopg2.DatabaseError) as error:
        success = False
        print(error)
    finally:
        if conn is not None:
            conn.close()
        db_lock.release()

    return success

def execute_many(command: str, args) -> bool:
    """Execute a SQL command against all all parameter sequences.

    command: SQL command string
    args: Parameter sequences for SQL command string

    return: Return if operation was successful
    """
    success = True

    conn = None
    try:
        db_lock.acquire()

        params = config()
        conn = psycopg2.connect(**params)

        with conn.cursor() as cur:
            cur.executemany(command, args)
        
        conn.commit()
        
    except (Exception, psycopg2.DatabaseError) as error:
        success = False
        print(error)
    finally:
        if conn is not None:
            conn.close()
        db_lock.release()

    return success

def initialize_database_schema(sql_file: str = "schema.sql") -> bool:
    """Schema initialization
    """
    sql_file = open(sql_file, "r")
    command = sql_file.read()
    return execute_one(command)

"""
TEAM
"""
def initialize_team_ratings(rating: float) -> bool:
    """Initialize all team ratings to a value.
    """
    command = f'''UPDATE team 
                  SET current_rating = {rating}'''
    return execute_one(command)

def update_team_ratings(team_ratings: dict) -> bool:
    """Update team ratings given a dictionary where the key is the team and value is
    the corresponding rating.
    """
    command = '''UPDATE team 
                 SET current_rating = %s 
                 WHERE team_name_abbreviation = %s'''
    args = []
    for team, rating in team_ratings.items():
        args.append([rating, team])
    return execute_many(command, args)

def get_team_ratings() -> dict:
    """Return a dictionary where the key is the team and value is the corresponding
    rating.
    """
    dict = {}
    team_ratings = execute_and_fetch_all(f'''SELECT team_name_abbreviation, current_rating 
                                             FROM team 
                                             ORDER BY team_name_abbreviation''')
    for team in team_ratings:
        dict[team[0]] = team[1]
    return dict

def get_team_rating(team_id: int) -> float:
    """Given a team ID, return the corrseponding rating.
    """
    rating = execute_and_fetch_one(f'''SELECT current_rating 
                                       FROM team 
                                       WHERE team_id = {team_id}''')
    return rating[0] if rating is not None else None

def get_team_name_information() -> dict:
    """Return a dictionary where the key is the team abbreviation and the value is the
    corresponding full name.
    """
    dict = {}
    teams = execute_and_fetch_all(f'''SELECT team_name_abbreviation, team_name 
                                      FROM team 
                                      ORDER BY team_name_abbreviation''')
    for team in teams:
        dict[team[0]] = team[1]
    return dict

def get_team_id_from_team_name_abbrevation(abbreviation: str) -> int:
    """Given a team abbreviation, return the corresponding team ID.
    """
    result = execute_and_fetch_one(f'''SELECT team_id 
                                     FROM team 
                                     WHERE team_name_abbreviation = \'{abbreviation}\'''')
    return result[0] if result is not None else None

def is_team_valid(abbreviation: str) -> bool:
    """Return if team abbreviation is valid
    """
    result = execute_and_fetch_all(f'''SELECT 1 
                                       FROM team 
                                       WHERE team_name_abbreviation = \'{abbreviation}\'''')
    return result is not None and len(result) > 0

"""
SEASON UPDATE
"""
def has_season_update_occurred(season_update_id: int) -> bool:
    """Return if an update has occurred for a given season ID.
    """
    result = execute_and_fetch_all(f'''SELECT 1 
                                       FROM season_update 
                                       WHERE season_update_id = \'{season_update_id}\'''')
    return result is not None and len(result) > 0

def insert_season_update_entry(season_update_id: int, update_date: str) -> bool:
    """Insert a season ID and update date to the database and return if success.
    """
    command = '''INSERT INTO season_update (season_update_id, update_date)
                 VALUES (%s, %s)'''
    args = (season_update_id, update_date)
    return execute_one(command, args)

"""
GAME
"""
def get_last_game_date() -> str:
    """Return the last date a game was inserted into the database.
    """
    result = execute_and_fetch_one(f'''SELECT MAX(game_date) 
                                       FROM game''')
    return result[0] if result is not None else None

def insert_game_data(game_data: list) -> bool:
    """Insert a list of games into the database.
    """
    command = '''INSERT INTO game (season_id, game_type, game_number, 
                                   game_date, start_time, venue, 
                                   home_team, away_team, home_score, 
                                   away_score, game_status, home_rating_start, 
                                   home_rating_end, away_rating_start, away_rating_end) 
                  VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
    return execute_many(command, game_data)

"""
ACCOUNT
"""
def get_account_information_from_account_name(account_name: str) -> dict:
    """Return account information for given account name.
    """
    command = f'''SELECT account_id, account_name, account_open_datetime, 
                       account_balance, account_email 
                  FROM account WHERE account_name = \'{account_name}\''''
    result = execute_and_fetch_one(command)
    if result is None or len(result) < 5:
        return None

    account_information = {
        'account_id' : result[0],
        'account_name' : result[1],
        'account_open_datetime' : result[2],
        'account_balance' : result[3],
        'account_email' : result[4]
    }
    return account_information

def insert_account(account_information: tuple) -> bool:
    """Insert an account into the database.
    """
    command = '''INSERT INTO account (account_name, account_open_datetime, 
                                      account_balance, account_email)
                 VALUES (%s, %s, %s, %s)'''
    return execute_one(command, account_information)

def update_account_balance(account_id: int, amount: float) -> bool:
    """Update an accounts balance.
    """
    command = f'''UPDATE account 
                  SET account_balance = account_balance + {amount} 
                  WHERE account_id = {account_id}'''
    return execute_one(command)

"""
TRADE
"""
def insert_trade(trade_information: tuple) -> bool:
    """Insert a trade into the database.
    """
    command = '''INSERT INTO trade (account_id, team_id, 
                                    trade_quantity, trade_datetime)
                 VALUES (%s, %s, %s, %s)'''
    return execute_one(command, trade_information)

def get_account_holdings_for_team(account_id: int, team_id: int) -> float:
    """Return the account holdings for a given account ID and team ID pair.
    """
    command = f'''SELECT SUM(trade_quantity) 
                  FROM trade 
                  WHERE account_id = {account_id} AND team_id = {team_id}'''
    result =  execute_and_fetch_one(command)
    return result[0] if result is not None else None