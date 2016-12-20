import pygame

from Graphics import controller as graphics_controller

WINDOW_WIDTH, WINDOW_HEIGHT = graphics_controller.WINDOW_WIDTH, graphics_controller.WINDOW_HEIGHT

GAME_SPEED = 0.033  # seconds per frame
GRAVITY = 3


class GraphicsComponent(pygame.sprite.Sprite):
    """Base class for all Graphical Game Components"""

    COMPONENT_ID = 0

    def __init__(self, pos, size=None):
        self.COMPONENT_ID = self.__class__.COMPONENT_ID
        GraphicsComponent.COMPONENT_ID += 1
        pygame.sprite.Sprite.__init__(self)
        self.graphics_controller = graphics_controller
        self.sprite = self.graphics_controller.resources[self.TYPE.lower()]
        if size is None:
            self.size = self.sprite.get_size()  # use sprite size if no size is specified
        else:
            self.size = size
        self.init_sprite()
        self.rect = pygame.Rect(pos, self.size)
        print("[GC] New Game Component '{}', ID: {}, size: ({}, {})".format(self.TYPE, self.COMPONENT_ID, *self.size))

    # add logging code
    def __del__(self):
        pass

    # abstract
    def init_sprite(self):
        raise NotImplementedError("Please Implement this method")

    # blit the object
    def blit(self, direct_display=False):
        self.graphics_controller.blit(self.sprite, self.rect)
        if direct_display:
            self.graphics_controller.update()

    # abstract
    def update(self, dt):
        raise NotImplementedError("Please Implement this method")

    def display(self):
        self.graphics_controller.blit(self.sprite, self.rect)


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

    # todo: decide: change design, or keep doing this for non-sprite components
    def init_sprite(self):
        pass  # has no sprite

    def display(self):
        pass


class PhysicsEntity(GraphicsComponent):
    """Base class for all physics affected entities"""
    X_MAX_SPEED = 10  # 10 pixels per second
    Y_MAX_SPEED = 10  # 10 pixels per second

    def __init__(self, pos):
        super(PhysicsEntity, self).__init__(pos)
        self.direction = 1  # negative: left (+x), positive: right (-x)
        self.x_speed = 0
        self.y_speed = 0
        self.x_accel = 0
        self.y_accel = 0

    # moves the entity, this changes the rectangle
    # relies on delta time
    def movement_pysics(self, dt):
        try:
            # the amount of time that has passed in the game relative to real time
            game_time = 1 / dt / GAME_SPEED  # the time that has passed in game is the: time_per_frame / game_speed_per_frame
        except ZeroDivisionError as ex:
            print('dt: {}'.format(dt))  # todo: debug how it's possible for 'dt' to be 0
            game_time = 0  # temporary fix

        # move left, and right
        if -self.X_MAX_SPEED < self.x_speed < self.X_MAX_SPEED:
            if self.direction:  # if player direction is right
                speed_change = max(-self.X_MAX_SPEED, self.x_accel * game_time - self.x_speed)
            else:  # player direction is left
                speed_change = min(self.X_MAX_SPEED, self.x_accel * game_time + self.x_speed)
            # self.x_speed += max(-self.X_MAX_SPEED, self.x_accel * game_time if self.direction else -min(self.X_MAX_SPEED, self.x_accel * (dt/GAME_SPEED))
            self.x_speed += speed_change
            print("[d]dt: {} \tspeed change: {}".format(dt, speed_change))  # debug code
        else:
            self.x_accel -= self.direction

        if not self.y_speed >= self.Y_MAX_SPEED:
            self.y_speed += self.y_accel * (game_time)
        else:
            self.y_accel += 1

        # max jump height
        if 0 < self.y_accel < 2:
            print("[d] jump accel on turn around: {}".format(self.y_accel))

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

        dx, dy = self.x_speed * (game_time), self.y_speed * (game_time)
        self.rect.move_ip(dx + boundary_offset, dy)
        print("[PL] speed: {}, accel: {}".format(self.x_speed, self.x_accel))

    # when no key press is registered anymore the event system should notify the player it's standing still
    def move(self, movement):
        if movement == 'right':
            self.x_accel = 4
        elif movement == 'left':
            self.x_accel = -4
        if movement == 'up':
            pass
        elif movement == 'down':
            pass
        if movement == 'jump':
            self.y_accel = 10

        if self.x_accel * self.direction < 0:  # detects if direction has changed by the negative/positive difference
            print("[D] accel:{} \tdirect: {}".format(self.x_accel, self.direction))
            self.sprite = pygame.transform.flip(self.sprite, True, False)
            self.direction *= -1

    # stops acceleration
    def stop_move(self, movement):
        if movement == 'right':
            if self.x_speed > 0 and self.x_accel > 0:
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


# the main player class
class Player(PhysicsEntity):
    """"The active player"""
    TYPE = 'Player'

    def __init__(self, pos):
        super(Player, self).__init__(pos)

    def init_sprite(self):
        self.sprite = pygame.transform.flip(pygame.transform.scale(self.sprite, (47, 30)).convert_alpha(), True, False)

    def update(self, dt):
        self.movement_pysics(dt)


    def stay_on_the_ground(self, dt):
        if self.ground is None:
            self.y_accel += GRAVITY

        try:
            # the amount of time that has passed in the game relative to real time
            game_time = 1 / dt / GAME_SPEED  # the time that has passed in game is the: time_per_frame / game_speed_per_frame
        except ZeroDivisionError as ex:
            print('dt: {}'.format(dt))  # todo: debug how it's possible for 'dt' to be 0
            game_time = 0  # temporary fix

        floor_y, self_y = self.ground.floor_pos, self.rect.bottomleft[1]
        if floor_y == self_y: # let player be one pixel
            pass
        elif floor_y < self_y:
            self.y_accel -= GRAVITY * (game_time)
        elif floor_y > self_y:
            x,y,b,h = self.rect
            self.rect = pygame.Rect(x, floor_y, b, h)

        print("[d] floor_y: {}, self_y: {},")


# A graphical game component which mainly interacts with the player (and monsters)
class Monster(PhysicsEntity):
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
# includes: entities
GAME_COMPONENT_TYPES = [Player, Meter, TestMonster]
GAME_COMPONENTS = {component.TYPE: component for component in GAME_COMPONENT_TYPES}

def create_game_component(self, component_type, pos):
    return GAME_COMPONENTS[component_type](pos)
