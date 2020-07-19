from .db_conn import get_db_connection,STATIONOWNED_DB_NAME,GAMES_DB_NAME
import scripts.stations as stations
from flask import session
import random
SYMBOLS=[chr(i) for i in range(48,58)]+[chr(i) for i in range(65,91)]+[chr(i) for i in range(97,123)]
def getRandSymbol(length):
    return "".join([random.choice(SYMBOLS) for i in range(length)])
def startGame(players_amount):
    conn = get_db_connection(GAMES_DB_NAME)
    print('a new game created.')

    #summon random and distinct gameid
    while True:
        gameid=getRandSymbol(6)#溢位?
        if conn.execute(f'SELECT * FROM games WHERE id="{gameid}"').fetchall():
            print("summoned the existing gameid. try making a new one....")
            continue
        break
    print('gameid:',gameid)

    #add a new game to sqlite
    cur=conn.cursor()
    cur.execute(f'INSERT INTO games(id,status,players_amount) VALUES("{gameid}","starting",{players_amount})')
    conn.commit()
    conn.close()

    #make brower remember the game
    session['game']=gameid

    #log of owning station
    conn=get_db_connection(STATIONOWNED_DB_NAME)
    conn.executescript(f"""CREATE TABLE {gameid}(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        station TEXT,
                        owner TEXT
                        );""")
    conn.commit()
    conn.close()
def getCurrentGameId():
    return "" if not session['game'] else session['game']

class Game:
    class GameNotFoundError(Exception):
        pass
    def __init__(self,gameid):
        conn=get_db_connection(GAMES_DB_NAME)
        game_info=conn.execute(f'SELECT * FROM games WHERE id="{gameid}"').fetchone()
        conn.close()
        if game_info is None:#game not found
            raise Game.GameNotFoundError(f"game {gameid} not found")
        #self.info=dict(game_info)
        self.gameid=game_info['id']
        self.created_timestamp=game_info['created_timestamp']
        self.started_timestamp=game_info['started_timestamp']
        self.status=game_info['status']
        self.players_amount=game_info['players_amount']
        self.players=Player.getAllplayers(gameid)
        #game_info_dict={'gameid':game_info['id']}


class Player:
    class PlayerNotFoundError(Exception):
        pass
    def __init__(self,id):
        conn=get_db_connection(GAMES_DB_NAME)
        player=conn.execute(f'SELECT * FROM players WHERE id="{id}"').fetchone()
        conn.close()
        if player is None:
            raise  Player.PlayerNotFoundError(f"player with id {id} not found.")
        self.password=player['password']
        self.name=player['name']
        self.gameid=player['gameid']
        self.id=player['id']
    def getEverOwnedStations(self):
        conn=get_db_connection(STATIONOWNED_DB_NAME)
        stations=conn.execute(f'SELECT station FROM {self.gameid} WHERE owner={self.id}').fetchall()
        conn.close()
        return [station[0] for station in stations]
    def getCurrentOwnedStations(self):
        owned_stations=[]
        for station in self.getEverOwnedStations():
            if stations.Station.getOwnerID(station,self.gameid)==self.id:#statoin ower's id==player's id
                owned_stations.append(station)
        print(f'player {self.name} owns {owned_stations}.')
        return owned_stations


    @staticmethod
    def getAllplayers(gameid):
        conn=get_db_connection(GAMES_DB_NAME)
        playerids=conn.execute(f'SELECT id FROM players WHERE gameid="{gameid}"').fetchall()
        conn.close()
        return [Player(playerid[0]) for playerid in playerids]
    @staticmethod
    def getOneplayer(gameid,name):
        players=Player.getAllplayers(gameid)
        player=[player for player in players if player.name==name]
        if player:
            return player[0]#return the only player in the game that matches the givin name
        raise Player.PlayerNotFoundError(f'player with name {name} not found.')


"""
DROP TABLE IF EXIST {gameid}
CREATE TABLE {gameid}(
    station TEXT PRIMARY KEY,
    owner TEXT
);
"""
#datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")