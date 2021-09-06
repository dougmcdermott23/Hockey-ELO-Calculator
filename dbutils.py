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
    return result is not None

def HasSeasonUpdateOccurred(season_update_id):
    result = ExecuteAndFetchAll(f"SELECT 1 FROM season_update WHERE season_update_id = '{season_update_id}'")
    return result is not None

def InsertSeasonUpdateEntry(season_update_id, update_date):
    conn = None
    try:
        params = Config()
        conn = psycopg2.connect(**params)

        with conn.cursor() as cur:
            command = f'''INSERT INTO season_update (season_update_id, update_date)
                            VALUES (%s, %s)'''
            cur.execute(command, (season_update_id, update_date))
            conn.commit()
        
    except (Exception, psycopg2.DatabaseError) as error:
        success = False
        print(error)
    finally:
        if conn is not None:
            conn.close()

def GetLastGameDate():
    result = ExecuteAndFetchOne(f"Select MAX(game_date) FROM game")
    return result

def LoadGameData(game_data):
    success = True

    conn = None
    try:
        params = Config()
        conn = psycopg2.connect(**params)

        with conn.cursor() as cur:
            command = '''INSERT INTO game (season_id, game_type, game_number, game_date, start_time, venue, home_team, away_team, home_score, away_score, game_status, home_rating_start, home_rating_end, away_rating_start, away_rating_end)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
            cur.executemany(command, game_data)
        
        conn.commit()
        
    except (Exception, psycopg2.DatabaseError) as error:
        success = False
        print(error)
    finally:
        if conn is not None:
            conn.close()

    return success

def InitializeTeamRatings(rating):
    conn = None
    try:
        params = Config()
        conn = psycopg2.connect(**params)

        with conn.cursor() as cur:
            command = f'UPDATE team SET current_rating = {rating}'
            cur.execute(command)
            conn.commit()
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def UpdateTeamRatings(team_ratings):
    success = True

    conn = None
    try:
        params = Config()
        conn = psycopg2.connect(**params)

        with conn.cursor() as cur:
            for team, rating in team_ratings.items():
                command = '''UPDATE team
                                SET current_rating = %s
                                WHERE team_name_abbreviation = %s'''
                cur.execute(command, (rating, team))
                conn.commit()
        
    except (Exception, psycopg2.DatabaseError) as error:
        success = False
        print(error)
    finally:
        if conn is not None:
            conn.close()

    return success

def InitializeDatabaseSchema():
    conn = None
    try:
        params = Config()
        conn = psycopg2.connect(**params)

        with conn.cursor() as cur:
            sql_file = open('schema.sql', 'r')
            cur.execute(sql_file.read())

        conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()