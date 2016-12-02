import pygame
from pygame.locals import *

class GraphicsComponent(pygame.sprite.Sprite):
    """Base class for all Graphical game components"""


class Player(GraphicsComponent):
    """"The active player"""
    def __init__(self, sprite, WINDOW_HEIGHT):
        pygame.sprite.Sprite.__init__(self)
        self.pos = [0, WINDOW_HEIGHT - 30]
        self.sprite = pygame.transform.flip(pygame.transform.scale(sprite, (47, 30)), True, False)
        self.direction = 1  # negative: left, positive: right

    def move(self, movement, direction=1):
        self.pos[0] += movement[0]
        self.pos[1] += movement[1]
        if direction != self.direction:
            self.sprite = pygame.transform.flip(self.sprite)

    def attack(self):
        pass # throw vial or other appropriate action

