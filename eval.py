import socketio
import json
from sys import argv, exit
import time
from signal import signal, SIGINT


USERNAME = "eval"
GAME_NAME_DEFAULT = "a"
URL = "http://localhost:3331/"

class Client:
    def main(self):
        # set up kill function
        signal(SIGINT, self.kill)

        if len(argv) == 3:
            self.game_name = argv[1]
            self.session_name = argv[2]
        elif len(argv) == 2:
            self.game_name = argv[1]
            self.session_name = str(round(time.time()))
        else:
            self.game_name = GAME_NAME_DEFAULT
            self.session_name = str(round(time.time()))

        # load sessions
        self.sessions = self.loadSessions()
        if self.session_name in self.sessions.keys():
            raise Exception(f"Existing session with name \"{ self.session_name }\"")
        self.current_session = []

        # connect to server
        self.sio = socketio.Client()
        self.sio.connect(URL + self.game_name)
        
        # connect to game
        self.sio.emit('game_connection', (self.game_name, USERNAME))

        print('connected to server')

        self.started = False

        # process new game states
        @self.sio.on('game_state')
        def onGameState(game_state):
            if len(game_state['players']) == 4:
                if not self.started:  # we are waiting for 4 players
                    print("4 players ready, starting game")
                    startGame()
                    self.started = True
            else:
                if self.started:
                    self.started = False
            
            if not self.started and (game_state['active'] or game_state['finished']):
                self.started = True

            if self.started:
                # parse messages
                for message in game_state['messages']:
                    u = message['username']
                    m = message['message']

                    # if server message
                    if u == "Server":
                        if len(m) >= 15 and m[-14:] == ' wins the game':  # game is over
                            # add new remaining cards
                            winning_player = m[:-14]
                            player_cards = {}
                            for player in game_state['players']:
                                player_cards[player] = game_state['num_cards'][player]
                            player_cards[winning_player] = 0
                            print(f"adding game { player_cards }")

                            # write sessions
                            self.current_session.append(player_cards)
                            self.sessions[self.session_name] = self.current_session
                            self.writeSessions()

                            # start new game
                            self.startGame()


    def startGame(self):
        self.sio.emit('chat-message', (self.game_name, USERNAME, "!start"))


    def loadSessions(self):
        try:
            with open('sessions.json', 'r') as file:
                sessions = json.loads(file.read())
        except IOError:
            firstTimeSetup()
            sessions = {}

        return sessions


    def writeSessions(self):
        with open('sessions.json', 'w') as file:
            file.write(json.dumps(self.sessions))


    def firstTimeSetup(self):
        print('performing first time setup')
        with open('sessions.json', 'w') as file:
            file.write(json.dumps({}))


    def kill(self, signal_received, frame):
        # disconnect from the server
        self.sio.disconnect()

        # print that program was hard killed
        print('Program killed')

        # kill the program
        exit()


if __name__ == '__main__':
    # instantiate the client class
    client = Client()

    # run the main method
    client.main()
