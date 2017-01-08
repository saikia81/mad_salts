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

import sys

from events import *
from game_components import *
from settings import *

# Input (keys, mouse)
class InputHandler:
    """handles key presses and the pointer"""
    movement_keys = ['left', 'right', 'up', 'jump']
    action_keys = {'attack': AttackEvent}
    KEYS = []

    def __init__(self):
        self.active_keys = []
        self.player = None

    def set_player(self, player):
        if type(player) == Player:
            self.player = player

    # player input handling
    # generates a stop move event
    def move(self, movement):
        if self.player is not None:
            event_handler.add(MoveEvent(player=self.player, movement=movement))
        else:
            if DEBUG:
                print("[IO] Event handled while no player selected, event discarded!")

    # generates a stop move event
    def stop_move(self, movement):
        if self.player is not None:
            event_handler.add(StopMoveEvent(player=self.player, movement=movement))
        else:
            if DEBUG:
                print("[IO] Event handled while no player selected, event discarded!")

    # key group handling
    # Every key group has a relevant function
    def handle_key(self, id, key_event_type=None):
        if self.player is not None:
            if id in self.movement_keys:  # player movement
                self.move(id)
            elif id in self.action_keys:  # player actions
                event_handler.add(self.action_keys[id])
        else:
            if DEBUG:
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
            elif event.key == K_d:  # right
                self.move('right')
            elif event.key == K_w:  # up
                self.move('up')
            elif event.key == K_s:  # down
                self.move('down')
            elif event.key == K_SPACE:  # down
                self.move('jump')
            elif event.key == K_t: # activate test
                test()
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
            event_handler.add(AttackEvent(attacker=self.player, pos=event.pos))


# a class which handels the initialization, resource loading, and interaction between the game components
class Game:
    """Game component handling (incl. screen), and game loop"""
    FPS = 30
    SOUND_RESOURCE = r''  # todo: replace with sound per image

    # Init Game state
    def __init__(self):
        assert (pygame.init(), (6, 0))  # assert all Pygame modules are loaded
        self.running = False
        self.init_sound()  # load a song for music
        self.clock = pygame.time.Clock()  # for frame control; time
        self.graphics = graphics_controller  # graphics controller
        # event_handler.start()
        self.input = InputHandler()  # keyboard, and mouse input
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
            if WARNING:
                print("[!]Sound didn't load!")

    def init_level(self):
        self.add_game_event(LoadLevelEvent(level=0, game_state=self))  # build, and load image
        sleep(1)

    # Event system
    def add_game_event(self, event):
        try:
            event_handler.add(event)
        except Full:
            if WARNING:
                print("[Ga] Event queue is full, event disposed: {}".format(event.TYPE))

    # handle event amount proportional to the amount of events in queue, alternatively thread it
    def handle_game_events(self):
        if event_handler.qsize() < 10:
            while not event_handler.empty():
                event = event_handler.get()
                event.handle()
        elif 20 < event_handler.qsize() >= 10:
            if WARNING:
                print("[!]queue is 10 items or more large")
            for _ in range(10):
                event = event_handler.get()
                event.handle()
        else:
            if WARNING:
                print("[!]queue seems to get big, add queue handling code")
            while not event_handler.empty():
                event = event_handler.get()
                event.handle()

    # start menu, currently sends you directly into the game
    def start_menu(self):
        self.graphics.init_screen()
        self.start_game()

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
            event_handler.handle_events()  # calls '.handle()' on (almost) every game event in queue

            # graphics processing
            if self.level is not None:
                self.level.display()

            # display after waiting for fps time passed
            pygame.display.update()

            # time betweem frames
            dt[loop_counter] = self.clock.tick(Game.FPS)  # returns the elapsed time in milliseconds

            # game mechanics
            # update game components with delta time
            # todo: make the physics simulation take into account the time till the frame is displayed
            self.level.detect_collisions()
            self.level.update(dt[loop_counter])  # 1/100 seconds (centiseconds)
            # detect collisions
            # update game components that aren't part of the image
            for component in self.active_game_components:
                component.update(dt[loop_counter])

            loop_counter += 1  # how many loops have been made
            # FPS
            if loop_counter == len(dt):  # print and start over every 15 frames
                frames_per_time = sum(dt)/len(dt)
                time_per_frame = 10 / sum(dt)/len(dt)
                if DEBUG:
                    print("[G] TPF: {}\t FPS: {}".format(time_per_frame, frames_per_time))
                loop_counter = 0

    def test(self):
        """function for testing pygame things"""
        for component in self.level.components:
            if type(component) == Text:
                self.add_game_event(DelGameComponentEvent(level=self.level, component=component))
                break

def display_level(level_n):
    input_handler = InputHandler(event_handler)

    graphics_controller.init_screen((1399, 905))

    class Temp:
        pass
    t = Temp()
    t.input = input_handler
    event_handler.add(LoadLevelEvent(level=level_n, game_state=t))
    event_handler.get().handle()
    level = t.level
    print('background size: {}'.format(level.rect.bottomleft))

    running = True
    dt = 0
    while running:
        # Input mechanics
        for event in pygame.event.get():
            input_handler.handle_pygame_event(event)

        while not event_handler.empty():
            event = event_handler.get()
            event.handle()

        # graphics processing
        if level is not None:
            level.display()
        # time betweem frames
        # display after waiting for fps time passed
        pygame.display.flip()

