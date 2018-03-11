import pygame
import zmq

from client.GameStateUpdater import GameStateUpdater

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


class GUIDisplay(object):
    """
        Viewer class
    """
    def __init__(self, display_delay=500):
        self.zmq_root_context = zmq.Context()
        self.display_delay = display_delay
        self.gsu = GameStateUpdater(self.zmq_root_context, target_url="127.0.0.1:9191")
        self.quit_flag = False

        self.gsu.start()
        pygame.time.wait(100)

        pygame.init()

        self.screen = pygame.display.set_mode(WINDOW_SIZE)

        # Set title of screen
        pygame.display.set_caption("Dragon's Arena")

        self.im_human = pygame.image.load("img/human.bmp")
        self.im_dragon = pygame.image.load("img/dragon.bmp")

    def mainloop(self):
        while self.gsu.is_game_running() and not self.quit_flag:
            for event in pygame.event.get():  # User did something
                if event.type == pygame.QUIT:  # If user clicked close
                    self.quit_flag = True

            boardstring = self.gsu.get_gamestate_in_string()
            self.draw_screen(boardstring)
            pygame.time.wait(self.display_delay)

        self.gsu.join()
        self.zmq_root_context.term()
        pygame.quit()

    def draw_screen(self, boardstring):
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

                if boardstring[row*25+column] == 'h':
                    self.screen.blit(self.im_human, ((MARGIN + HEIGHT) * row + MARGIN,
                                      (MARGIN + WIDTH) * column + MARGIN))
                elif boardstring[row*25+column] == 'd':
                    self.screen.blit(self.im_dragon, ((MARGIN + HEIGHT) * row + MARGIN,
                                      (MARGIN + WIDTH) * column + MARGIN))
     
        # Update the screen with what we've drawn
        pygame.display.flip()
