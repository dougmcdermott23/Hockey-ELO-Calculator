import psycopg2
import threading

from config import Config

db_lock = threading.Lock()

def ExecuteAndFetchAll(command):
    result = None
    conn = None
    try:
        db_lock.acquire()

        params = Config()
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

def ExecuteAndFetchOne(command):
    result = None
    conn = None
    try:
        db_lock.acquire()

        params = Config()
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

def ExecuteOne(command, args=None):
    success = True

    conn = None
    try:
        db_lock.acquire()

        params = Config()
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

def ExecuteMany(command, args):
    success = True

    conn = None
    try:
        db_lock.acquire()

        params = Config()
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
def InitializeDatabaseSchema():
    sql_file = open('schema.sql', 'r')
    command = sql_file.read()
    return ExecuteOne(command)

# team
def InitializeTeamRatings(rating):
    command = f'UPDATE team SET current_rating = {rating}'
    return ExecuteOne(command)

def UpdateTeamRatings(team_ratings):
    command = '''UPDATE team SET current_rating = %s WHERE team_name_abbreviation = %s'''
    args = []
    for team, rating in team_ratings.items():
        args.append([rating, team])
    return ExecuteMany(command, args)

def GetTeamRatings():
    dict = {}
    team_ratings = ExecuteAndFetchAll(f"SELECT team_name_abbreviation, current_rating FROM team ORDER BY team_name_abbreviation")
    for team in team_ratings:
        dict[team[0]] = team[1]
    return dict

def GetTeamRating(team_id):
    rating = ExecuteAndFetchOne(f"SELECT current_rating FROM team WHERE team_id = {team_id}")
    return rating[0] if rating is not None else None

def GetTeamNameInformation():
    dict = {}
    teams = ExecuteAndFetchAll(f"SELECT team_name_abbreviation, team_name FROM team ORDER BY team_name_abbreviation")
    for team in teams:
        dict[team[0]] = team[1]
    return dict

def GetTeamIdFromTeamNameAbbreviation(abbreviation):
    result = ExecuteAndFetchOne(f"SELECT team_id FROM team WHERE team_name_abbreviation = '{abbreviation}'")
    return result[0] if result is not None else None

def IsTeamValid(abbreviation):
    result = ExecuteAndFetchAll(f"SELECT 1 FROM team WHERE team_name_abbreviation = '{abbreviation}'")
    return result is not None and len(result) > 0

# season_update
def HasSeasonUpdateOccurred(season_update_id):
    result = ExecuteAndFetchAll(f"SELECT 1 FROM season_update WHERE season_update_id = '{season_update_id}'")
    return result is not None and len(result) > 0

def InsertSeasonUpdateEntry(season_update_id, update_date):
    command = '''INSERT INTO season_update (season_update_id, update_date)
                    VALUES (%s, %s)'''
    args = (season_update_id, update_date)
    return ExecuteOne(command, args)

# game
def GetLastGameDate():
    result = ExecuteAndFetchOne(f"Select MAX(game_date) FROM game")
    return result[0] if result is not None else None

def InsertGameData(game_data):
    command = '''INSERT INTO game (season_id, game_type, game_number, game_date, start_time, venue, home_team, away_team, home_score, away_score, game_status, home_rating_start, home_rating_end, away_rating_start, away_rating_end)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
    return ExecuteMany(command, game_data)

# account
def GetAccountInformationFromAccountName(account_name):
    command = f"SELECT account_id, account_name, account_open_datetime, account_balance, account_email FROM account WHERE account_name = '{account_name}'"
    result = ExecuteAndFetchOne(command)
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

def InsertAccount(account_information):
    command = '''INSERT INTO account (account_name, account_open_datetime, account_balance, account_email)
                    VALUES (%s, %s, %s, %s)'''
    return ExecuteOne(command, account_information)

def UpdateAccountBalance(account_id, amount):
    command = f"UPDATE account SET account_balance = account_balance + {amount} WHERE account_id = {account_id}"
    return ExecuteOne(command)

# trade
def InsertTrade(trade_information):
    command = '''INSERT INTO trade (account_id, team_id, trade_quantity, trade_datetime)
                    VALUES (%s, %s, %s, %s)'''
    return ExecuteOne(command, trade_information)

def GetAccountHoldingsForTeam(account_id, team_id):
    command = f"SELECT SUM(trade_quantity) FROM trade WHERE account_id = {account_id} AND team_id = {team_id}"
    result =  ExecuteAndFetchOne(command)
    return result[0] if result is not None else None