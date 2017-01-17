from game_components import *
from graphics import controller as graphics_handler, Camera, complex_camera
import random

# make an Object file, and add all needed resources (based on folder position and file names)
class Level:
    """A class with image resources, and helper functions"""

    def __init__(self, level_name, player, static_world_components, dynamic_world_components, background=None,
                 level_size=None, camera_type=None):
        if level_size == None:
            level_size = background.size
        self.background = background
        self.size = level_size
        self.name = level_name
        # a dictionary with all image related game components
        self.player = player
        self.characters = []  # starts empty; is filled by npc, and the player(s)
        self.npc = pygame.sprite.Group()
        self.static_components = static_world_components  # image parts (e.g. background, ground)
        self.dynamic_components = dynamic_world_components  # image parts (e.g. swings, moving objects, bullets)
        self.components = [] + self.static_components + self.dynamic_components  # redundant list; fast requesting component
        self.add_character(player)
        # build the static game world
        self.image, self.rect = self.build_background(level_size, background=background,
                                                      static_components=self.static_components)
        if camera_type is not None:
            self.camera = Camera(camera_type, player.rect, level_size)  # the screen view
            # todo: decide on who should hold the camera
            graphics_handler.set_camera(self.camera)  # makes it possible to blit directly to the graphics handler
        else:
            self.camera = None
        self.freeze = False  # freezes all updates to components
        if INFO:
            print("[LV] image '{}' loaded".format(level_name))
        self.killed_monster = 0

    @staticmethod
    def build_background(level_size, background=None, static_components=None, colour=(255, 150, 0)):
        if static_components is None:
            static_components = []

        level = pygame.Surface(level_size)
        level.fill(colour)
        level_rect = level.get_rect()
        if background is not None:
            level.blit(background.image, background.rect)
            if INFO:
                print('[LV] Background blitted in build: {}'.format(background.rect))

        for placement in [Background, Ground]:  # first blit Background, afterwards Ground
            for component in static_components:
                # if not self.level_rect.contains(component.rect): continue  # only if component fits in level
                if type(component) == placement:
                    level.blit(component.image.convert_alpha(), component.rect)
        if INFO:
            print("image surface created: {}".format(level))
        return level, level_rect

    # game component management)
    def add_world_component(self, world_component):
        self.static_components.append(world_component)
        if DEBUG:
            print("added image to game world: " + repr(world_component.image))
        self.image.blit(world_component.image, world_component.rect)
        self.components.append(world_component)

    # when adding a dynamic level component to the level, this method should be used exclusively
    def add_component(self, component):
        self.dynamic_components.append(component)
        self.components.append(component)
        component.level = self  # can't get sprite groups to work

    def del_component(self, component):
        if type(component) == Player:
            self.player = None
        try:
            del self.dynamic_components[self.dynamic_components.index(component)]  # component should have __eq__ overridden
        except ValueError as ex:
            if WARNING:
                print(f"[LL] couldn't find component in dynamic components list {component}")
        try:
            del self.components[self.components.index(component)]
        except ValueError as ex:
            if WARNING:
                print(f"[LL] couldn't find component in components list {component}")

    def add_character(self, character):
        self.characters.append(character)
        if character.TYPE == 'Monster':
            character.enemy = self.player
        character.level = self
        #self.npc.add(character)

    def del_character(self, character):
        index = self.characters.index(character)
        del self.characters[index]
        if character is self.player:
            self.player = None
        if isinstance(character, Monster):
            self.killed_monster += 1

    def del_component_index(self):  # maybe implement this
        pass

    def get_dynamic_components(self):
        """builds a (flat) list with all dynamic game component"""
        return [x for x in self.dynamic_components]

    def get_game_components(self):
        """Builds a new list with all static and dynamic components"""
        # first get the static components, as these will be blitted over by the dynamic ones
        return [x for x in self.components]

    def update(self, dt):
        """update all game components in the current level (does not checks for collisions)"""
        if self.player is None:
            self.end()
        if self.freeze:
            if self.player:

                self.add_component(Text("you can unfreeze the screen with 'f'",
                                        (self.camera.rect.centerx-80, self.camera.rect.centery-160), (200, 200),
                                        max_time=1,font_size=25))
            return
        for character in self.characters:
            if character.is_alive():
                character.update(dt)
            else:
                self.del_character(character)
        for component in self.dynamic_components:
            component.update(dt)
        # update camera as last
        if self.camera and self.player:
            self.camera.update(self.player.rect)
        if len(self.characters) <= 1:  # there should always be one monster in the game
            self.add_character(Schagel((random.randint(0, self.size[0]), self.size[1]/2), (58, 52)))

    def check_level_finished(self):
        if self.killed_monster >= 8:
            return True
        return False

    # collision detection per entity that the function is called with
    @staticmethod
    def detect_collision(entity, components):
        if entity.ground:
            return
        for component in components:
            if pygame.sprite.collide_rect(entity, component):
                if component:  # makes it acceptable to have None in components
                    if DEBUG:
                        print("[CD] ground collision!")
                    return component
                else:
                    if DEBUG:
                        print("[CD] unknown collision: {}".format(component))

    @staticmethod
    def detect_entity_collision(entity):
        pass

    # returns None, or the first found ground
    @staticmethod
    def find_type_collision(entity, components, component_type):
        for component in components:
            if pygame.sprite.collide_rect(entity, component) and type(component) == component_type:
                if DEBUG:
                    print("[CD] {} collision!".format(component_type))
                return component

    # calls on_collision on all entities
    @staticmethod
    def detect_type_collisions(entities, components, component_types):
        """detects the collision between all static components, of one or multiple types, and 'entities';
        calls on_collision on every entity"""
        for entity in entities:
            for component in components:
                if type(component) in component_types and pygame.sprite.collide_rect(entity, component):
                    if DEBUG:
                        print(f"[CD] collision: '{entity}', '{component}'!")
                    component.on_collision(entity)
                    if isinstance(component, PhysicsEntity):
                        entity.on_collision(component)

    def detect_characters_ground(self):
        for character in self.characters:
            for component in self.static_components:
                if type(component) in [Ground, BuildingBlock] and pygame.sprite.collide_rect(character, component):
                    if DEBUG: print(f"[CD] ground collision: '{character}', '{component}'!")
                    character.on_collision(component)
                    break
                character.ground = None

    # checks collision between all characters with zero double-checks
    def detect_character_collisions(self):
        """Check collision between every character once.
         Calls the collision method on each with as argument the other"""
        temp = [character for character in self.characters]
        for character0 in self.characters:
            for character1 in temp:
                if character0 != character1 and pygame.sprite.collide_rect(character0, character1):
                    character0.on_collision(character1)
                    character1.on_collision(character0)
                    if DEBUG:
                        print(f"[LV] collision between: {character0} and {character1}")
            del temp[0]

    def detect_characters_out_of_bound(self):
        for character in self.characters:
            if not pygame.sprite.collide_rect(character, self):
                self.del_character(character)
                if DEBUG:
                    print(f"char out of bound: {character}")
            if 0 > character.rect.left:
                character.rect.left = 0
            elif character.rect.left > self.size[0]: # level x size
                character.rect.right = self.size[0]

    # check collisions for affected parties
    def detect_collisions(self):
        self.detect_characters_out_of_bound()
        self.detect_character_collisions()
        self.detect_characters_ground()
        self.detect_type_collisions(self.characters, self.dynamic_components, [Vial])
        self.detect_type_collisions(self.dynamic_components, self.static_components, [Ground])


    # displays all image components from back- to foreground
    def display(self):
        """calls display on every component;
        blitting them, and adding their rectangle to a dirty rectangles list"""
        # first put the background on the display
        if self.camera is None:
            camera_rect = None
        else:
            camera_rect = self.camera.rect

        graphics_controller.blit(self.image, self.rect, self.camera.rect) # display level base image
        for dynamic_component in self.dynamic_components:  # things like throw-ables
            dynamic_component.display(camera_rect)
        for character in self.characters:  # player and NPCs
            character.display(camera_rect)
        for static_component in self.static_components:  # foreground is the last to be displayed
            if type(static_component) == ForeGround:
                static_component.display(camera_rect)

    def end(self):
        self.freeze = True
        self.add_component(Text("End Of Game", (self.camera.rect.centerx, self.size[1] / 2), (100, 50), font_size=30))

    def __del__(self):
        graphics_handler.unset_camera()
        if INFO:
            print("[LL] image '{}' unloaded".format(self.name))



# component order matters!
def level_builder(level_number):
    graphics_controller.init_screen()
    # any component that is part of the level should be added to world_components list
    static_level_components = []  # additional dynamic blocks and other level_number components
    dynamic_level_components = []
    background_pos = (0, 0)
    level_size = None
    player_size = (82, 64)
    camera_type = complex_camera
    player_pos = (50, 50)
    if level_number == -1:  # testing
        level_size = (1920,1080)
        graphics_controller.init_screen()
        level_name = 'forest'
        player = Player((50, 50), size=player_size)  # player and it's starting position in the level_number
        ground_pos = 500
        static_level_components.append(Ground('forest_ground01', (0, ground_pos)))
        static_level_components.append(Ground('forest_ground02', pos=(850, ground_pos)))
        dynamic_level_components.append(Text(MOVEMENT_INSTRUCTIONS, (100, 200), (300, 100), 1000))

        static_level_components.append(ForeGround('forest_grass01', (100,-80), size=(0, 0)))
    elif level_number == 0:
        level_name = 'forest'
        ground_pos = 500
        static_level_components.append(Ground('forest_ground01', (0, ground_pos)))
        static_level_components.append(Ground('forest_ground02', (850, ground_pos)))
        dynamic_level_components.append(Text(MOVEMENT_INSTRUCTIONS, (100, 100), (300, 100), 10000))

        # dynamic_level_components
    elif level_number == 2: #forest
        level_size = (3840, 1080)
        level_name = 'forest'

        static_level_components.append(Ground('forest_ground01', (-20, 770), size=(800, 200)))

        static_level_components.append(Ground('forest_ground02', (950, 770), size=(600, 200)))

        static_level_components.append(Ground('forest_ground01', (1550, 770), size=(800, 200)))

        static_level_components.append(Ground('forest_ground02', (1550+800, 770), size=(600, 200)))

        dynamic_level_components.append(Text(MOVEMENT_INSTRUCTIONS, (100, 400), (300, 770), max_time=60))

    elif level_number == 1: #lab
        level_size = (1920, 1080)
        level_name = 'lab'
        ground_pos = 500
        static_level_components.append(Ground('forest_ground02', (-50, 800), size=(450, 350)))

        static_level_components.append(Ground('forest_ground02', (450, 800), size=(600, 350)))


        static_level_components.append(Ground('forest_ground02', (1060, 800), size=(500, 350)))



        static_level_components.append(Ground('forest_ground02', (1300, 800), size=(450, 350)))

        static_level_components.append(Background('lab_stuff01', (600, 470), size=(450, 350)))

        dynamic_level_components.append(Text(MOVEMENT_INSTRUCTIONS, (100, 400), (300, 100), max_time=60))


    else:
        raise NotImplementedError(f"Level value hasn't been implemented! {level_number}")

    background = Background(level_name, background_pos, level_size)
    player = Player(player_pos, size=player_size)  # player and it's starting position in the level_number
    return Level(level_name, player, static_level_components, dynamic_level_components, background=background,
                 level_size=level_size, camera_type=camera_type)
