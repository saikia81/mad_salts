import pygame

import Graphics
from Graphics import WINDOW_WIDTH, WINDOW_HEIGHT

GAME_SPEED = 0.033  # seconds per frame
GRAVITY = 10

class GraphicsComponent(pygame.sprite.Sprite):
    """Base class for all Graphical Game Components"""

    COMPONENT_ID = 0

    def __init__(self, pos=(0, 0)):
        self.COMPONENT_ID = self.__class__.COMPONENT_ID
        self.__class__.COMPONENT_ID += 1
        pygame.sprite.Sprite.__init__(self)
        self.graphics_handler = Graphics.graphics_handler
        self.sprite = self.graphics_handler.resources[self.TYPE.lower()]
        self.init_sprite()
        self.dimensions = self.sprite.get_size()
        self.rect = pygame.Rect(pos, self.dimensions)

    def __del__(self):
        pass

    # abstract
    def init_sprite(self):
        raise NotImplementedError("Please Implement this method")

    # blit the object
    def blit(self, direct_display=False):
        self.graphics_handler.blit(self.sprite, self.rect)
        if direct_display:
            self.graphics_handler.update()

    # abstract
    def update(self, dt):
        raise NotImplementedError("Please Implement this method")

    def display(self):
        self.graphics_handler.blit(self.sprite, self.rect)


class Background(GraphicsComponent):
    """Background"""
    TYPE = 'Background' # this shouldn't be used, the name should have it's number as suffix

    def __init__(self, level_number):
        self.TYPE += str(level_number)  # A correct name is needed for initialization
        super(Background, self).__init__()

    def init_sprite(self):
        self.sprite = pygame.transform.smoothscale(self.sprite, (WINDOW_WIDTH, WINDOW_HEIGHT))


# text meters on screen (for debugging)
# todo: enable sprite base meters
class Meter(GraphicsComponent):
    """meters which display game state"""
    TYPE = 'Meter'

    def __init__(self, update_function, pos):
        super(Player, self).__init__(pos, self.TYPE)
        self.update_function = update_function
        self.value = 0

    def update(self, dt):
        self.value = self.update_function()

    # todo: change design, or keep doing this for non-sprite components
    def init_sprite(self):
        pass  # has no sprite

    def display(self):
        pass


class MassEntity(GraphicsComponent):
    X_MAX_SPEED = 10  # 10 pixels per second
    Y_MAX_SPEED = 10  # 10 pixels per second
    def __init__(self, pos):
        super(MassEntity, self).__init__(pos)
        self.direction = 1  # negative: left (+x), positive: right (-x)
        self.x_speed = 0
        self.y_speed = 0
        self.x_accel = 0
        self.y_accel = 0

# the main player class
class Player(MassEntity):
    """"The active player"""
    TYPE = 'Player'

    def __init__(self, pos):
        super(Player, self).__init__(pos)

    def init_sprite(self):
        self.sprite = pygame.transform.scale(self.sprite, (47, 30)).convert_alpha()

    # moves the player, this changes the state of placement
    # physics included (relies on delta time)
    def update(self, dt):
        # move left, and right
        if -self.X_MAX_SPEED < self.x_speed < self.X_MAX_SPEED:
            self.x_speed += min(self.X_MAX_SPEED, self.x_accel * (dt/GAME_SPEED)) if self.direction else max(-self.X_MAX_SPEED, self.x_accel * (dt/GAME_SPEED))
            print("[d]speed change: {}".format(self.x_speed))
        else:
            self.x_accel -= self.direction

        if not self.y_speed >= self.Y_MAX_SPEED:
            self.y_speed += self.y_accel * (dt/GAME_SPEED)

        # max jump height
        if self.y_speed >= 6:
            print("[d] jump accel on turn around: {}".format(self.y_accel))
            self.y_accel = -GRAVITY

        # level edge collision
        l, t, _, _ = self.rect
        boundary_offset = 0
        if not 0 <= l <= WINDOW_WIDTH:
            self.x_speed = 0
            self.x_accel = 0
            if 0 >= l:
                boundary_offset = 1
            else:
                boundary_offset = 1
            print("[d] boundary offset: {}".format(self.y_speed))

        dx, dy = self.x_speed * (dt / GAME_SPEED), self.y_speed * (dt / GAME_SPEED)
        self.rect.move_ip(dx + boundary_offset, dy)
        print("[PL] speed: {} |accel: {}".format(self.x_speed, self.x_accel))

    # when no key press is registered anymore the event system should notify the player it's standing still
    def move(self, movement):
        if movement == 'right':
            self.x_accel = 2
        elif movement == 'left':
            self.x_accel = -2
        if movement == 'up':
            pass
        elif movement == 'down':
            pass
        if movement == 'jump':
            self.y_accel = 10

        if self.x_accel * self.direction < 0:  # detects if direction has changed by negative, positive difference
            self.sprite = pygame.transform.flip(self.sprite, True, False)

    # stops acceleration
    def stop_move(self, movement):
        if movement == 'right':
            if self.x_speed > 0 and self.y_accel < 0:
                self.x_speed = 0
                self.x_accel = 0
        elif movement == 'left':
            if self.x_speed < 0 and self.x_accel < 0:
                self.x_speed = 0
                self.x_accel = 0
        if movement == 'up':
            pass
        elif movement == 'down':
            pass
        if movement == 'jump':
            pass

# A graphical game component which mainly interacts with the player (and monsters)
class Monster(MassEntity):
    """Monster baseclass"""
    TYPE = 'Monster'
    def __init__(self, pos):
        super(Monster, self).__init__(pos)

    def init_sprite(self):
        self.sprite = self.sprite.convert_alpha()

class TestMonster(Monster):
    TYPE = 'Testmonster'

    def __init__(self, pos):
        super(TestMonster, self).__init__(pos)

    def update(self, dt):
        pass

# game components list
# includes: entities, world blocks, and background
GAME_COMPONENT_TYPES = [Player, Meter, TestMonster]
GAME_COMPONENTS = {component.TYPE: component for component in GAME_COMPONENT_TYPES}

#
def create_game_component(self, component_type, pos):
    return GAME_COMPONENTS[component_type](pos)

