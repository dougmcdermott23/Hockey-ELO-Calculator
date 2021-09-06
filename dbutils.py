import psycopg2
from config import Config

def ExecuteAndFetchAll(command):
    result = None
    conn = None
    try:
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
    return result

def ExecuteAndFetchOne(command):
    result = None
    conn = None
    try:
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
    return result

def ExecuteOne(command, args=None):
    success = True

    conn = None
    try:
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

    return success

def ExecuteMany(command, args):
    success = True

    conn = None
    try:
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

    return success

def GetTeamNameInformation():
    dict = {}
    teams = ExecuteAndFetchAll(f"SELECT team_name_abbreviation, team_name FROM team ORDER BY team_name_abbreviation")
    for team in teams:
        dict[team[0]] = team[1]
    return dict

def GetTeamRatings():
    dict = {}
    team_ratings = ExecuteAndFetchAll(f"SELECT team_name_abbreviation, current_rating FROM team ORDER BY team_name_abbreviation")
    for team in team_ratings:
        dict[team[0]] = team[1]
    return dict

def IsTeamValid(abbreviation):
    result = ExecuteAndFetchAll(f"SELECT 1 FROM team WHERE team_name_abbreviation = '{abbreviation}'")
    return result is not None and len(result) > 0

def HasSeasonUpdateOccurred(season_update_id):
    result = ExecuteAndFetchAll(f"SELECT 1 FROM season_update WHERE season_update_id = '{season_update_id}'")
    return result is not None and len(result) > 0

def InsertSeasonUpdateEntry(season_update_id, update_date):
    command = '''INSERT INTO season_update (season_update_id, update_date)
                    VALUES (%s, %s)'''
    args = (season_update_id, update_date)
    return ExecuteOne(command, args)

def GetLastGameDate():
    result = ExecuteAndFetchOne(f"Select MAX(game_date) FROM game")
    return result

def LoadGameData(game_data):
    command = '''INSERT INTO game (season_id, game_type, game_number, game_date, start_time, venue, home_team, away_team, home_score, away_score, game_status, home_rating_start, home_rating_end, away_rating_start, away_rating_end)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
    args = game_data
    return ExecuteMany(command, args)

def InitializeTeamRatings(rating):
    command = f'UPDATE team SET current_rating = {rating}'
    return ExecuteOne(command)

def UpdateTeamRatings(team_ratings):
    command = '''UPDATE team SET current_rating = %s WHERE team_name_abbreviation = %s'''
    args = []
    for team, rating in team_ratings.items():
        args.append([rating, team])
    return ExecuteMany(command, args)

def InitializeDatabaseSchema():
    sql_file = open('schema.sql', 'r')
    command = sql_file.read()
    return ExecuteOne(command)