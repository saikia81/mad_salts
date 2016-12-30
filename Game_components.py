import pygame

from Graphics import controller as graphics_controller

WINDOW_WIDTH, WINDOW_HEIGHT = graphics_controller.CAMERA_WIDTH, graphics_controller.CAMERA_HEIGHT

GAME_SPEED = 0.033  # seconds per frame
GRAVITY = 20


class GraphicsComponent(pygame.sprite.Sprite):
    """Base class for all Graphical Game Components"""

    component_id = 0

    def __init__(self, pos, size=None):
        pygame.sprite.Sprite.__init__(self)
        # create an ID for  every graphical object
        self.component_id = self.__class__.component_id
        GraphicsComponent.component_id += 1  # add one
        self.graphics_controller = graphics_controller  # graphics controller so components can take care of blitting
        self.sprite = self.graphics_controller.resources[self.TYPE.lower()] # search for sprite by type name
        # use sprite size if no size is specified
        if size is None:
            self.size = self.sprite.get_size()
        else:
            self.size = size
        # prepare sprite (size, alpha channel, etc.)
        self.init_sprite()
        self.rect = pygame.Rect(pos, self.size)  # a rectangle which represents the exact position in the game

        # DEBUG information
        print("[GC] New Game Component '{}', ID: {}, pos: ({}, {}), size: ({}, {})".format(self.TYPE, self.component_id,
                                                                                           *self.rect))

    # todo: add logging code
    def __del__(self):
        try:
            print("[GC] Dead Game Component '{}', ID: {}, pos: ({}, {}), size: ({}, {})".format(self.TYPE,
                                                                                                self.component_id,
                                                                                                *self.rect))
        except AttributeError:
            print("[GC] not initialized right!")

    # abstract
    def init_sprite(self):
        raise NotImplementedError("Please Implement this method!")

    # blit the object to the active display
    def blit(self, direct_display=False):
        self.graphics_controller.blit(self.sprite, self.rect)
        if direct_display:
            self.graphics_controller.update()

    # display sprite onto virtual screen (inside the active display)
    def display(self, screen=None):
        if screen is None:
            return self.blit()
        self.graphics_controller.blit_to_camera(self.sprite, self.rect, screen)


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
    """Base class for all physics affected entities. Entity will be able to move ('left', 'right', 'up', and 'down'):
    horizontally, and vertically. Every entity contains the members: x/y_accel, and x/y_speed,
    which can be used to directly influence movement """

    X_MAX_SPEED = 80  # 10 pixels per meter per second
    Y_MAX_SPEED = 40  # (10 * meters) / seconds

    def __init__(self, pos):
        super(PhysicsEntity, self).__init__(pos)
        self.direction = 1  # negative: left (+x), positive: right (-x)
        self.ground = None  # the ground object under it's feet
        self.x_speed = 0  # m/s
        self.y_speed = 0
        self.x_accel = 0  # m/s/s
        self.y_accel = 0
        self.move_x = False

    # moves the entity, this changes the rectangle
    # relies on delta time
    def movement_pysics(self, dt):
        if self.ground:
            if not self.rect.colliderect(self.ground.rect):

                self.y_accel = 0
                self.y_speed = 0
            if not (self.x_accel or self.x_speed or self.y_accel or self.y_speed): return

        try:
            # the amount of time that has passed in the game relative to real time
            game_time = 1 / dt / GAME_SPEED  # the time that has passed in game is the: time_per_frame / game_speed_per_frame
        except ZeroDivisionError as ex:
            print('[PE] game speed problem; dt: {}, GS: {}'.format(dt, GAME_SPEED))
            print(ex)
            return  # temporary fix

        # x speed
        if -self.X_MAX_SPEED < self.x_speed < self.X_MAX_SPEED:  # max speed
            if self.direction:  # if player direction is right
                self.x_speed = min(self.X_MAX_SPEED, self.x_accel * game_time + self.x_speed)
            else:  # player direction is left
                self.x_speed = max(-self.X_MAX_SPEED, self.x_accel * game_time - self.x_speed)
            print("[PE]dt: {} \tspeed: {}".format(dt, self.x_speed))
        else:
            self.x_speed -= self.direction * 30  # air displacement cost

        # x acceleration
        if self.move_x:
            self.x_accel -= min(self.x_accel*self.direction, self.direction * 30)  # deceleration constant

        # Y speed
        if not self.y_speed >= self.Y_MAX_SPEED:
            self.y_speed += self.y_accel * game_time
        else:
            self.y_accel += 1

        # Y acceleration
        if self.ground is None:
            self.y_accel += GRAVITY * game_time
        else:
            self.y_accel = 0
            self.y_speed = 0

        # reports jump accel
        if 0 < self.y_accel < 2:
            print("[PE] accel on turn-auround: {}".format(self.y_accel))

        # level edge collision
        l, t, _, _ = self.rect
        boundary_offset = 0
        if not 0 <= l:
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
            self.x_accel = 20
            self.move_x = True
        elif movement == 'left':
            self.x_accel = -20
            self.move_x = True
        if movement == 'up':
            self.y_accel = -5
            self.move_y = True
        elif movement == 'down':
            self.y_accel = 5
            self.move_y = True
        if movement == 'jump':
            self.y_accel = 25

        if self.x_accel * self.direction < 0:  # detects if direction has changed by the negative/positive difference
            print("[D] accel:{} \tdirect: {}".format(self.x_accel, self.direction))
            self.sprite = pygame.transform.flip(self.sprite, True, False)
            self.direction *= -1

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
        self.y_accel = 0
        self.x_accel = 0
        self.ground = ground

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
        if floor_y == self_y:  # let player be one pixel
            pass
        elif floor_y < self_y:
            self.y_accel -= GRAVITY * (game_time)
        elif floor_y > self_y:
            x, y, b, h = self.rect
            self.rect = pygame.Rect(x, floor_y, b, h)

        print("[d] floor_y: {}, self_y: {},")

# the main player class
class Player(PhysicsEntity):
    """"The active player"""
    TYPE = 'Player'

    def __init__(self, pos):
        super(Player, self).__init__(pos)

    def init_sprite(self):
        self.sprite = pygame.transform.flip(pygame.transform.scale(self.sprite, (47, 30)).convert_alpha(), True, False)

    def update(self, dt):
        # print("player update!")
        self.movement_pysics(dt)

    def attack(self, pos):
        print("[PL] attack at: {}".format(pos))  # do something


# A graphical game component which mainly interacts with the player (and monsters)
class Monster(PhysicsEntity):
    """Monster baseclass"""
    TYPE = 'Monster'

    def __init__(self, pos):
        super(Monster, self).__init__(pos)

    def init_sprite(self):
        self.sprite = self.sprite.convert_alpha()

    def update(self, dt):
        self.movement_pysics(dt)
        self.make_decision()

    def make_decision(self):
        raise NotImplementedError("please implement this method!")

class TestMonster(Monster):
    TYPE = 'Testmonster'

    def __init__(self, pos):
        super(TestMonster, self).__init__(pos)

    def make_decision(self):
        pass


# game components list
# includes: entities
GAME_COMPONENT_TYPES = [Player, Meter, TestMonster]
GAME_COMPONENTS = {component.TYPE: component for component in GAME_COMPONENT_TYPES}

def create_game_component(self, component_type, pos):
    return GAME_COMPONENTS[component_type](pos)
