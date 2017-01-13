# graphical, and level components which can be used together to make a world in which you can play (and learn)

import time

import pygame

from event_handling import event_handler
from graphics import controller as graphics_controller
from settings import *

GAME_SPEED = 0.033  # seconds per frame
GRAVITY = 10

class GraphicsComponent(pygame.sprite.Sprite):
    """Base class for all Graphical Game Components"""

    id = 0

    def __init__(self, pos, size=None):
        pygame.sprite.Sprite.__init__(self)
        # create an ID for  every graphical object
        self.id = self.__class__.id
        GraphicsComponent.id += 1  # increment class variable
        self.graphics_controller = graphics_controller  # graphics controller so components can take care of blitting
        self.find_resources()  # automatically searches for the appropriate surfaces that go with the component
        # use image size if no size is specified
        if size is None:
            self.size = self.image.get_size()
        else:
            self.size = size
        # prepare image (size, alpha channel, etc.)
        self.init_image()
        self.rect = pygame.Rect(pos, self.size)  # a rectangle which represents the exact position in the game
        # DEBUG information
        if INFO:
            print("[GC] New Game Component '{}', ID: {}, pos: ({}, {}), size: ({}, {})".format(self.TYPE, self.id,
                                                                                               *self.rect))
    def __eq__(self, other):
        return self.id == other.id


    # todo: add logging code
    def __del__(self):
        try:
            if INFO:
                print("[GC] Dead Game Component '{}', ID: {}, pos: ({}, {}), size: ({}, {})".format(self.TYPE,
                                                                                                    self.id,
                                                                                                    *self.rect))
        except AttributeError as ex:
            print("[GC] '{}' not initialized right!".format(self.TYPE))
            print(ex)

    def find_resources(self):
        if self.TYPE.lower() in ['text']:
            return
        self.image = self.graphics_controller.resources[self.TYPE.lower()]  # search for image by type name

    # abstract
    def init_image(self):
        raise NotImplementedError("Please Implement this method!")

    # blit the object to the active display
    def blit(self, direct_display=False):
        self.graphics_controller.blit(self.image, self.rect)
        if direct_display:
            self.graphics_controller.update()

    # display image onto virtual screen (inside the active display)
    def display(self, screen):
        self.graphics_controller.blit_to_camera(self.image, self.rect, screen)

class LevelComponent(GraphicsComponent):
    """Base class for all level building blocks"""

    def update(self):
        raise NotImplementedError(f"Implement update for non-static type: {self.TYPE}")

# Renders text and makes a surface for it
class Text(GraphicsComponent):
    """a surface with rendered text"""
    TYPE = "Text"

    def __init__(self, text, pos, size, max_time=0, font_size=20):
        self.font = pygame.font.SysFont("Ariel", font_size)
        self.text = text
        self.image = None
        super().__init__(pos, size)
        self.start_time = time.time()
        self.max_time = max_time

    def init_image(self):
        text = self.font.render(self.text, True, (255, 255, 255))
        self.image = text  #.convert_alpha()
        if DEBUG:
            print(f"text image has init: {self.rect}")

    def update(self, dt):
        if self.max_time:
            if time.time() - self.start_time > self.max_time:
                event_handler.add()

# text meters on screen (for debugging)
# todo: enable image base meters
class Meter(GraphicsComponent):
    """meters which display game state"""
    TYPE = 'Meter'

    def __init__(self, update_function, pos):
        super().__init__(pos)
        self.update_function = update_function
        self.value = 0

    def update(self, dt):
        self.value = self.update_function()

    # todo: decide: change design, or keep doing this for non-image components
    def init_image(self):
        pass  # has no image

    def display(self):
        pass


class PhysicsEntity:
    """Base class for all physics affected entities.
    horizontally, and vertically. Every entity contains the members: x/y_accel, and x/y_speed,
    which can be used to directly influence movement """

    # these default values have been chosen for a character
    X_ACCELERATION_SPEED = 8
    Y_ACCELERATION_SPEED = 5
    JUMP_ACCELERATION_SPEED = 7

    X_MAX_SPEED = 50  # 10 pixels per meter per second
    Y_MAX_SPEED = 40  # (10 * meters) / seconds
    X_MAX_ACCEL = -1

    def __init__(self):
        self.direction = 1  # negative: left (+x), positive: right (-x)
        self.ground = None  # the ground object under it's feet
        self.stairs = None  # makes vertical movement possible
        self.x_speed = 0  # m/s
        self.y_speed = 0
        self.x_accel = 0  # m/s/s
        self.y_accel = 0
        self.move_x = False
        self.jump = False

    # moves the entity, this changes the rectangle
    # relies on delta time
    def movement_physics(self, dt):
        if self.ground:
            # check if ground is still under entity
            if not self.rect.colliderect(self.ground.rect.inflate(1, 1)):
                self.ground = None
            if not (self.x_accel or self.x_speed or self.y_accel or self.y_speed): # return if nothing is happening
                return

        if dt == 0:
            game_time = 0
        else:
            # the amount of time that has passed in the game relative to real time
            game_time = 1 / dt / GAME_SPEED  # the time that has passed in game is the: time_per_frame / game_speed_per_frame

        # x acceleration
        if self.move_x:
            # todo: find out why this is done (and document it!)
            self.x_accel -= 0  # min(self.x_accel*self.direction, self.direction * 30)  # deceleration constant

        # x speed
        if -self.X_MAX_SPEED < self.x_speed < self.X_MAX_SPEED:  # max speed
            if self.direction:  # if player direction is right
                self.x_speed = min(self.X_MAX_SPEED, self.x_accel * game_time + self.x_speed)
            else:  # player direction is left
                self.x_speed = max(-self.X_MAX_SPEED, self.x_accel * game_time - self.x_speed)
        else:
            self.x_speed -= self.direction * 30  # air displacement cost

        if self.jump:
            self.ground = None
            if self.y_accel < 0:
                self.y_accel += 1 * game_time
                if DEBUG:
                    print(f"[PE] Y acceleration decreased by: {1 * game_time}")
                self.ground = None
            elif self.ground is None:
                self.y_accel = GRAVITY * game_time
            else:
                self.y_accel = 0

                # Y speed
            if self.y_accel < 0 and not self.y_speed >= -self.Y_MAX_SPEED:
                self.y_speed += self.y_accel * game_time
            else:
                self.y_accel += 1 * game_time
        else:
            # Y acceleration
            if self.y_accel < 0:
                self.y_accel += 1 * game_time
                self.ground = None
            elif self.ground is None:
                self.y_accel = GRAVITY * game_time
            else:
                self.y_accel = 0

        # Y speed
        if self.ground:
            self.y_speed = 0
        elif not self.y_speed >= self.Y_MAX_SPEED:
            self.y_speed += self.y_accel * game_time
        else:
            self.y_accel += 1 * game_time

        # reports jump accel
        if 0 < self.y_accel < 2:
            if DEBUG:
                print("[PE] accel on turn-auround: {}".format(self.y_accel))

        # image edge collision
        l, t, _, _ = self.rect
        boundary_offset = 0
        if not 0 <= l:
            self.x_speed = 0
            self.x_accel = 0
            if 0 >= l:
                boundary_offset = 1
            else:
                boundary_offset = 1
            if DEBUG:
                print("[d] boundary offset: {}".format(self.y_speed))

        dx, dy = self.x_speed * (game_time), self.y_speed * (game_time)
        self.rect.move_ip(dx + boundary_offset, dy)
        if DEBUG:
            print("[PE] speed: ({}, {}), accel: ({}, {})".format(self.x_speed, self.y_speed, self.x_accel, self.y_accel))



class Character(LevelComponent, PhysicsEntity):
    """Physical Entity which is able to move ('left', 'right', 'up', 'down', and jump)"""

    def __init__(self, pos):
        super().__init__(pos)
        PhysicsEntity.__init__(self)

    def init_image(self):
        self.image = self.image.convert_alpha()

    # when no key press is registered anymore the input event system should notify the player it's standing still
    def move(self, movement):
        if movement == 'right':
            self.x_accel = self.X_ACCELERATION_SPEED
            self.move_x = True
        elif movement == 'left':
            self.x_accel = -self.X_ACCELERATION_SPEED
            self.move_x = True
        if movement == 'up':
            if self.stairs:
                self.y_accel = -self.Y_ACCELERATION_SPEED
                self.move_y = True
        elif movement == 'down':
            self.y_accel = self.Y_ACCELERATION_SPEED
            self.move_y = True
        if movement == 'jump':
            if self.ground is not None:
                self.y_accel = -self.JUMP_ACCELERATION_SPEED
                self.jump == True

        if self.x_accel * self.direction < 0:  # detects if direction has changed by the negative/positive difference
            if DEBUG:
                print("[D] accel:{} \tdirect: {}".format(self.x_accel, self.direction))
            self.image = pygame.transform.flip(self.image, True, False)
            self.direction *= -1  # reverse direction

    # stops acceleration
    def stop_move(self, movement):
        if movement == 'right':
            if self.x_speed > 0 or self.x_accel > 0:
                self.x_speed = 0
                self.x_accel = 0
            self.move_x = False
        elif movement == 'left':
            if self.x_speed < 0 or self.x_accel < 0:
                self.x_speed = 0
                self.x_accel = 0
            self.move_x = False
        if movement == 'up':
            pass
        elif movement == 'down':
            self.y_accel = 0
            self.y_speed = 0
        if movement == 'jump':
            pass

    # collision detection adds a new ground
    def set_ground(self, ground):
        """grounds the entity, and stops vertical movement"""
        if self.ground is None:
            self.y_accel = 0
            self.x_accel = 0
        self.ground = ground
        self.rect.bottomleft = (self.rect.bottomleft[0], ground.rect.topleft[1] + 1)

    # must be implemented by children
    def on_collision(self, other):
        if type(other) == Ground:
            self.set_ground(other)
        elif type(other) == BuildingBlock:
            # find from which side the block is touched
            print("[PE] building block touched!")


# the main player class
class Player(Character):
    """"The active player"""
    TYPE = 'Player'

    def __init__(self, pos):
        super(Player, self).__init__(pos)
        self.direction = -1 # the player sprite has a different direction

    def update(self, dt):
        self.movement_physics(dt)

    def attack(self, pos):
        if INFO:
            print("[PL] attack at: {}".format(pos))  # do something

    def stay_on_the_ground(self, dt):

        if dt == 0:
            game_time = 0
            if WARNING:
                print('[PL] dt: {}'.format(dt))
        else:
            game_time = 1 / dt / GAME_SPEED  # time passed in game = time_per_frame / game_speed_per_frame

        floor_y, self_y = self.ground.floor_pos, self.rect.bottomleft[1]
        if floor_y == self_y:  # let player be one pixel
            pass
        elif floor_y < self_y:
            self.y_accel -= GRAVITY * game_time
        elif floor_y > self_y:
            x, y, b, h = self.rect
            self.rect = pygame.Rect(x, floor_y, b, h)

        print("[d] floor_y: {}, self_y: {},")

# A graphical game component which mainly interacts with the player (and monsters)
class Monster(Character):
    """Monster baseclass"""
    TYPE = 'Monster'

    def __init__(self, pos):
        super(Monster, self).__init__(pos)

    def update(self, dt):
        self.movement_physics(dt)
        self.make_decision()

    def make_decision(self):
        raise NotImplementedError("please implement this method!")

class TestMonster(Monster):
    TYPE = 'Testmonster'

    def __init__(self, pos):
        super(TestMonster, self).__init__(pos)

    def make_decision(self):
        pass



class StaticLevelComponent(LevelComponent):
    """Base class for all image building blocks"""

    def __init__(self, resource_name, pos, size=None):
        # if the size is None; it will be determined by the image resolution
        if size is not None and len(size) != 2:
            raise ValueError("Size has to be a tuple of length 2!")
        self.TYPE = resource_name  # A correct name is needed for (image) init
        super(StaticLevelComponent, self).__init__(pos, size)

    def init_image(self):
        try:
            self.image = pygame.transform.smoothscale(self.image, self.size)
        except ValueError:
            self.image = pygame.transform.scale(self.image, self.size)

    def update(self, dt):
        pass

class Portal(StaticLevelComponent):
    """portal"""
    TYPE = 'portal'

    def __init__(self, resource_name, pos, size=None):
        super().__init__(resource_name, pos, size)

    def update(self, dt):
        pass


class BuildingBlock(GraphicsComponent):
    """buildingblock"""
    TYPE = 'BuildingBlock'

    def __init__(self, resource_name, pos, size=None):
        super(BuildingBlock, self).__init__(resource_name, pos, size=size)

class Background(StaticLevelComponent):
    """Background"""
    TYPE = 'Background'

    def __init__(self, resource_name, pos, size=None):
        super().__init__(resource_name+'_background', pos, size)

    def scale_background_to_camera(self, size):
        if size is not None:  # if the size is smaller than the camera, it will scale the to the camera size
            if size[0] <= CAMERA_WIDTH:
                size = (CAMERA_WIDTH, size[1])
            if size[1] <= CAMERA_HEIGHT:
                size = (size[0], CAMERA_HEIGHT)

            return size # do something with this


class ForeGround(StaticLevelComponent):
    """ForeGround"""
    TYPE = 'Foreground'


class Ground(StaticLevelComponent):
    """ground"""
    TYPE = 'ground'

    def __init__(self, resource_name, pos, size=None):
        super(Ground, self).__init__(resource_name, pos, size=size)


# game components list
# includes: entities
GAME_COMPONENT_TYPES = [Player, Meter, TestMonster]
GAME_COMPONENTS = {component.TYPE: component for component in GAME_COMPONENT_TYPES}

def create_game_component(self, component_type, pos):
    return GAME_COMPONENTS[component_type](pos)
