#!/bin/python3

# A serious 2.5D game in Python3 using Pygame.
#
# educational value may vary between:
# 1. The dangers, and basic properties of chemical combinations
# 2. salt memorising
#
#mode ideas
# learning mode: let's you play freely with the chemical components
# defender mode: is a castle defence game; the gameplay
# story mode: crazy scientist on the run against monsters with salts

import sys, os
import signal # SIGTERM handling
from time import sleep
from queue import *  # linear time progression; FIFO
import pygame
from pygame.locals import *

from Levels import level_builder
from Game_components import *
from Graphics import graphics_handler
from Events import *

#SIGTERM (and any other signal, handling)
# should make the game end a little graceful
def signal_handler(signal, frame):
    print('Signal: {}'.format(signal))
    sleep(1)
    pygame.quit()
    sys.exit(0)

# todo: find out why SIGTERM doesn't work
signal.signal(signal.SIGTERM, signal_handler)

#Game mechanics Ideas
# monster's attack eachother when they are a different color (because elitism?)
# monster's chemical composition changes because of (a salt) reactions (and makes them susceptible to physical attacks)
# Monster's walk towards player, possibly replace with AI

# maybe put IO here (key events, etc)
class IOController:
    pass

# a class which handels the initialization, resource loading, and interaction between the game components
class Game:
    """Game component handling (incl. screen), and game loop"""
    FPS = 30
    SOUND_RESOURCE = r''
    GAME_EVENTS = [LoadLevelEvent]  # todo redesign event system to incorperate arguments (speed, force, etc.)

    # Init Game state
    def __init__(self):
        assert(pygame.init(), (6, 0))  # assert all pygame modules are loaded
        self.game_event_queue = Queue()  # Game event system
        self.clock = pygame.time.Clock()  #  ticks per second
        self.graphics = graphics_handler # graphics controller
        self.io_controller = IOController()
        self.init_sound()  # load a song for music
        self.active_game_components = []
        #self.load_game_components()
        self.level = None

    def load_resources(self):
        self.init_sound()
        if self.show_fps:
            self.active_game_components.append(Meter(self.clock.get_fps, (30, 40)))

    # save, and unload game
    def de_init(self):
        pygame.quit()
        self.running = False
        sys.exit()

    # load a song, ready for playing
    def init_sound(self):
        self.music = None
        try:
            self.music = pygame.mixer.Sound(Game.SOUND_RESOURCE)
        except pygame.error:
            print("[!]Sound didn't load!")

    def init_level(self, level_number):
        level_builder(level_number, self.graphics.resources)

    # Event system
    def add_game_event(self, event):
        try:
            print("[G] event added: {}".format(event))
            self.game_event_queue.put_nowait(event)
        except Full:
            print("[!] warning, event queue is full, event disposed: {}".format(event.TYPE))

    # todo: handle event amount proportional to the amount of events in queue, alternatively thread it
    def handle_game_events(self):
        if self.game_event_queue.qsize() < 10:
            while not self.game_event_queue.empty():
                event = self.game_event_queue.get()
                event.handle()
        elif 20 < self.game_event_queue.qsize() >= 10:
            print("[!]queue is 10 items or more big")
            for _ in range(10):
                event = self.game_event_queue.get()
                event.handle()
        else:
            print("[!]queue seems to get big, add queue handling code")
            while not self.game_event_queue.empty():
                event = self.game_event_queue.get()
                event.handle()

    def handle_pygame_event(self, event):
        if self.level is not None:
            player = self.level.static_game_components['player']
        else:
            return
        if event == pygame.QUIT:
            self.de_init()
        # keypress handling
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                self.de_init()
            # For now: key presses are handled directly from here.
            # todo: decide what keypresses do (maybe something with a physics engine)
            if event.key == K_a:  # left
                player.rect.move(-10, 0)
            if event.key == K_d:  # right
                player.rect.move(10, 0)
            if event.key == K_w:  # up
                player.rect.move(0, 10)
            if event.key == K_s:  # down
                player.rect.move(0, -10)
            print('player moved: {}'.format(player.rect))
        elif event.type == KEYUP:  # something to handle seperate key pressing and releasing
            # if event.key == K_a:  # left
            #     player.move()
            # if event.key == K_d:  # right
            #     player.move()
            # if event.key == K_w:  # up
            #     player.move()
            # if event.key == K_s:  # down
            #     player.move()
            pass
        # mouse handling
        elif event.type == MOUSEBUTTONDOWN:
            self.add_game_event(AttackEvent())

    # start menu, currently sends you directly into the game
    def start_menu(self):
        self.start_game()

    # load and start game
    def start_game(self):
        # starts music
        if self.music:
            self.music.play()

        self.running = True
        loop_counter = 0
        self.add_game_event(LoadLevelEvent(level=0, game_state=self))
        while self.running:
            # game mechanics
            events = [event for event in pygame.event.get()]
            for event in events:
                self.handle_pygame_event(event)
            self.handle_game_events()  # handles game component events

            # graphics processing
            #self.graphics.blit_test()
            self.level.display()
            self.graphics.update_dirty_rects()

            # game state
            # update
            if self.level is not None:
                self.level.update()

            for component in self.active_game_components:
                component.update()

            self.last_update = self.clock.tick(Game.FPS)
            loop_counter += 1 # how many loops have been made

def main():
    game = Game()
    game.start_menu()

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt as ex:
        print("[!] keyboard interrupt signal received!")