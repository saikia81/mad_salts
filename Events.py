from Game_components import Text
from Levels import level_builder


class GameEvent:
    def __init__(self, **data):
        self.event_name = self.TYPE
        self.data = data

    def __getattr__(self, name):
        try:
            return self.data[name]
        except:
            pass

    def __del__(self):
        print("[EV] handled: {} with data: {}".format(self.TYPE, self.data))

    def handle(self):
        raise NotImplementedError("Please implement this method")


class LoadLevelEvent(GameEvent):
    """loads a image using Level.level_builder"""
    TYPE = 'LoadLevel'

    def handle(self):
        # create new image, and add it to the game state
        self.game_state.level = level_builder(self.level)  # new image
        self.game_state.input.set_player(self.game_state.level.player)  # adds initialized player to input handler


class AttackEvent(GameEvent):
    TYPE = 'ATTACK'

    def handle(self):
        self.attacker.attack(self.pos)


class AddTextEvent(GameEvent):
    TYPE = 'ADDTEXT'

    def handle(self):
        test = Text(self.text, self.pos, self.size)
        print("test: " + repr(test))
        self.level.add_world_component(test)


# movement events are a bad design idea, but right now necessary
class MoveEvent(GameEvent):
    TYPE = 'MOVE'

    def handle(self):
        self.player.move(self.movement)


# probably not needed
class StopMoveEvent(GameEvent):
    TYPE = 'StopMove'

    def handle(self):
        self.player.stop_move(self.movement)


class GroundCollisionEvent(GameEvent):
    TYPE = 'GroundCollission'

    def handle(self):
        self.entity.set_ground(self.ground)


EVENTS = [LoadLevelEvent, AttackEvent, AddTextEvent, MoveEvent, StopMoveEvent, GroundCollisionEvent]


def create_game_event(_type, **data):
    return EVENTS[_type](data)

# game_events = {name: GameEvent(name) for name, handler in {'attack':None, 'init_level': None}.values()}
