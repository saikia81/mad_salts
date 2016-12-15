import Graphics
import Levels


# event names are lower case snake case, just like python variables
# event types are the class name without 'Event'
# An event implements the 'handle' method, which can change the 'level' state or a game_component's state
# for now it shouldn't do anything directly with the graphics controller
#
# You can delete a active game object by deleting it from the level state (

# game events
class GameEvent:
    def __init__(self, **data):
        self.event_name = self.TYPE
        self.data = data
        print("[EV] added: {}".format(self.TYPE))

    def __del__(self):
        print("[EV] handled: {}".format(self.TYPE))

    def handle(self):
        raise NotImplementedError("Please implement this method")

class LoadLevelEvent(GameEvent):
    """loads a level using Level.level_builder"""
    TYPE = 'LoadLevel'
    def handle(self):
        # create new level, and add it to the game state
        self.data['game_state'].level = Levels.level_builder(self.data['level'] ,self.data['game_state'])

class AttackEvent(GameEvent):
    TYPE = 'ATTACK'
    def handle(self):
        pass # create vial with appropriate speed, and position

class AddTextEvent(GameEvent):
    TYPE = 'AddText'
    def handle(self):
        Graphics.graphics_handler.make_text(self.data['text'])

# movement events are a bad design idea, but right now necessary
class MoveEvent(GameEvent):
    TYPE = 'MOVE'
    def handle(self):
        self.data['player'].move(self.data['movement'])

# probably not needed
class StopMoveEvent(GameEvent):
    TYPE = 'StopMove'
    def handle(self):
        self.data['player'].stop_move(self.data['movement'])


event_types = {'LoadLevelEvent': LoadLevelEvent, 'AttackEvent': AttackEvent}

def create_game_event(type, data = None):
    return event_types[type](data)


#game_events = {name: GameEvent(name) for name, handler in {'attack':None, 'init_level': None}.values()}
