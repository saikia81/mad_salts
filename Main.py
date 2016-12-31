#!/bin/python3

# A serious 2.5D game in Python3 using Pygame.
#
# Educational value may vary between:
# 1. The dangers, and basic properties of chemical combinations
# 2. salt memorising
#
# mode ideas
# learning mode: let's you play freely with the chemical components
# defender mode: is a castle defence game; the gameplay
# story mode: crazy scientist on the run against monsters with salts
#
# Game mechanics Ideas
# monster's attack each other when they are a different color (because elitism?)
# monster's chemical composition changes because of (a salt) reactions (and makes them susceptible to physical attacks)
# Monster's walk towards player, possibly replace with AI


import signal  # SIGTERM handling
import sys
import time
from queue import *  # linear time progression; FIFO

from pygame.locals import *

from Events import *
from Game_components import *
from Graphics import controller as graphics_controller
from Levels import Ground


def signal_handler(signal, frame):
    print('Signal: {}'.format(signal))
    time.sleep(1)
    pygame.quit()
    sys.exit(0)


signal.signal(signal.SIGTERM, signal_handler)  # todo: find out why SIGTERM doesn't work


class EventHandler(Queue):
    def get_event(self):  # don't use this, use Queue.get
        return self.event_queue.get()

    # adds
    def add(self, event):
        try:
            print("[G] event added: {}".format(event.TYPE))
            self.put_nowait(event)
        except Full:
            print("[!] warning, event queue is full, event disposed: {}".format(event.TYPE))

    def has_event(self):
        return not self.empty()


# Input (keys, mouse)
class InputHandler:
    """handles key presses and the pointer"""
    movement_keys = ['left', 'right', 'up', 'jump']
    action_keys = {'attack': AttackEvent}
    KEYS = []

    def __init__(self, event_handler):
        self.event_handler = event_handler
        self.active_keys = []
        self.player = None

    def set_player(self, player):
        if isinstance(player, Player):
            self.player = player

    # player input handling
    # generates a stop move event
    def move(self, movement):
        if self.player is not None:
            self.event_handler.add(MoveEvent(player=self.player, movement=movement))
        else:
            print("[IO] Event handled while no player selected, event discarded!")

    # generates a stop move event
    def stop_move(self, movement):
        if self.player is not None:
            self.event_handler.add(StopMoveEvent(player=self.player, movement=movement))
        else:
            print("[IO] Event handled while no player selected, event discarded!")

    # key group handling
    # Every key group has a relevant function
    def handle_key(self, id, key_event_type=None):
        if self.player is not None:
            if id in self.movement_keys:  # player movement
                self.move(id)
            elif id in self.action_keys:  # player actions
                self.event_handler.add(self.action_keys[id])
        else:
            print("[IO] Event handled while no player selected, event discarded!")

    def press(self, id):
        self.handle_key(id)

    def release(self, id):
        pass

    def handle_mouse(self, id):
        pass

    def handle_pygame_event(self, event):
        if event == pygame.QUIT:
            Game.de_init()
        # keypress handling
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                Game.de_init()
            # todo: decide what keypresses do (maybe something with a physics engine)
            if event.key == K_a:  # left
                self.move('left')
            if event.key == K_d:  # right
                self.move('right')
            if event.key == K_w:  # up
                self.move('up')
            if event.key == K_s:  # down
                self.move('down')
            if event.key == K_SPACE:  # down
                self.move('jump')
        # when a key is released, in some casescreate an event
        elif event.type == KEYUP:  # something to handle seperate key pressing and releasing
            if event.key == K_a:  # left
                self.stop_move('left')
            if event.key == K_d:  # right
                self.stop_move('right')
            if event.key == K_w:  # up
                self.stop_move('up')
            if event.key == K_s:  # down
                self.stop_move('down')
            if event.key == K_SPACE:  # down
                self.stop_move('jump')
        # mouse handling
        elif event.type == MOUSEBUTTONDOWN:
            self.event_handler.add(AttackEvent(attacker=self.player, pos=event.pos))


# a class which handels the initialization, resource loading, and interaction between the game components
class Game:
    """Game component handling (incl. screen), and game loop"""
    FPS = 30
    SOUND_RESOURCE = r''  # todo: replace with sound per image

    # Init Game state
    def __init__(self):
        assert (pygame.init(), (6, 0))  # assert all pygame modules are loaded
        self.running = False
        self.init_sound()  # load a song for music
        self.clock = pygame.time.Clock()  # for frame control; time
        self.graphics = graphics_controller  # graphics controller
        self.game_event_handler = EventHandler()  # Game event system
        self.input = InputHandler(self.game_event_handler)  # keyboard, and mouse input
        self.active_game_components = []  # can be used to hold all on-screen game components for optimization
        # self.load_game_components()
        self.level = None

    def load_resources(self):
        self.init_sound()
        # todo: make this an Event
        if self.show_fps:  # adds a fps meter to the Game state active_game_components list
            self.active_game_components.append(Meter(self.clock.get_fps, (30, 40)))

    # save, and unload game
    @staticmethod
    def de_init():
        pygame.quit()
        print("[Ga] de-init completed!")
        sys.exit()

    # load a song, ready for playing
    def init_sound(self):
        self.music = None
        try:
            self.music = pygame.mixer.Sound(Game.SOUND_RESOURCE)
        except pygame.error:
            print("[!]Sound didn't load!")

    def init_level(self):
        self.add_game_event(LoadLevelEvent(level=0, game_state=self))  # build, and load image

    # Event system
    def add_game_event(self, event):
        try:
            self.game_event_handler.add(event)
        except Full:
            print("[Ga] Event queue is full, event disposed: {}".format(event.TYPE))

    # handle event amount proportional to the amount of events in queue, alternatively thread it
    def handle_game_events(self):
        if self.game_event_handler.qsize() < 10:
            while not self.game_event_handler.empty():
                event = self.game_event_handler.get()
                event.handle()
        elif 20 < self.game_event_handler.qsize() >= 10:
            print("[!]queue is 10 items or more large")
            for _ in range(10):
                event = self.game_event_handler.get()
                event.handle()
        else:
            print("[!]queue seems to get big, add queue handling code")
            while not self.game_event_handler.empty():
                event = self.game_event_handler.get()
                event.handle()

    # start menu, currently sends you directly into the game
    def start_menu(self):
        self.start_game()

    # collision detection per entity that the function is called with
    @staticmethod
    def detect_collision(entity, components):
        for component in components:
            if pygame.sprite.collide_rect(entity, component):
                if component:
                    return  component
                    print("[CD] ground collision!")
                else:
                    print("[CD] unknown collision: {}".format(component))
        return component

    @staticmethod
    def detect_entity_collision(entity):
        pass

    # returns None, or the first found ground
    @staticmethod
    def find_type_collision(entity, components, component_type):
        for component in components:
            if pygame.sprite.collide_rect(entity, component) and type(component) == component_type:
                print("[CD] {} collision!".format(component_type))
                return component

    # getting the next colliding component
    @staticmethod
    def detect_type_collision(entity, components, component_type):
        for component in components:
            if pygame.sprite.collide_rect(entity, component) and type(component) == component_type:
                print("[CD] {} collision!".format(component_type))
                return component
        return None

    def detect_collisions(self):
        ground = self.detect_type_collision(self.level.player, self.level.static_components, Ground)
        if ground is not None:
            self.add_game_event(GroundCollisionEvent(entity=self.level.player, ground=ground))
        # for entity in self.image

    # load and start game
    def start_game(self):
        # starts music
        if self.music:
            self.music.play()

        # load the first level
        self.init_level()

        self.running = True
        loop_counter = 0
        dt = [0]*15
        while self.running:
            # Input mechanics
            for event in pygame.event.get():
                self.input.handle_pygame_event(event)
            self.handle_game_events()  # handles game component events

            # graphics processing
            if self.level is not None:
                self.level.display()
            # time betweem frames
            dt[loop_counter] = self.clock.tick(Game.FPS)  # returns the elapsed time in milliseconds
            # display after waiting for fps time passed
            pygame.display.update()

            # game mechanics
            # update game components with delta time
            self.level.update(dt[loop_counter])  # 1/100 seconds (centiseconds)
            # detect collisions
            self.detect_collisions()
            # update game copmonents that aren't part of the image
            for component in self.active_game_components:
                component.update(dt[loop_counter])

            loop_counter += 1  # how many loops have been made
            # FPS
            if loop_counter == len(dt):  # print and start over every 10 frames
                frames_per_time = sum(dt)/len(dt)
                time_per_frame = 10 / sum(dt)/len(dt)
                print("[G] TPF: {}\t FPS: {}".format(time_per_frame, frames_per_time))
                loop_counter = 0

def simulate_input(game):
    time.sleep(3)
    game.add_game_event(AddTextEvent(level=game.level, text="HELLO WORLD!", pos=(20, 20), size=(300, 150)))
    #game.add_game_event(create_game_event("Attack", attacker= game.image.player, pos=(20, 20)))

def rectangle_test():
    a = pygame.Rect((0, 0), (1280, 720))
    b = pygame.Rect((200, 400), (300, 460))
    print("clamp: " + str(b.clamp(a)))

    a = pygame.Rect((0, 0), (1280, 720))
    b = pygame.Rect((1200, 700), (300, 460))
    print("contains: " + str(a.contains(b)))  # has to be completely contained

    a = pygame.Rect((100, 100), (1200, 720))
    b = pygame.Rect((0, 0), (1280, 720))
    print("adding top-left: " + str(a.topleft+b.topleft))

    a = pygame.Rect((1, 1), (1280, 720))
    print("inflate: " + str(a.inflate(2, 2)))


def main():
    rectangle_test()
    exit()
    game = Game()
    #Thread(target=simulate_input, args=[game]).start()
    game.start_menu()

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt as ex:
        print("[!] keyboard interrupt signal received!")

