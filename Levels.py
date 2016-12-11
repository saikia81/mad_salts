from Game_components import *
from Graphics import WINDOW_WIDTH, WINDOW_HEIGHT

# make an Object file, and add all needed resources (based on folder position and file names)

class Level:
    """A class with level resources, and helper functions"""
    def __init__(self, level, background, player, world_components):
        # a dictionary with all level related game components
        self.static_game_components = {'background': background, 'player': player}
        self.dynamic_game_components = {'world_components': world_components, 'NPCs': []}
        self.level = level
        print("[+] level '{}' loaded".format(level))

    def __getattr__(self, name):
        try:
            return self.components[name]
        except ValueError:
            pass

        # Default
        return self.__getattribute__(name)

    def get_game_components(self):
        components = []
        components += list(self.static_game_components.values())
        components += self.get_dynamic_game_components()
        return components

    def get_dynamic_game_components(self):
        components = []
        for component_lst in self.dynamic_game_components.values():
            components += list(component_lst)
        return components

    # update all dynamic components in the current level
    def update(self):
        for component in self.get_dynamic_game_components():
            component.update()
            print("[Lv] updated")

    def display(self):
        for component in self.get_game_components():
            component.display()

    def __del__(self):
        pass


# needs to get the active game resources as argument, with which it will init the level graphics
# the player will also be created
def level_builder(level):
    #level specification
    if level == 0:
        player = Player((284, 666))
        background = Background(level)
        world_components = []  # additional dynamic blocks and other level components
    elif level == 1:
        pass
    else:
        raise ValueError("Level value hasn't been implemented!")

    return Level(level, background, player, world_components)