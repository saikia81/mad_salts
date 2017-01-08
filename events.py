from threading import Thread

from game_components import Text
from levels import level_builder
from settings import *

class GameEvent(Thread):
    def __init__(self, **data):
        super(GameEvent, self).__init__()
        self.event_name = self.TYPE
        self.data = data

    def __getattr__(self, name):
        try:
            return self.data[name]
        except:
            pass

    def __del__(self):
        if INFO:
            print("[EV] handled: {} with data: {}".format(self.TYPE, self.data))

    def handle(self):
        raise NotImplementedError("Please implement this method")

    def run(self):
        return self.handle()

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
        c = []
        for x in self.level.components:
            if type(x) == Text:
                c.append(x.text)
        if self.text in c:
            if DEBUG:
                print('text already present')
            return
        text = Text(self.text, self.pos, self.size)
        self.level.add_component(text)


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

class DelGameComponentEvent(GameEvent):
    TYPE = 'DelGameComponent'

    def handle(self):
        try:
            del self.level.components[self.level.components.index(self.component)]
        except ValueError as ex:
            if WARNING:
                print(f"[EV] component couldn't be deleted: {self.component}")
        del self.level.dynamic_components[self.level.dynamic_components.index(self.component)]



EVENTS = [LoadLevelEvent, AttackEvent, AddTextEvent, MoveEvent, StopMoveEvent, GroundCollisionEvent,
          DelGameComponentEvent]


def create_game_event(_type, **data):
    return EVENTS[_type](data)

# game_events = {name: GameEvent(name) for name, handler in {'attack':None, 'init_level': None}.values()}


