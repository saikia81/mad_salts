from Game_components import *
from Graphics import controller as graphics_handler, Camera

CAMERA_WIDTH = graphics_handler.CAMERA_WIDTH
CAMERA_HEIGHT = graphics_handler.CAMERA_HEIGHT

# make an Object file, and add all needed resources (based on folder position and file names)

class Level():
    """A class with image resources, and helper functions"""

    def __init__(self, level_name, player, static_world_components, dynamic_world_components, background=None,
                 level_size=None, camera_type=None):
        if level_size == None:
            level_size = background.size
        self.level_size = level_size
        self.level_name = level_name
        # a dictionary with all image related game components
        self.player = player
        self.playing_entities = []  # starts empty; is filled by monsters, and other NPC
        self.npcs = pygame.sprite.Group()
        self.static_components = static_world_components  # image parts (e.g. background, ground)
        self.dynamic_components = dynamic_world_components  # image parts (e.g. swings, moving objects, bullets)
        self.components = [] + self.static_components + self.dynamic_components  # redundant list; fast requesting component
        # build the static game world
        self.image, self.rect = self.build_background(level_size, background=background,
                                                      static_components=self.static_components)
        if camera_type is not None:
            self.camera = Camera(camera_type, player.rect, level_size)  # the screen view
            # todo: decide on who should hold the camera
            graphics_handler.set_camera(self.camera)  # makes it possible to blit directly to the graphics handler
        else:
            self.camera = None

        print("[LV] image '{}' loaded".format(level_name))

    @staticmethod
    def build_background(level_size, background=None, static_components=None, colour=(255, 150, 0)):
        if static_components is None:
            static_components = []


        level = pygame.Surface(level_size)
        level.fill(colour)
        level_rect = level.get_rect()
        if background is not None:
            level.blit(background.image, background.rect)
            print('[LV] Background blitted in build: {}'.format(background.rect))

        for placement in [Background, Ground]:  # first blit Background, afterwards Ground
            for component in static_components:
                # if not self.level_rect.contains(component.rect): continue  # only if component fits in level
                if type(component) == placement:
                    level.blit(component.image.convert_alpha(), component.rect)

        print("image surface created: {}".format(level))
        return level, level_rect

    def __getattr__(self, name):
        try:
            return self.components[name]
        except ValueError: pass  # requested name isn't a game component, do default behaviour
        except TypeError: pass
        return self.__getattribute__(name)

    # find player ground
    def find_player_ground(self):
        pass #x = self.player.rect.x

    # game component management
    def add_NPC(self, npc):
        self.add_game_component('NPC', npc)

    def add_world_component(self, world_component):
        self.static_components.append(world_component)
        print(world_component.image)
        self.image.blit(None, world_component.rect)

    # when adding a component to a image, this method should be used exclusively
    def add_game_component(self, component):
        self.components.append(component)

    def del_game_component(self, component_type, component):
        del self.dynamic_components[component_type][component]  # component should have __eq__ overridden
        del self.components[component]

    def get_dynamic_components(self):
        """builds a (flat) list with all dynamic game component"""
        return [x for x in self.dynamic_components]

    def get_game_components(self):
        """Builds a new list with all static and dynamic components"""
        # first get the static components, as these will be blitted over by the dynamic ones
        return [x for x in self.components]

    def update(self, dt):
        """update all image components in the current image"""
        self.player.update(dt)  # the player gets the first move
        for component in self.dynamic_components:
            component.update(dt)
        # update camera as last
        if self.camera:
            self.camera.update(self.player.rect)

    # displays all image components from back- to foreground
    def display(self):
        """calls display on every component; blitting them, and adding their rectangle to a dirty rectangles list"""
        # first put the background on the display
        if self.camera is not None:
            graphics_controller.blit(self.image, self.rect, self.camera.rect)
        else:
            graphics_controller.blit(self.image, self.rect)
        #for component in self.static_components:
        #    component.display(self.camera)
        self.player.display(self.camera)
        for dynamic_component in self.dynamic_components:
            dynamic_component.display(self.camera)

    def __del__(self):
        graphics_handler.unset_camera()
        print("[LL] image '{}' unloaded".format(self.level_name))


# image parts handling
class StaticLevelComponent(GraphicsComponent):
    """Base class for all image building blocks"""

    def __init__(self, resource_name, pos, size=None):
        # if the size is None; it will be determined by the image resolution
        if size is not None and len(size) != 2:
            raise ValueError("Size has to be a tuple of length 2!")
        self.TYPE = resource_name  # A correct name is needed for (image) init
        super(StaticLevelComponent, self).__init__(pos, size)

    def init_image(self):
        self.image = pygame.transform.smoothscale(self.image, self.size)


class Background(StaticLevelComponent):
    """Background"""
    TYPE = 'Background'
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
        super(Ground, self).__init__(resource_name, pos, size=None)


# image builder; calls image init
# component order matters!
def level_builder(level_number):
    world_component_types = ['Background', 'Foreground', 'Ground']
    # any component that is part of the world should be added to world_components list
    static_level_components = []  # additional dynamic blocks and other level_number components
    dynamic_level_components = []
    level_size = None

    if level_number == -1:  # testing
        level_name = 'test'
        background = Background('background0', (0, 0))
        player = Player((50, 50))  # player and it's starting position in the level_number
        ground_pos = 500
        static_level_components.append(Ground('forest_ground_p0', (0, ground_pos)))
        static_level_components.append(Ground('forest_ground_p1', (700, ground_pos)))
    elif level_number == 0:
        level_name = 'forest'
        level_size = (CAMERA_WIDTH*2, CAMERA_HEIGHT*2)
        player = Player((50, 50))  # player and it's starting position in the level_number
        background = Background('background0', (0, 0), level_size)
        ground_pos = 500
        static_level_components.append(Ground('forest_ground_p0', (0, ground_pos)))
        static_level_components.append(Ground('forest_ground_p1', (700, ground_pos)))

        # dynamic_level_components
    elif level_number == 1:
        raise NotImplementedError("Level value hasn't been implemented!")
        level_name = ''
        player = Player((0, 0))

        # static_level_components
        # dynamic_level_components
    else:
        raise NotImplementedError("Level value hasn't been implemented!")

    return Level(level_name, player, static_level_components, dynamic_level_components, background=background,
                 level_size=level_size, camera_type=None)
