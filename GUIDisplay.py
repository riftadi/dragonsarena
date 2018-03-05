import pygame
import json
from GameState import GameState
from threading import Thread

# Introducing some (bad) global variables for pygame screen..
# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
 
# This sets the WIDTH and HEIGHT of each grid location
WIDTH = 20
HEIGHT = 20
 
# This sets the margin between each cell
MARGIN = 2

# Set the HEIGHT and WIDTH of the screen
WINDOW_SIZE = [552, 552]


class GUIDisplay(Thread):
    """
        Viewer class
    """
    def __init__(self, display_delay):
        Thread.__init__(self)
        self.gamestate = GameState()
        self.display_delay = display_delay
        self.quit_flag = False

        pygame.init()

        self.screen = pygame.display.set_mode(WINDOW_SIZE)

        # Set title of screen
        pygame.display.set_caption("Dragon's Arena")

        self.im_human = pygame.image.load("human.bmp")
        self.im_dragon = pygame.image.load("dragon.bmp")

    def set_gamestate(self, state):
        self.gamestate = state

    def stop(self):
        self.quit_flag = True

    def run(self):
        while not self.quit_flag:
            for event in pygame.event.get():  # User did something
                if event.type == pygame.QUIT:  # If user clicked close
                    self.quit_flag = True
            self.screen.fill(BLACK)
         
            # Draw the grid
            for row in xrange(25):
                for column in xrange(25):
                    pygame.draw.rect(self.screen,
                                     WHITE,
                                     [(MARGIN + HEIGHT) * row + MARGIN,
                                      (MARGIN + WIDTH) * column + MARGIN,
                                      HEIGHT,
                                      WIDTH])
                    obj = self.gamestate.get_object(row, column)
                    if obj != None:
                        if obj.get_type() == 'h':
                            self.screen.blit(self.im_human, ((MARGIN + HEIGHT) * row + MARGIN,
                                              (MARGIN + WIDTH) * column + MARGIN))
                        elif obj.get_type() == 'd':
                            self.screen.blit(self.im_dragon, ((MARGIN + HEIGHT) * row + MARGIN,
                                              (MARGIN + WIDTH) * column + MARGIN))
         
            # Go ahead and update the screen with what we've drawn.
            pygame.display.flip()
            pygame.time.wait(self.display_delay)

        pygame.quit()
