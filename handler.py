import socket
from _thread import start_new_thread
import pickle
from tkinter import Tk, Canvas

# GLOBAL VARIABLES
HOST = 'localhost'
PORT = 5555

class Box:
    '''
        Class for boxes in the game.
    '''
    def __init__(self, canvas):
        
        self.canvas = canvas
        self.sign = " "     # can be X or O

    def draw(self, x1, y1, x2, y2):
        self.id = self.canvas.create_rectangle(x1, y1, x2, y2)

class TicTacToe:
    '''
        This is essentially the GUI for the game and handles
        all the GUI related stuff.
    '''
    def __init__(self):
        '''
            Creating the window and the canvas
        '''
        self.root = Tk()
        self.canvas = Canvas(self.root,  height = 500, width = 400)
        self.canvas.bind("<Button-1>", self.turn)
        self.canvas.pack()

    def start_game(self, game_type):
        '''
            Starts the game by instatiating a Game object.

        '''
        self.game = Game(game_type, self)
        self.game.turns = 0 # number of turns

        self.game.start_game()
        self.create_board()

        # mainloop
        self.root.mainloop()    

    def create_board(self):
        '''
            Creates the boxes for the game
        '''
        self.boxes = []
        # x and y co-ordinates for initial box
        x = y = 50
        for row in range(3):
            for col in range(3):
                new_box = Box(self.canvas)
                new_box.draw(x, y, x + 100, y + 100)
                self.boxes.append(new_box)
                y += 100
                if y == 350: y = 50

            x += 100

        # TEXT
        self.canvas.create_text(79, 370, text ="Player O", fill = "Black", font=("Bold", 12) )
        self.canvas.create_text(321, 370, text="Player X", fill="Black", font=("Bold", 12))
        self.canvas.create_line(49, 380, 110, 380, fill = "Blue")
        self.canvas.create_line(291, 380, 350, 380, fill="Red")

        if self.game.game == 'host':
            self.turn_text = self.canvas.create_text(250, 400, text ="Your Turn",
                                                fill = "Black", font=("Bold", 20))
        else:
            self.turn_text = self.canvas.create_text(250, 400, text ="Opponent's Turn",
                                                     fill = "Black", font=("Bold", 20))
    def update_turn_text(self):
        self.canvas.delete(self.turn_text)
        if self.game.turn :
            self.turn_text = self.canvas.create_text(250, 400, text ="Your Turn",
                                                fill = "Black", font=("Bold", 20))
        else:
            self.turn_text = self.canvas.create_text(250, 400, text ="Opponent's Turn",
                                                     fill = "Black", font=("Bold", 20))

    def turn(self, event):
        '''
            Handler when a turn is played
        '''
        if self.game.turn:
            for box in self.boxes:
                coords = self.canvas.coords(box.id)
                # Checks through co-ordinates of mouse which box was clicked
                if event.x < coords[2] and event.x > coords[0] and box.sign == ' ':
                    if event.y < coords[3] and event.y > coords[1]:

                        if self.game.game == "guest":
                            self.canvas.create_text((coords[0]+coords[2])/2, (coords[1]+coords[3])/2,
                                                        text = 'X',fill = "RED", font = ('Bold', 40))
                            box.sign = 'X'
                            self.game.turns = self.game.turns + 1

                        elif self.game.game == 'host':
                            self.canvas.create_text((coords[0] + coords[2]) / 2, (coords[1] + coords[3]) / 2,
                                                                    text='O', fill="BLUE", font=('Bold', 40))
                            box.sign = 'O'
                            self.game.turns = self.game.turns + 1

                        else:
                            pass    

                        if self.win():
                            self.canvas.delete(self.turn_text)
                            self.canvas.create_text(200, 450, text = str(box.sign) + " WON!", fill = "BLACK", font = ("BOLD", 30))
                            self.canvas.unbind("<Button-1>")
                        
                        elif self.game.turns == 9:
                            self.canvas.delete(self.turn_text)
                            self.canvas.unbind("<Button-1>")
                            self.canvas.create_text(200, 450, fill = "BLACK", text = "IT'S A DRAW!", font = ("BOLD", 30))
                        
                        else:
                            pass
                        self.game.send_data(coords)
                        self.update_turn_text()    

    def win(self):
        '''
            Checks if someone won
        '''
        row = 0
        # Checks for vertical win in every column
        for _ in range(3):
            if self.boxes[row].sign == self.boxes[row+1].sign == self.boxes[row+2].sign != ' ':
                return True    
            row += 3

        row = 0
        # Checks for horizontal win in every column
        for _ in range(3):
            if self.boxes[row].sign == self.boxes[row+3].sign == self.boxes[row+6].sign != ' ':
                return True
            row += 1

        # Checks for Diagonal Win
        if self.boxes[0].sign == self.boxes[4].sign == self.boxes[8].sign != ' ':
            return True

        elif self.boxes[2].sign == self.boxes[4].sign == self.boxes[6].sign != ' ':
            return True    

        return False

    def update(self, data):
        '''
            Updates changes made by other player's turn
        '''
        coords = pickle.loads(data)

        for box in self.boxes:
            if self.canvas.coords(box.id) == coords:
                box.sign = 'X' if self.game.game == 'host' else 'O'

                self.game.turns = self.game.turns + 1
                self.game.turn = True
                self.update_turn_text()

                if self.game.game == 'host':
                    self.canvas.create_text((coords[0]+coords[2])/2, (coords[1]+coords[3])/2,
                                                text = 'X',fill = "RED", font = ('Bold', 40))
                else:
                    self.canvas.create_text((coords[0]+coords[2])/2, (coords[1]+coords[3])/2,
                                               text = 'O',fill = "BLUE", font = ('Bold', 40))

                if self.win():
                    self.canvas.create_text(200, 450, text = str(box.sign) + " WON!",
                                                 fill = "BLACK", font = ("BOLD", 30))
                    self.canvas.unbind("<Button-1>")                             
                        
                elif self.game.turns == 9:
                    self.canvas.create_text(200, 450, fill = "BLACK",
                          text = "IT'S A DRAW!", font = ("BOLD", 30))
                    self.canvas.unbind("<Button-1>")

                else:
                    pass                                                                         


class Game:
    '''
        This is the handler class for the game.
        It handles the socket connections and data transfer among some other things.
    '''
    def __init__(self, game_type, gui):
        self.gui = gui
        self.game = game_type
        self.turn = True if game_type == 'host' else False
        self.turns = 0
   
    def start_game(self):
        if self.game == 'guest':
            self.start_game_as_guest()
        else:
            self.start_game_as_host()

    def start_game_as_host(self):
        '''
            Starts game by creating a server.

        '''
        self.server = socket.socket()
        self.server.bind((HOST, PORT))

        print("Starting Game Server..")
        self.server.listen(1)
        print('Waiting for someone to join')

        self.game_conn = self.server.accept()[0]
        print('playing with {}'.format(self.game_conn))

        # Keeps the connection alive
        self.game_conn.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

        start_new_thread(self.get_data, ())
    

    def start_game_as_guest(self):
        '''
            Starts the game by connecting to a server
        '''
        self.game_conn = socket.socket()

        print("Finding a game..")
        self.game_conn.connect((HOST, PORT))

        # Keeps the connection alive
        self.game_conn.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        print("Connected!")

        start_new_thread(self.get_data, ())

    def get_data(self):
        '''
            Gets data from other player after turn is completed
        '''
        while True:
            data = self.game_conn.recv(4096)        
            if data is not None:
                self.gui.update(data)
                self.turn = True

    def send_data(self, payload):
        '''
            Sends data to the other player after turn completed
        '''
        data = pickle.dumps(payload)
        self.game_conn.send(data)
        self.turn = False            


if __name__ =='__main__':
    # Start game
    type_ = input("play as: 'host' or 'guest' ")

    new_game = TicTacToe()
    new_game.start_game(type_)