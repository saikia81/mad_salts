import pygame
from pygame.locals import *
import Graphics
# graphical game components and builders

# graphical game base class
class GraphicsComponent(pygame.sprite.Sprite):
    """Base class for all Graphical Game Components"""
    def __init__(self, pos=(0, 0)):
        pygame.sprite.Sprite.__init__(self)
        self.graphics_handler = Graphics.graphics_handler
        self.sprite = self.graphics_handler.resources[self.NAME.lower()]
        self.dimensions = self.sprite.get_size()
        self.rect = pygame.Rect(pos, self.dimensions)

    def __del__(self):
        pass

    #blit the object
    def blit(self, direct_display=False):
        self.graphics_handler.blit(self.sprite, self.rect)
        if direct_display:
            self.graphics_handler.update()

    # abstract
    def update(self):
        raise NotImplementedError("Please Implement this method")

    def display(self):
        self.graphics_handler.blit(self.sprite, self.rect)


class Background(GraphicsComponent):
    """Background"""
    NAME = 'Background' # this shouldn't be used, the name should have it's number as suffix

    def __init__(self, level_number):
        self.NAME += str(level_number)  # A correct name is needed for initialization
        super(Background, self).__init__()


# text meters on screen (for debugging)
# todo: enable sprite base meters
class Meter(GraphicsComponent):
    """meters which display game state"""
    NAME = 'Meter'

    def __init__(self, update_function, pos):
        super(Player, self).__init__(pos, self.NAME)
        self.update_function = update_function
        self.value = 0

    def update(self):
        self.value = self.update_function()


# the main player class
class Player(GraphicsComponent):
    """"The active player"""
    NAME = 'Player'

    def __init__(self, pos):
        super(Player, self).__init__(pos)
        self.sprite = pygame.transform.scale(self.sprite, (47, 30))  #.convert_alpha()
        self.direction = 1  # negative: left, positive: right

    # addes movement to the player, this changes the state of movement
    # when no key press is registered anymore the event system should notify the player it's standing still
    def move(self, movement, direction=1):
        self.rect.move_ip(movement)

        if direction != self.direction:
            self.sprite = pygame.transform.flip(self.sprite)

    def attack(self):
        pass # throw vial or other appropriate action

    def update(self):
        pass


# A graphical game component which mainly interacts with the player (and monsters)
class Monster(GraphicsComponent):
    """Monster baseclass"""
    NAME = 'Monster'
    def __init__(self, pos):
        super(Monster, self).__init__(pos)

class TestMonster(Monster):
    NAME = 'Testmonster'

    def __init__(self, pos):
        super(TestMonster, self).__init__(pos)


# game components list
# includes: entities, world blocks, and background
GAME_COMPONENT_TYPES = [Player, Meter, TestMonster]
GAME_COMPONENTS = {component.NAME : component for component in GAME_COMPONENT_TYPES}

#
def create_game_component(self, component_type, pos):
    return GAME_COMPONENTS[component_type](pos)

def make_player(self, resources):
    pass
def make_monster(self, monster_type):
    pass

