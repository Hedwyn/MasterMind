import random
from enum import Enum

## Game Parameters
CODE_LENGTH = 5
MAX_TRIES = 12
COLORS = ['grey', 'red', 'blue', 'yellow', 'green', 'brown', 'white', 'black', 'orange']

class Token(Enum):
    """Token colors enumeration. Note that the first color is reserved and stands for undefined"""
    RED     =    COLORS[1]
    BLUE    =    COLORS[2]
    YELLOW  =    COLORS[3]
    GREEN   =    COLORS[4]
    BROWN   =    COLORS[5]
    WHITE   =    COLORS[6]
    BLACK   =    COLORS[7]
    ORANGE  =    COLORS[8]

class Score:
    def __init__(self, white_ctr, black_ctr):
        self.white = white_ctr
        self.black = black_ctr
    
    def __str__(self):
        return("W: " + str(self.white) + " B: " + str(self.black))

class Game:
    def __init__(self, gui = None):
        """Starts a Master Mind game"""
        self.played_combinations = []
        if gui:
            self.display = gui.log
        else:
            self.display = print
        self.previous_points = []
        self.code = self.generate_secret_code()
        # self.display("Code == " + str(self.code))
        self.tries = 0
        self.iswon = False
        self.islost = False
        # self.play()

    def generate_secret_code(self):
        """Generates a random secret combination"""
        code = []
        colors = [color.value for color in Token]
        for i in range(CODE_LENGTH):
            code.append(random.choice(colors))
        return(code)
    
    def count_points(self, code):
        """Count the number of black and white tokens for the submitted combination.
        Rules:
        - One black token for each token that has the right color at the right place
        - One white token for each token that has the right color at the wrong place."""
        black_ctr = 0
        white_ctr = 0
        played_colors = []
        for idx, color in enumerate(code):
            if color == self.code[idx]:
                black_ctr += 1
            else:
                if not(color in played_colors):
                    if color in self.code:
                        played_colors.append(color)
                        white_ctr += 1
        return(Score(white_ctr, black_ctr))
                    
    def submit(self, code):
        """Submits the player's combination for check"""
        self.played_combinations.append(code)
        score = self.count_points(code)
        # self.display(score)
        self.tries += 1
        if score.black == 5:
            self.won()
        elif self.tries < MAX_TRIES:
            self.previous_points.append(score)
            won = False
        else:
            self.lost()
        return(score)

    def play(self):
        """Starts the game loop.
        The game finished when the player guesses the right combination or when all the tries have been consumed"""
        won = False
        while self.tries < MAX_TRIES:
            code = input()
            while len(code) != CODE_LENGTH:
                self.display("Invalid code, you must submit a code of length " + str(CODE_LENGTH))
                code = input()
            self.tries += 1
            if self.submit(code):
                self.won()
                return
            self.display("You have " + str(MAX_TRIES - self.tries) + " tries left")
        self.lost()

    def won(self):
        """The player has managed to find the secret code before using all his/her tries"""
        self.display("Congratulations, you won in " + str(self.tries) + " tries")
        self.iswon = True

    def lost(self):
        """All the tries have been consumed, the game is lost"""
        self.display("Sorry, you lost !")
        self.islost = True

if __name__ == "__main__":
    Game()


    
            
