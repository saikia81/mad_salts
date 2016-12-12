from Game_components import *


# make an Object file, and add all needed resources (based on folder position and file names)

class Level:
    """A class with level resources, and helper functions"""
    def __init__(self, level, background, player, world_components):
        # a dictionary with all level related game components
        self.static_game_components = {'background': background, 'player': player}
        self.dynamic_game_components = {'world_component': world_components, 'NPC': []}
        self.level = level
        print("[+] level '{}' loaded".format(level))

    def __getattr__(self, name):
        try:
            return self.components[name]
        except ValueError:
            pass

        # Default
        return self.__getattribute__(name)

    def add_NPC(self, npc):
        self.add_game_component('NPC', npc)

    def add_world_component(self, world_component):
        self.add_game_component('world_component', world_component)

    def add_game_component(self, component_type, component):
        self.dynamic_game_components[component_type].append(component)

    def del_game_component(self):
        pass

    def get_dynamic_game_components(self):
        components = []
        for component_lst in self.dynamic_game_components.values():
            components += list(component_lst)
        return components

    def get_game_components(self):
        components = self.get_dynamic_game_components()
        components += list(self.static_game_components.values())
        return components

    def update(self):
        for component in self.get_dynamic_game_components():
            component.update()
            print("[Lv] updated")
    # update all dynamic components in the current level

    def display(self):
        for component in self.get_game_components():
            component.display()

    def __del__(self):
        pass


# needs to get the active game resources as argument, with which it will init the level graphics
# the player will also be created
def level_builder(level):
    #level specification
    background = Background(level)  # level is needed to find the matching background
    world_components = []  # additional dynamic blocks and other level components

    if level == 0:
        player = Player((200, 500)) #player and it's posision
        #world_components.append(None)  # any component that is part of the world should be added to world_components list
    elif level == 1:
        player = Player((0, 0))
        #world_components.append(None)  # any component that is part of the world should be added to world_components list
    elif level == 2:
        pass
    else:
        raise ValueError("Level value hasn't been implemented!")

    return Level(level, background, player, world_components)