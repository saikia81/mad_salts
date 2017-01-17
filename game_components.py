# graphical, and level components which can be used together to make a world in which you can play (and learn)

import time

import pygame

from event_handling import event_handler
from graphics import controller as graphics_controller
from configurations import *

GAME_SPEED = 0.033  # seconds per frame (1s/30fps)
GRAVITY = 6


# moves the entity, this changes the rectangle
# relies on delta time
class PhysicsEntity:
    """Base class for all physics affected entities.
    horizontally, and vertically. Every entity contains the members: (x/y)_accel, and (x/y)_speed,
    which can be used to directly influence movement (or so I claim)"""

    # values that are defined by the physical constraints and characteristics
    RIGHT = 1  # going right on the X-axis means a positive change for x
    LEFT = -1
    UP = -1
    DOWN = 1  # going down on the y-axis means a positive change in y

    # these default values have been chosen for a non-moving entity
    X_ACCELERATION_SPEED = 0
    Y_ACCELERATION_SPEED = 0
    JUMP_SPEED = 0

    X_MAX_SPEED = 10  # 10 pixels per second
    Y_MAX_SPEED = 50  # (10 * meters) / seconds
    X_MAX_ACCEL = 30  # general limit, think about adding force (F=M*a)

    def __init__(self):
        self.direction = 1  # negative: left (+x), positive: right (-x)
        self.ground = None  # the ground object under it's rectangle
        self.stairs = None  # makes vertical movement possible
        self.x_speed = 0  # speed
        self.y_speed = 0
        self.x_accel = 0  # acceleration
        self.y_accel = 0
        self._dx = 0  # update these variables for the movement
        self._dy = 0
        self.x_movement = False
        self.jumping = False

    # moves the entity, this changes the rectangle
    # relies on delta time
    def physics_movement(self, dt):  # todo: rewrite with Newtonian physics
        # ground should be checked/set before this method is called
        if not self.jumping:
            if self.ground is not None and not (self.x_accel or self.x_speed or self.y_accel or self.y_speed):
                return
        # first move the player by it's acceleration (which can have been set by something else)
        # x accel define the acceleration based on current accel, and movement input
        x_accel_direction = lambda: (self.x_accel / abs(self.x_accel)) if self.x_accel != 0 else 0
        x_move_direction = lambda: (self.x_speed / abs(self.x_speed)) if self.x_speed != 0 else 0
        # multiply by the direction (+)or(-)self / self
        if self.x_accel != 0:
            # If accel is too high, X_MAX_ACCEL limits it
            #self.x_accel = min(abs(self.x_accel), self.X_MAX_ACCEL) * x_accel_direction()
            # x speed change
            # speed up or down. If speed is to high, X_MAX_SPEED limits it
            self.x_speed += x_accel_direction()
            self.x_speed = min(abs(self.x_accel + self.x_speed), self.X_MAX_SPEED) * x_move_direction()
            # using acceleration means you lose it (pushing costs energy)
            # accel minuts 0 or a
            self.x_accel -=  self.direction
            # self.x_accel - min(abs(self.x_accel), 0) * (self.x_accel / abs(self.x_accel))
        elif self.x_speed != 0:  # when there is no acceleration, but you are moving: you loose speed (de-accel)
            # 1m/s divided by the time that has passed = 1m/(s**2) multiplied by it's direction
            # loose max_speed in 1 second time, or just make x speed 0
            self.x_speed -= min(abs(self.x_speed), self.X_MAX_SPEED * (dt / 1000)) * x_move_direction()

        y_accel_direction = lambda: (self.y_accel / abs(self.y_accel)) if self.y_accel != 0 else 0
        y_move_direction = lambda: (self.y_speed / abs(self.x_speed)) if self.y_speed != 0 else 0

        if self.jumping:
            if self.ground:
                self.y_speed = -self.JUMP_SPEED  # if jumping set speed directly at once
                print("DB JUMP!")
            else:
                if self.y_speed < 0:  # going up
                    self.y_speed += GRAVITY * (dt / 60)
                else:
                    self.jumping = False
        else:
            if self.ground:
                self.y_speed = 0
            else:
                self.y_speed += GRAVITY  # min(abs(self.y_speed + self.y_accel), self.Y_MAX_SPEED)

        # move rect by delta movement
        dx, dy = self.x_speed, self.y_speed

        self.rect.move_ip(dx, dy)

        if PHYSICS_DEBUG:
            print(f"[PE] {repr(self)} speed:({(self.x_speed)}, {(self.y_speed)}), accel:({(self.x_accel)}, {(self.y_accel)})")
            print(f"[PE] movement:({dx}, {dy})")


class GraphicsComponent(pygame.sprite.Sprite):
    """Base class for all Graphical Game Components"""

    id = 0

    def __init__(self, pos, size=None):
        pygame.sprite.Sprite.__init__(self)
        # create an ID for  every graphical object
        self.id = self.__class__.id
        GraphicsComponent.id += 1  # increment class identifier for the next
        self.graphics_controller = graphics_controller  # graphics controller so components can take care of blitting
        self._find_resource()  # automatically searches for the appropriate surfaces that go with the component
        # use image size if no size is specified
        if size is None:
            self.size = self.resource.get_size()
        else:
            self.size = size
        # prepare image (size, alpha channel, etc.)
        self._init_image()
        self.rect = pygame.Rect(pos, self.size)  # a rectangle which represents it's position in the level
        # DEBUG information
        if INFO:
            print("[GC] New Game Component '{}', ID: {}, pos: ({}, {}), size: ({}, {})".format(self.TYPE, self.id,
                                                                                               *self.rect))
    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        return str(self.id)

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

    def _find_resource(self):
        try:
            self.resource = self.graphics_controller.resources[self.TYPE.lower()]  # search for image by type name
        except Exception:
            self.resource = self.graphics_controller.resources[self.TYPE.lower()[:-11]] # search for image by type name

    # abstract
    def _init_image(self):
        self.image = self.resource

    # blit the object to the active display
    def blit(self, direct_display=False):
        self.graphics_controller.blit(self.image, self.rect)
        if direct_display:
            self.graphics_controller.update()

    # display image onto virtual screen (inside the active display)
    def display(self, screen=None):
        if self.image == None:
            if Warning: print(f"[GC] {self} has no image!")
            return
        if screen is not None:
            self.graphics_controller.blit_to_camera(self.image, self.rect, screen)
        else:
            graphics_controller.blit(self.image, self.rect)

class GameComponent(GraphicsComponent):
    """Base class for all level building blocks"""

    def __init__(self, pos, size=None):
        super().__init__(pos, size)
        self.level = None

    def __repr__(self):
        return f"{self.TYPE}: {super().__repr__()}"

    def update(self, dt):
        raise NotImplementedError(f"Implement update for non-static type: {self.TYPE}")

    def kill(self):
        if self.level:
            self.level.del_component(self)

class Weapon(GraphicsComponent):
    TYPE = 'Weapon'
    def __init__(self, owner, ammo_type):
        self.owner = owner
        x, y, _, _ = owner.rect
        # super().__init__((x,y))
        self.ammo_type = ammo_type
        self.amount = 20  # new weapon always has 5 ammo
        self.projectile = None

    def set_ammo(self, ammo_type, amount):
        self.ammo_type = ammo_type
        self.amount = amount

    def add_ammo(self, amount):
        self.amount += amount

    def has_ammo(self):
        return self.amount > 0

    def use(self, point): # direction is the position of the mouse
        self.owner.level.add_component(self.projectile)
        if not self.projectile:
            return
        if point[0] > self.owner.rect.centerx:
            direction = 'right'
        else:
            direction = 'left'
        self.projectile.throw(direction)
        self.projectile = None

    def load_projectile(self):
        if self.amount > 0:  # check if empty
            self.amount -= 1
            self.projectile = self.ammo_type(self.owner.rect.center)


class Vial(GameComponent, PhysicsEntity):
    TYPE = 'Erlemeyer1'
    # these default values have been chosen for a non-moving entity
    X_ACCELERATION_SPEED = 30
    Y_ACCELERATION_SPEED = 25
    JUMP_SPEED = 50

    X_MAX_SPEED = 30  # 10 pixels per second
    Y_MAX_SPEED = 50  # (10 * meters) / seconds
    X_MAX_ACCEL = 30  # general limit, think about adding force (F=M*a)

    DAMAGE = 100

    def __init__(self, pos, size=(14, 14)):
        super().__init__(pos, size)
        PhysicsEntity.__init__(self)

    def _init_image(self):
        self.image = pygame.transform.smoothscale(self.resource, self.size)

    def update(self, dt):
        self.physics_movement(dt)
        pygame.transform.rotate(self.image, 360*(dt/1000))

    def on_collision(self, other):
        if type(other) == Monster:
            self.kill()
        elif type(other) == Ground:
            self.kill()
            print("erlemeyer fell on the ground")

    def throw(self, direction):
        if direction == 'right':
            self.x_speed = 30
            self.direction = self.RIGHT
        elif direction == 'left':
            self.x_speed = -30
            self.direction = self.LEFT
        else:
            raise ValueError(f"Movement type not supported: {movement}")
        self.y_speed = -12

    #start with a speed by acceleration, and decrease speed over time
    # start with speed up, decreese over time
    def physics_movement(self, dt):  # todo: rewrite with Newtonian physics
        # first move the player by it's acceleration (which can have been set by something else)
        # x accel define the acceleration based on current accel, and movement input
        x_accel_direction = lambda: (self.x_accel / abs(self.x_accel)) if self.x_accel != 0 else 0
        x_move_direction = lambda: (self.x_speed / abs(self.x_speed)) if self.x_speed != 0 else 0
        # multiply by the direction (+)or(-)self / self
        self.x_speed -= x_move_direction()
        self.y_speed += 1

        # move rect by delta movement
        dx, dy = self.x_speed, self.y_speed

        self.rect.move_ip(dx, dy)

        if PHYSICS_DEBUG:
            print(
                f"[PE] {repr(self)} speed:({(self.x_speed)}, {(self.y_speed)}), accel:({(self.x_accel)}, {(self.y_accel)})")
            print(f"[PE] movement:({dx}, {dy})")

# Renders text and makes a surface for it
class Text(GameComponent):
    """a surface with rendered text"""
    TYPE = "Text"

    # max time in seconds
    def __init__(self, text, pos, size, max_time=-1, font_size=20):
        self.font = pygame.font.SysFont("Ariel", font_size)
        self.text = text
        self.image = None
        super().__init__(pos, size)
        self.start_time = time.time()
        self.max_time = max_time

    def _find_resource(self):
        pass  # no resources are available for text

    def _init_image(self):
        text = self.font.render(self.text, True, (255, 255, 255))
        self.image = text  #.convert_alpha()

    def update(self, dt):
        if self.max_time == -1:
            pass
        elif self.max_time > 0:
            if time.time() - self.start_time > self.max_time:
                self.kill()

    def is_alive(self):
        return self.max_time > 0

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
    def _init_image(self):
        pass  # has no image

    def display(self):
        pass

class Character(GameComponent, PhysicsEntity):
    """Physical Entity which is able to move ('left', 'right', 'up', 'down', and jumping)"""

    # these default values have been chosen for a Player
    X_ACCELERATION_SPEED = 14  # pixels/(s**2)
    Y_ACCELERATION_SPEED = 20
    JUMP_SPEED = 30
    # the player is about 64 pixels high (which might translate to 2 or more meters
    X_MAX_SPEED = 18  # pixels per second
    Y_MAX_SPEED = 14  # (10 * meters) / seconds
    X_MAX_ACCEL = -1  # think about adding force (F=M*a)

    def __init__(self, pos, size):
        # every character has a name
        self.walk_images = []
        self.walk_cycle = 0
        self.resource = []
        super().__init__(pos, size)
        PhysicsEntity.__init__(self)
        self.life_points = 100
        self.invulnerable = 0  # amount of invulnerable frames

    # all characters have a list as resource
    def _find_resource(self):
        resource_amount = 0
        for resource_name in graphics_controller.resources.keys():
            if f'{self.name.lower()}' in resource_name:
                self.walk_images.append(graphics_controller.resources[resource_name])
                resource_amount += 1
        self.image_amount = resource_amount

    def _init_image(self):  # prepare the images, and cycle variables

        right_walk_images = self.walk_images
        left_walk_images = []

        for i in range(self.image_amount):
            self.walk_images[i] = pygame.transform.smoothscale(self.walk_images[i].convert_alpha(), self.size)
            left_walk_images.append(pygame.transform.flip(self.walk_images[i], True, False))
        self.directional_walk_images = {-1*self.direction: left_walk_images, 1*self.direction: right_walk_images}
        self.image = self.walk_images[self.walk_cycle]
        print(f"[CH] images init: {self.image_amount}")

    def _next_image(self):
        if self.x_movement:
            self.walk_images = self.directional_walk_images[self.direction]
            self.walk_cycle += 1
            if self.walk_cycle >= 7: # there are 7 walking animations
                self.walk_cycle = 0
            self.image = self.walk_images[self.walk_cycle]
        if self.invulnerable:  # blink once a tick
            if self.image == None:
                self.image = self.walk_images[self.walk_cycle]
            else:
                self.image = None

    def is_alive(self):
        return self.life_points > 0

    # when no key press is registered anymore the input event system should notify the player it's standing still
    # monsters, and other self moving entities should decide on their own when to stop
    def move(self, movement):
        if movement == 'right':
            self.x_accel = self.X_ACCELERATION_SPEED
            self.x_movement = True
            self.direction = self.RIGHT
        elif movement == 'left':
            self.x_accel = -self.X_ACCELERATION_SPEED
            self.direction = self.LEFT
            self.x_movement = True
        elif movement == 'up':
            if self.stairs:
                self.y_accel = -self.Y_ACCELERATION_SPEED
                self.y_movement = True
        elif movement == 'down':
            if self.stairs:
                self.y_accel = self.Y_ACCELERATION_SPEED
                self.y_movement = True
        elif movement == 'jump':
            self.jumping = True

        else:
            raise ValueError(f"Movement type not supported: {movement}")

        if self.x_accel * self.direction < 0:  # detects if direction has changed by the negative/positive change
            if DEBUG:
                print("[D] accel:{} \tdirect: {}".format(self.x_accel, self.direction))
            self.direction *= -1  # reverse direction
            self.turn_around()

    # stops acceleration, and speed
    def stop_move(self, movement):
        if movement == 'right':
            if self.x_speed > 0 or self.x_accel > 0:
                self.x_speed = 0
                self.x_accel = 0
            self.x_movement = False
            self.walk_cycle = 0
        elif movement == 'left':
            if self.x_speed < 0 or self.x_accel < 0:
                self.x_speed = 0
                self.x_accel = 0
                self.walk_cycle = 0
            self.x_movement = False
        elif movement == 'up':
            self.y_movement = False
        elif movement == 'down':
            self.y_movement = False
        elif movement == 'jump':
            pass
        else:
            raise ValueError(f"Movement type not supported: {movement}")

    def turn_around(self):
        self.walk_images = self.directional_walk_images[self.direction]
        self.walk_cycle = 0  # walk animation must restart when moving in different direction

    # collision detection adds a new ground
    def set_ground(self, ground):
        """grounds the entity, and stops vertical movement"""
        if self.ground is None:
            self.y_accel = 0
            self.y_speed = 0

        self.ground = ground
        self.rect.bottom = ground.rect.top + 1
        self.rect.bottom = ground.rect.top + 1

    # must be implemented for physical entities
    def on_collision(self, other):
        if type(other) == Ground:
            if other.rect.left < self.rect.centerx < other.rect.right:
                self.set_ground(other)
            elif self.rect.left < other.rect.left:
                self.x_accel = min(self.x_accel, 0)  # don't move right
            elif self.rect.right > other.rect.right:
                self.x_accel = max(self.x_accel, 0)  # don't move left

        elif type(other) == BuildingBlock:
            # find from which side the block is touched
            print("[CH] building block touched!")

    def update(self, dt):
        self.physics_movement(dt)
        self._next_image()

# the controlled player(s) class
class Player(Character):
    """"The active player"""
    TYPE = 'Player'

    def __init__(self, pos, size):
        self.name = self.TYPE
        self.direction = 1  # the player sprite starting direction is 'right'
        self.walk_cycle = 0
        super().__init__(pos, size)
        self.accesories = {Weapon: None}  # things you wear, and hold
        self.inventory = {} # item: item_amount
        self.accesories[Weapon] = Weapon(self, Vial)
        self._first_attack = True

    def display(self, screen):
        super().display(screen) # display self
        # display all things the player is holding, and wearing
        for acc in self.accesories.values():
            if acc is not None and not isinstance(acc, GraphicsComponent):
                acc.display(screen)

    def update(self, dt):
        if dt == 0: return  # time must pas, else an update is meaningless
        super().update(dt)
        if self.invulnerable:
            self.invulnerable -= 1
            if PLAYER_DEBUG: print(f"invulnerable for: {self.invulnerable}")

    def on_collision(self, other):
        if isinstance(other, Monster):  # if it's a monster (or subtype)
            self.x_accel /= 2  # half the acceleration
            anti_direction = - (other.rect.centerx - self.rect.centerx) / abs(other.rect.centerx - self.rect.centerx or 1)
            self.damage(20, anti_direction)

        else:
            super().on_collision(other)

    # throw Vial
    def attack(self, relative_pos):
        pos = relative_pos[0] - self.level.camera.rect.left, relative_pos[1] - self.level.camera.rect.top
        if self._first_attack:
            length = len(SALT_DISSOLVING_INSTRUCTIONS)
            firstpart, secondpart = SALT_DISSOLVING_INSTRUCTIONS[: int(length/ 2)+2], SALT_DISSOLVING_INSTRUCTIONS[int(length/2)+2:]
            self.level.add_component(Text(firstpart, (self.rect.left, self.rect.top-30),
                                          (200,50), max_time=100,font_size=22))
            self.level.add_component(Text(secondpart, (self.rect.left, self.rect.top-10),
                                          (200,50), max_time=100,font_size=22))
            self.level.freeze = True
            self._first_attack = not self._first_attack
        weapon = self.accesories[Weapon]
        if weapon is not None and weapon.has_ammo():
            weapon.load_projectile()
            weapon.use(pos)
        if DEBUG:
            print("[PL] attack at: {}".format(pos))  # do something


    def stop_independent_x_movement(self, dt):  # for boats or other vehicles
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

    def damage(self, damage, direction):
        if self.invulnerable <= 0:
            self.invulnerable = 60  # (1 / (0.033 second/frame)) * 2 seconds ~= 60 frames
            if DEBUG: print("f[PL] invulnerable for {int(2 * 1/GAME_SPEED)} ticks")  # debug invulnerability time'

            self.x_accel = 6 * direction
            self.y_accel = - self.JUMP_SPEED / 2  # you get thrown in the air
            self.jumping = True


# A graphical game component which mainly interacts with the player (and monsters)
class Monster(Character):
    """Monster baseclass"""
    TYPE = 'Monster'

    X_ACCELERATION_SPEED = 5
    Y_ACCELERATION_SPEED = 15
    JUMP_SPEED = 20

    X_MAX_SPEED = 10  # 10 pixels per meter per second
    Y_MAX_SPEED = 10  # (10 * meters) / seconds

    def __init__(self, pos, size):
        super().__init__(pos, size)
        self.enemy = None
        self.life_points = 100

    def update(self, dt):
        super().update(dt)
        self.make_decision()
        print(f'schagel PE: xspeed: {self.x_speed}, pos: {self.rect}')

    def make_decision(self):
        raise NotImplementedError("please implement this method!")

    def on_collision(self, other):
        if type(other) == Player:
            self.x_accel /= 2
        elif type(other) == Vial:
            self.damage(other.DAMAGE)
        else:
            super().on_collision(other)

    def damage(self, damage):
        self.life_points -= damage
        if self.life_points <= 0:
            self.kill()
    def kill(self):
        self.level.add_component(Text("NaCl -> Na+(aq) + Cl-(aq)", self.rect.topleft, (200, 100), max_time=10))
        super().kill()

class TestMonster(Monster):
    def __init__(self, pos):
        super().__init__(pos)

    def make_decision(self):
        pass

# sheep with spiky-animal in dutch combined: schaap-egel
class Schagel(Monster):
    """Schagel is a jumping monster"""
    def __init__(self, pos, size):
        self.direction = -1  # sprite faces left
        self.name = self.__class__.__name__
        super().__init__(pos, size)

    # basic decision making
    # todo: implement AI for character's decision making
    def make_decision(self):
        if self.enemy is None:
            return
        if self.enemy.rect.centerx-15 < self.rect.centerx:  # 10 is so the monster walks through the player
            if self.direction == self.RIGHT:
                self.stop_move('right')
            self.move('left')
        elif self.enemy.rect.centerx+15 > self.rect.centerx:
            if self.direction == self.LEFT:
                self.stop_move('left')
            self.move('right')
        if self.enemy.rect.center[1] > self.rect.centery and 200 > abs(self.enemy.rect.centerx - self.rect.centerx):
            self.move('jump')
        if self.ground and (self.ground.rect.right - 20 < self.rect.centerx or
                            self.rect.centerx < self.ground.rect.left + 20):
            self.move('jump')

class Portal(GameComponent):
    """portal"""
    TYPE = 'portal'

    def __init__(self, resource_name, pos, size=None):
        super().__init__(resource_name, pos, size)

    def update(self, dt):
        pass

# static parts

class StaticLevelComponent(GameComponent):
    """Base class for all image building blocks"""

    def __init__(self, resource_name, pos, size=None):
        # if the size is None; it will be determined by the image resolution
        if size is not None and len(size) != 2:
            raise ValueError("Size has to be a tuple of length 2!")
        self.TYPE = resource_name  # A correct name is needed for (image) init
        super(StaticLevelComponent, self).__init__(pos, size)

    def __repr__(self):
        return super().__repr__() + f"pos: {self.rect.topleft}"

    def _init_image(self):
        try:
            self.image = pygame.transform.smoothscale(self.resource, self.size)
        except ValueError as ex:
            if WARNING:
                print(f"[SC] pygame.transform.smoothscale failed with error: {ex}")
            self.image = pygame.transform.scale(self.resource, self.size)

    def update(self, dt):
        pass

    def on_collision(self, other):
        pass

class BuildingBlock(StaticLevelComponent):
    """buildingblock"""
    TYPE = 'BuildingBlock'

    def __init__(self, resource_name, pos, size=None):
        super(BuildingBlock, self).__init__(resource_name, pos, size=size)

class Background(StaticLevelComponent):
    """Background"""
    TYPE = 'Background'

    def __init__(self, resource_name, pos, size=None):
        super().__init__(resource_name+'_background', pos, size)

    @staticmethod
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
GAME_COMPONENT_TYPES = [Player, Meter, Portal, Schagel, Text]
GAME_COMPONENTS = {component.__name__: component for component in GAME_COMPONENT_TYPES}

def create_game_component( component_type, pos, size=None):
    return GAME_COMPONENTS[component_type](pos, size=size)
