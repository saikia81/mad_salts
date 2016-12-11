import Game_components
import Levels
import Graphics

# game events
class GameEvent:
    def __init__(self, **data):
        self.event_name = self.TYPE
        self.data = data
        print("[EV] added: {}".format(self.TYPE))

    def handle(self):
        raise NotImplementedError("Please implement this method")

class LoadLevelEvent(GameEvent):
    """loads a level using Level.level_builder"""
    TYPE = 'LoadLevel'

    def handle(self):
        # create new level, and add it to the game state
        self.data['game_state'].level = Levels.level_builder(self.data['level'])
        print("[EV] handled: {}".format(self.TYPE))

class AttackEvent(GameEvent):
    TYPE = 'ATTACK'
    def handle(self):
        print('attack!')

event_types = {'LoadLevelEvent': LoadLevelEvent}

def create_game_event(type, data = None):
    return event_types[type](data)


#game_events = {name: GameEvent(name) for name, handler in {'attack':None, 'init_level': None}.values()}
