import psycopg2
import threading

from config import config

db_lock = threading.Lock()

def execute_and_fetch_all(command: str) -> list:
    result = None
    conn = None
    try:
        db_lock.acquire()

        params = config()
        conn = psycopg2.connect(**params)
        
        with conn.cursor() as cur:
            cur.execute(command)
            result = cur.fetchall()
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
        db_lock.release()
    return result

def execute_and_fetch_one(command: str) -> tuple:
    result = None
    conn = None
    try:
        db_lock.acquire()

        params = config()
        conn = psycopg2.connect(**params)
        
        with conn.cursor() as cur:
            cur.execute(command)
            result = cur.fetchone()
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
        db_lock.release()
    return result

def execute_one(command: str, args=None) -> bool:
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

# Schema initialization
def initialize_database_schema() -> bool:
    sql_file = open("schema.sql", "r")
    command = sql_file.read()
    return execute_one(command)

# team
def initialize_team_ratings(rating: float) -> bool:
    command = f'UPDATE team SET current_rating = {rating}'
    return execute_one(command)

def update_team_ratings(team_ratings: dict) -> bool:
    command = '''UPDATE team SET current_rating = %s WHERE team_name_abbreviation = %s'''
    args = []
    for team, rating in team_ratings.items():
        args.append([rating, team])
    return execute_many(command, args)

def get_team_ratings() -> dict:
    dict = {}
    team_ratings = execute_and_fetch_all(f"SELECT team_name_abbreviation, current_rating FROM team ORDER BY team_name_abbreviation")
    for team in team_ratings:
        dict[team[0]] = team[1]
    return dict

def get_team_rating(team_id: int) -> float:
    rating = execute_and_fetch_one(f"SELECT current_rating FROM team WHERE team_id = {team_id}")
    return rating[0] if rating is not None else None

def get_team_name_information() -> dict:
    dict = {}
    teams = execute_and_fetch_all(f"SELECT team_name_abbreviation, team_name FROM team ORDER BY team_name_abbreviation")
    for team in teams:
        dict[team[0]] = team[1]
    return dict

def get_team_id_from_team_name_abbrevation(abbreviation: str) -> int:
    result = execute_and_fetch_one(f"SELECT team_id FROM team WHERE team_name_abbreviation = '{abbreviation}'")
    return result[0] if result is not None else None

def is_team_valid(abbreviation: str) -> bool:
    result = execute_and_fetch_all(f"SELECT 1 FROM team WHERE team_name_abbreviation = '{abbreviation}'")
    return result is not None and len(result) > 0

# season_update
def has_season_update_occurred(season_update_id: int) -> bool:
    result = execute_and_fetch_all(f"SELECT 1 FROM season_update WHERE season_update_id = '{season_update_id}'")
    return result is not None and len(result) > 0

def insert_season_update_entry(season_update_id: int, update_date: str) -> bool:
    command = '''INSERT INTO season_update (season_update_id, update_date)
                    VALUES (%s, %s)'''
    args = (season_update_id, update_date)
    return execute_one(command, args)

# game
def get_last_game_date() -> str:
    result = execute_and_fetch_one(f"Select MAX(game_date) FROM game")
    return result[0] if result is not None else None

def insert_game_data(game_data: list) -> bool:
    command = '''INSERT INTO game (season_id, game_type, game_number, game_date, start_time, venue, home_team, away_team, home_score, away_score, game_status, home_rating_start, home_rating_end, away_rating_start, away_rating_end)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
    return execute_many(command, game_data)

# account
def get_account_information_from_account_name(account_name: str) -> dict:
    command = f"SELECT account_id, account_name, account_open_datetime, account_balance, account_email FROM account WHERE account_name = '{account_name}'"
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
    command = '''INSERT INTO account (account_name, account_open_datetime, account_balance, account_email)
                    VALUES (%s, %s, %s, %s)'''
    return execute_one(command, account_information)

def update_account_balance(account_id: int, amount: float) -> bool:
    command = f"UPDATE account SET account_balance = account_balance + {amount} WHERE account_id = {account_id}"
    return execute_one(command)

# trade
def insert_trade(trade_information: tuple) -> bool:
    command = '''INSERT INTO trade (account_id, team_id, trade_quantity, trade_datetime)
                    VALUES (%s, %s, %s, %s)'''
    return execute_one(command, trade_information)

def get_account_holdings_for_team(account_id: int, team_id: int) -> float:
    command = f"SELECT SUM(trade_quantity) FROM trade WHERE account_id = {account_id} AND team_id = {team_id}"
    result =  execute_and_fetch_one(command)
    return result[0] if result is not None else None