from Game_components import *

from Graphics import Camera, simple_camera


# make an Object file, and add all needed resources (based on folder position and file names)

class Level:
    """A class with level resources, and helper functions"""

    def __init__(self, level_name, player, static_world_components, dynamic_world_components):
        self.level_name = level_name
        # a dictionary with all level related game components
        self.player = player
        self.static_components = static_world_components
        self.dynamic_components = dynamic_world_components
        self.dynamic_components.append(player)
        self.components = [] + self.static_components + self.dynamic_components  # redundant list; fast requesting level component
        self.camera = Camera(simple_camera, 480, 320)  # the screen view
        print("[+] level '{}' loaded".format(level_name))

    def __getattr__(self, name):
        try:
            return self.components[name]
        except ValueError:  # requested name isn't a game component, do default behaviour
            pass
        return self.__getattribute__(name)

    # find player ground
    def find_player_ground(self):
        pass #x = self.player.rect.x

    # game component management
    def add_NPC(self, npc):
        self.add_game_component('NPC', npc)

    def add_world_component(self, world_component):
        self.add_game_component('world_component', world_component)

    # when adding a component to a level, this methid should be used exclusively
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
        """update all dynamic game components in the current level"""
        for component in self.dynamic_components:
            component.update(dt)
        print("[LL] updated all components")

    def display(self):
        """calls display on every component; blitting them, and adding their rectangle to a dirty rectangles list"""
        for component in self.components:
            component.display()

    def __del__(self):
        print("[LL] level '{}' unloaded".format(self.level_name))


# level component handling
class StaticLevelComponent(GraphicsComponent):
    """Base class for all static Level Components"""

    def __init__(self, resource_name, pos, size=None):
        if size is not None and len(size) != 2:
            raise ValueError("Size has to be a tuple of length 2!")
        self.TYPE = resource_name  # A correct name is needed for initialization
        super(StaticLevelComponent, self).__init__(pos, size)

    def init_sprite(self):
        self.sprite = pygame.transform.smoothscale(self.sprite, self.size)


class Background(StaticLevelComponent):
    """Background"""
    TYPE = 'Background'

class ForeGround(StaticLevelComponent):
    """ForeGround"""
    TYPE = 'Foreground'

class Ground(StaticLevelComponent):
    """ground"""
    TYPE = 'ground'

    def __init__(self, resource_name, pos, size=None):
        super(Ground, self).__init__(resource_name, pos, size=None)


# level builder; calls level init
# component order matters!
def level_builder(level):
    world_component_types = ['Background', 'Foreground', 'Ground']
    # any component that is part of the world should be added to world_components list
    static_level_components = []  # additional dynamic blocks and other level components
    dynamic_level_components = []

    if level == 0:
        level_name = 'forrest'
        player = Player((200, 500))  # player and it's starting position in the level

        static_level_components.append(Background('background0', (0, 0), (WINDOW_WIDTH, WINDOW_HEIGHT)))
        static_level_components.append(Ground('forest_ground', (0, 0)))

        # dynamic_level_components += None
    elif level == 1:
        raise NotImplementedError("Level value hasn't been implemented!")
        level_name = ''
        player = Player((0, 0))

        # static_level_components
        # dynamic_level_components
    else:
        raise NotImplementedError("Level value hasn't been implemented!")

    return Level(level_name, player, static_level_components, dynamic_level_components)
