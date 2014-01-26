# controller.py
# Tech Kuo(thk42) and Charles Lai(cjl223)
# 12-2-12
# Extensions: Try Again, Scoreboard
"""Controller module for Breakout

This module contains a class and global constants for the game Breakout.
Unlike the other files in this assignment, you are 100% free to change
anything in this file. You can change any of the constants in this file
(so long as they are still named constants), and add or remove classes."""
import colormodel
import random
from graphics import *

# CONSTANTS

# Width of the game display (all coordinates are in pixels)
GAME_WIDTH  = 480
# Height of the game display
GAME_HEIGHT = 620

# Width of the paddle
PADDLE_WIDTH = 58
# Height of the paddle
PADDLE_HEIGHT = 11
# Distance of the (bottom of the) paddle up from the bottom
PADDLE_OFFSET = 30

# Horizontal separation between bricks
BRICK_SEP_H = 5
# Vertical separation between bricks
BRICK_SEP_V = 4
# Height of a brick
BRICK_HEIGHT = 8
# Offset of the top brick row from the top
BRICK_Y_OFFSET = 70

# Number of bricks per row
BRICKS_IN_ROW = 10
# Number of rows of bricks, in range 1..10.
BRICK_ROWS = 10
# Width of a brick
BRICK_WIDTH = GAME_WIDTH / BRICKS_IN_ROW - BRICK_SEP_H

# Diameter of the ball in pixels
BALL_DIAMETER = 18

# Number of attempts in a game
NUMBER_TURNS = 3

# Basic game states
# Game has not started yet
STATE_INACTIVE = 0
# Game is active, but waiting for next ball
STATE_PAUSED   = 1
# Ball is in play and being animated
STATE_ACTIVE   = 2
# Game is over, deactivate all actions
STATE_COMPLETE = 3


# CLASSES
class Breakout(GameController):
    """Instance is the primary controller for Breakout.

    This class extends GameController and implements the various methods
    necessary for running the game.

        Method initialize starts up the game.

        Method update animates the ball and provides the physics.

        The on_touch methods handle mouse (or finger) input.

    The class also has fields that provide state to this controller.
    The fields can all be hidden; you do not need properties. However,
    you should clearly state the field invariants, as the various
    methods will rely on them to determine game state."""
    # FIELDS.

    # Current play state of the game; needed by the on_touch methods
    # Invariant: One of STATE_INACTIVE, STATE_PAUSED, STATE_ACTIVE
    _state = STATE_INACTIVE

    # List of currently active "bricks" in the game.
    #Invariant: A list of  objects that are instances of GRectangle (or a
    #subclass) If list is  empty, then state is STATE_INACTIVE (game over)
    _bricks = []

    # The player paddle
    # Invariant: An object that is an instance of GRectangle (or a subclass)
    # Also can be None; if None, then state is STATE_INACTIVE (game over)
    _paddle = None

    # The ball to bounce about the game board
    # Invariant: An object that is an instance of GEllipse (or a subclass)
    # Also can be None; if None, then state is STATE_INACTIVE (game over) or
    # STATE_PAUSED (waiting for next ball)
    _ball = None

    # ADD MORE FIELDS (AND THEIR INVARIANTS) AS NECESSARY
    
    # The welcome screen
    # Invariant: An object that is an instance of GLabel.
    # Also can be None; if None, then game has not started yet.
    _welcomescreen = None

    # The anchor point of the paddle
    # Invariant: 2-element tuple of float or None
    _anchor = None
    
    # The distance between the x-coordinate of the anchor point and the left edge of the paddle
    # Invariant: Value is a float
    _xdistance = 0.0
    
    # The x-coordinate of the left edge of the paddle
    # Invariant: Value is a float
    _leftvalue = GAME_WIDTH/2 - PADDLE_WIDTH/2
    
    #The x-coordinate of the ball
    # Invariant: Value is a float
    _xposball = 0.0
    
    #The y-coordinate of the ball
    # Invariant: Value is a float
    _yposball = 0.0
    
    #The x-velocity of the ball
    # Invariant: Value is a float
    _vxball = 0.0
    
    #The y-velocity of the ball
    # Invariant: Value is a float
    _vyball = 0.0
    
    #The index of _bricks that represents the brick the ball has collided with
    # Invariant: Value is an int
    _collidedbrick = 0
    
    #Player lives
    # Invariant: Value is an int
    _lives = 3
    
    # The paused screen
    # Invariant: An object that is an instance of GLabel.
    # Also can be None; only None before first time ball hits bottom boundary and when state is not STATE_PAUSED afterwards
    _pausedscreen = None
    
    # The game over screen
    # Invariant: An object that is an instance of GLabel.
    # Also can be None; only None when _lives does not equal 0 and state != STATE_INACTIVE
    _gameoverscreen = None
    
    # The win screen
    # Invariant: An object that is an instance of GLabel.
    # Also can be None; only None when _bricks is not empty.
    _winscreen = None

    # Count of bricks remaining in play
    # Invariant: An object that is an instance of GLabel.
    # Also can be None; only None when state is STATE_INACTIVE
    _brickscore = None
    
    # Display of lives of player
    # Invariant: An object that is an instance of GLabel.
    # Also can be None; only None when state is STATE_INACTIVE
    _playerlives = None
    # METHODS

    def initialize(self):
        """Initialize the game state.

        Initialize any state fields as necessary to statisfy invariants.
        When done, set the state to STATE_INACTIVE, and display a message
        saying that the user should press to play a game."""
        
        self._welcomescreen = GLabel(text = 'Press to Play',pos = (0,310),halign = 'left', valign = 'middle', font_size = 63)
        self.view.add(self._welcomescreen)
        self._state = STATE_INACTIVE

    def update(self, dt):
        """Animate a single frame in the game.

        This is the method that does most of the work.  It moves the ball, and
        looks for any collisions.  If there is a collision, it changes the
        velocity of the ball and removes any bricks if necessary.

        This method may need to change the state of the game.  If the ball
        goes off the screen, change the state to either STATE_PAUSED (if the
        player still has some tries left) or STATE_COMPLETE (the player has
        lost the game).  If the last brick is removed, it needs to change
        to STATE_COMPLETE (game over; the player has won).

        Precondition: dt is the time since last update (a float).  This
        parameter can be safely ignored."""
        
        if self._lives == 0:
            self._state = STATE_INACTIVE
            self._gameoverscreen = GLabel(text = 'Game Over \nTry again?',pos = (0,310),halign = 'left', valign = 'middle', font_size = 70)
            self.view.add(self._gameoverscreen)
            self._resetGame()
        if self._state == STATE_PAUSED and self._pausedscreen is None and self._lives < 3 and self._lives != 0:
            self._pausedscreen = GLabel(text = 'Ball will be served in 3 seconds',pos = (0,310),halign = 'left', valign = 'middle', font_size = 25)
            self.view.add(self._pausedscreen)
            self.delay(self._addBall, 3)
        if self._state == STATE_ACTIVE:
            self.view.remove(self._ball)
            self._vxball = self._ball._vx
            self._vyball = self._ball._vy
            self._xposball = self._ball.pos[0] + self._vxball
            self._yposball = self._ball.pos[1] + self._vyball
            self._checkCollisions()
            if self._state != STATE_PAUSED:
                self._ball = Ball((self._xposball, self._yposball), self._vxball, self._vyball)
                self._view.add(self._ball)
            if len(self._bricks)== 0:
                self._winGame()

    def on_touch_down(self,view,touch):
        """Respond to the mouse (or finger) being pressed (but not released)

        If state is STATE_ACTIVE or STATE_PAUSED, then this method should
        check if the user clicked inside the paddle and begin movement of the
        paddle.  Otherwise, if it is one of the other states, it moves to the
        next state as appropriate.

        Precondition: view is just the view attribute (unused because we have
        access to the view attribute).  touch is a MotionEvent (see
        documentation) with the touch information."""
        
        if self._state  == STATE_INACTIVE:
            if not self._welcomescreen is None:
                self.view.remove(self._welcomescreen)
            if not self._gameoverscreen is None:
                self.view.remove(self._gameoverscreen)
            self._state = STATE_PAUSED
            self._setBricks()
            self._displayScore()
            self._setPaddle()
            self.delay(self._addBall, 3)
        if self._paddle.collide_point(touch.x, touch.y) == True:
            self._anchor = (touch.x, touch.y)
            self._xdistance = (touch.x - self._leftvalue)

    def on_touch_move(self,view,touch):
        """Respond to the mouse (or finger) being moved.

        If state is STATE_ACTIVE or STATE_PAUSED, then this method should move
        the paddle. The distance moved should be the distance between the
        previous touch event and the current touch event. For all other
        states, this method is ignored.

        Precondition: view is just the view attribute (unused because we have
        access to the view attribute).  touch is a MotionEvent (see
        documentation) with the touch information."""
        
        if self._state == STATE_ACTIVE and not self._anchor is None or self._state == STATE_PAUSED and not self._anchor is None:
            self._movePaddle()
            self._anchor = (touch.x, touch.y)

    def on_touch_up(self,view,touch):
        """Respond to the mouse (or finger) being released.

        If state is STATE_ACTIVE, then this method should stop moving the
        paddle. For all other states, it is ignored.

        Precondition: view is just the view attribute (unused because we have
        access to the view attribute).  touch is a MotionEvent (see
        documentation) with the touch information."""
        self._anchor = None

    # ADD MORE HELPER METHODS (PROPERLY SPECIFIED) AS NECESSARY
    def _setBricks(self):
        """Sets up bricks
        """
        for x in range(BRICK_ROWS):
            ypos = GAME_HEIGHT-BRICK_Y_OFFSET-BRICK_HEIGHT*x-BRICK_SEP_V*x
            xlist = `x`
            for y in range(BRICKS_IN_ROW):
                    if int(xlist[len(xlist)-1]) == 0 or int(xlist[len(xlist)-1]) == 1 :
                        brick = GRectangle(pos = (BRICK_SEP_H/2+BRICK_WIDTH*y+BRICK_SEP_H*y, ypos), size = (BRICK_WIDTH,BRICK_HEIGHT), linecolor = colormodel.RED, fillcolor = colormodel.RED)
                        self.view.add(brick)
                        self._bricks.append(brick)
                    if int(xlist[len(xlist)-1]) == 2 or int(xlist[len(xlist)-1]) == 3:
                        brick = GRectangle(pos = (BRICK_SEP_H/2+BRICK_WIDTH*y+BRICK_SEP_H*y, ypos), size = (BRICK_WIDTH,BRICK_HEIGHT), linecolor = colormodel.ORANGE, fillcolor = colormodel.ORANGE)
                        self.view.add(brick)
                        self._bricks.append(brick)
                    if int(xlist[len(xlist)-1]) == 4 or int(xlist[len(xlist)-1]) == 5:
                        brick = GRectangle(pos = (BRICK_SEP_H/2+BRICK_WIDTH*y+BRICK_SEP_H*y, ypos), size = (BRICK_WIDTH,BRICK_HEIGHT), linecolor = colormodel.YELLOW, fillcolor = colormodel.YELLOW)
                        self.view.add(brick)
                        self._bricks.append(brick)
                    if int(xlist[len(xlist)-1]) == 6 or int(xlist[len(xlist)-1]) == 7:
                        brick = GRectangle(pos = (BRICK_SEP_H/2+BRICK_WIDTH*y+BRICK_SEP_H*y, ypos), size = (BRICK_WIDTH,BRICK_HEIGHT), linecolor = colormodel.GREEN, fillcolor = colormodel.GREEN)
                        self.view.add(brick)
                        self._bricks.append(brick)
                    if int(xlist[len(xlist)-1]) == 8 or int(xlist[len(xlist)-1]) == 9:
                        brick = GRectangle(pos = (BRICK_SEP_H/2+BRICK_WIDTH*y+BRICK_SEP_H*y, ypos), size = (BRICK_WIDTH,BRICK_HEIGHT), linecolor = colormodel.CYAN, fillcolor = colormodel.CYAN)
                        self.view.add(brick)
                        self._bricks.append(brick)

    def _setPaddle(self):
        """Creates the paddle(a GRectangle object), adds it to the view, and assigns it to the _paddle field"""
        
        paddle = GRectangle(pos = (GAME_WIDTH/2-PADDLE_WIDTH/2, PADDLE_OFFSET), size = (PADDLE_WIDTH, PADDLE_HEIGHT), linecolor = colormodel.BLACK, fillcolor = colormodel.BLACK)
        self.view.add(paddle)
        self._paddle = paddle

    def _movePaddle(self):
        """"Moves the paddle by removing the current paddle from the view and creating a new paddle.
        This new paddle is then assigned to _paddle. Location of the new paddle is restricted to between 0 and GAME_WIDTH-PADDLE WIDTH"""
        
        self.view.remove(self._paddle)
        newpos = (min((max(self._anchor[0] - self._xdistance, 0)),GAME_WIDTH-PADDLE_WIDTH), PADDLE_OFFSET)
        newpaddle = GRectangle(pos = newpos, size = (PADDLE_WIDTH, PADDLE_HEIGHT), linecolor = colormodel.BLACK, fillcolor = colormodel.BLACK)
        self._leftvalue = self._anchor[0] - self._xdistance
        self._paddle = newpaddle
        self.view.add(newpaddle)

    def _addBall(self):
        """Creates a Ball object and adds it to the view.
    
        Also checks if there is GLabel object under_pausedscreen and removes it if there is
        and changes the state to STATE_ACTIVE after ball has been created and added to view """
        
        if not self._pausedscreen is None:
            self.view.remove(self._pausedscreen)
            self._pausedscreen = None
        self._ball = Ball()
        self.view.add(self._ball)
        self._state = STATE_ACTIVE

    def _checkCollisions(self):
        """Checks for collisions with the boundaries of the game and collisions with the paddle and bricks
        if the ball hits the bottom boundary, player loses a life, ball is removed, and state is changed to STATE_PAUSED.
        Otherwise if it hits a boundary of the paddle, it is reflected. If it hits a brick, the collided brick is removed"""
        
        if self._yposball <= 0: #check bottom boundary
            self._lives -= 1
            self._playerlives.text = 'Player Lives: ' + `self._lives`
            self.view.remove(self._ball)
            self._ball = None
            self._state = STATE_PAUSED
            return
        if self._yposball + BALL_DIAMETER >= GAME_HEIGHT: #check top boundary
            self._vyball = -self._vyball
            self._yposball = self._ball.pos[1] + self._vyball
        if self._xposball + BALL_DIAMETER >= GAME_WIDTH: #check right boundary
                self._vxball = -self._vxball
                self._xposball = self._ball.pos[0] + self._vxball
        if self._xposball <= 0: #check left boundary
                self._vxball = -self._vxball
                self._xposball = self._ball.pos[0] + self._vxball
        if self._getCollidingObject() == self._paddle: #check paddle
                self._vyball = -self._vyball
                self._yposball = self._ball.pos[1] + self._vyball
        if self._getCollidingObject() == self._collidedbrick: #check bricks
                self._view.remove(self._collidedbrick)
                self._bricks.remove(self._collidedbrick)
                self._vyball = -self._vyball
                self._yposball = self._ball.pos[1] + self._vyball
                self._brickscore.text = 'Bricks Remaining: '+`len(self._bricks)`

    def _getCollidingObject(self):
        """Returns: GObject that has collided with the ball
        
        This method checks the four corners of the ball, one at a 
        time. If one of these points collides with either the paddle 
        or a brick, it stops the checking immediately and returns the 
        object involved in the collision. It returns None if no 
        collision occurred."""
        
        if self._paddle.collide_point(self._xposball, self._yposball) == True or self._paddle.collide_point(self._xposball+BALL_DIAMETER, self._yposball) == True:
            if self._vyball >= 0:
                return None
            if self._vyball <= 0:
                return self._paddle
        for x in range(len(self._bricks)):
            if self._checkCorners(x):
                self._collidedbrick = self._bricks[x]
                return self._collidedbrick

    def _checkCorners (self, x):
        """ Returns: True if the corners of the ball have collided with a brick, False otherwise"""
        
        if self._bricks[x].collide_point(self._xposball, self._yposball) == True:
            return True
        elif self._bricks[x].collide_point(self._xposball + BALL_DIAMETER, self._yposball) == True:
            return True
        elif self._bricks[x].collide_point(self._xposball, self._yposball + BALL_DIAMETER) == True:
            return True
        elif self._bricks[x].collide_point(self._xposball + BALL_DIAMETER, self._yposball + BALL_DIAMETER) == True:
            return True
        else:
            return False

    def _resetGame (self):
        """Resets the game so the player can play another round.
        
        Resets player lives to 3, removes paddle and resets related fields, removes all bricks and resets its field,
        and removes the scoreboard(display of number of bricks in play and player lives left)"""
        
        self._lives = 3 #reset lives
        self.view.remove(self._paddle) #remove paddle
        self._paddle = None
        self._xdistance = 0.0
        self._leftvalue = GAME_WIDTH/2 - PADDLE_WIDTH/2
        for x in range(len(self._bricks)): #remove bricks
            self.view.remove(self._bricks[x])
        self._bricks = []
        self.view.remove(self._brickscore) #Remove brickscore
        self._brickscore = None
        self.view.remove(self._playerlives) #Remove playerlives
        self._playerlives = None

    def _winGame (self):
        """ End the game when the player breaks all the bricks
        Creates a GLabel object for the win screen, sets state to STATE_COMPLETE, and removes ball, paddle, and scoreboard"""
        
        self._state = STATE_COMPLETE
        self._winscreen = GLabel(text = 'You Won!',pos = (0,310),halign = 'left', valign = 'middle', font_size = 82)
        self.view.add(self._winscreen)
        self.view.remove(self._ball) #Remove ball
        self._ball = None
        self.view.remove(self._paddle)#Remove paddle
        self._paddle = None
        self.view.remove(self._brickscore) #Remove brickscore
        self._brickscore = None
        self.view.remove(self._playerlives) #Remove playerlives
        self._playerlives = None

    def _displayScore(self):
        """Displays scoreboard(numbers of bricks still in play and player lives left).
        Creates a GLabel object for number of bricks in play and another for player lives and adds both to the view"""
        
        self._brickscore = GLabel(text ='Bricks Remaining: '+`len(self._bricks)`, pos = (10,550),halign = 'left', valign = 'middle', font_size = 15)
        self.view.add(self._brickscore)
        self._playerlives = GLabel(text = 'Player Lives: ' + `self._lives`, pos = (350,550),halign = 'left', valign = 'middle', font_size = 15)
        self.view.add(self._playerlives)


class Ball(GEllipse):
    """Instance is a game ball.

    We extends GEllipse because a ball does not just have a position; it
    also has a velocity.  You should add a constructor to initialize the
    ball, as well as one to move it.

    Note: The ball does not have to be a GEllipse. It could be an instance
    of GImage (why?). This change is allowed, but you must modify the class
    header up above."""
    
    # FIELDS.  

    # Velocity in x direction.
    # Invariant: Value is a float
    _vx = 0.0
    # Velocity in y direction.
    # Invariant: Value is a float
    _vy = 0.0

    # ADD MORE METHODS (PROPERLY SPECIFIED) AS NECESSARY
    def __init__(self, position = (GAME_WIDTH/2-BALL_DIAMETER/2,310), vx = 0.0, vy = 0.0):
        """Constructor: a black GEllipse object with position pos, diameter 18, horizontal velocity vx, and vertical velocity vy
        
        Precondition: position is a tuple, vx and vy are floats"""
        
        super(Ball, self).__init__(pos = position, size = (18,18), fillcolor = colormodel.BLACK, linecolor = colormodel.BLACK)
        if vx == 0.0:
            self._vx = random.uniform(1.0, 5.0)
            self._vx = self._vx * random.choice([-1,1])
        else:
            self._vx = vx
        if vy == 0.0:
            self._vy = -5.0
        else:
            self._vy = vy
        