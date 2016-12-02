#!/bin/python3

# A serious 2.5D game in Python3 using Pygame.
#
# educational value may vary between:
# 1. The dangers, and basic properties of chemical combinations
# 2. salt learning
#
# learning mode: let's you play freely with the chemical components
# defender mode: is a castle defence game; the gameplay
# story mode: crazy scientist on the run against monsters with salts

import sys, os
import signal # SIGTERM handling
from time import sleep

from queue import LifoQueue as Queue  # linear time progression means LIFO
import pygame
from pygame.locals import *

from Entities import *

#SIGTERM (and any other signal, handling)
# should make the game end a little graceful
def signal_handler(signal, frame):
  print('Signal: {}'.format(signal))
  sleep(1)
  pygame.quit()
  sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)

# a class which holds the initialization, resource loading, and interaction between the game components
class Game:
    """Game component handling (incl. screen), and game loop"""
    FPS = 30
    SOUND_RESOURCE = r''
    GAME_EVENTS = {'attack': Player.attack}

    # Init Game state
    def __init__(self):
        assert(pygame.init(), (6, 0))  # assert all pygame modules are loaded
        self.game_event_queue = Queue()
        self.clock = pygame.time.Clock()
        self.graphics = Graphics()
        self.init_sound()  # load a song for music
        self.game_components = {}
        self.load_resource()

    def load_resource(self):
        self.make_player()

    # save, and unload
    def de_init(self):
        pygame.quit()

    # load a song, ready for playing
    def init_sound(self):
        self.music = None
        try:
            self.music = pygame.mixer.Sound(Game.SOUND_RESOURCE)
        except pygame.error:
            print("[!]Sound didn't load!")

    def make_player(self):
        self.game_components['player'] = Player(self.graphics.resources['player'], self.graphics.WINDOW_HEIGHT)

    # Event system
    def add_game_event(self, event_name):
        self.game_event_queue.put(event_name)

    def handle_game_event(self, event):
        self.GAME_EVENTS[event] # find an event's handler function, and execute

    def handle_pygame_event(self, event):
        player = self.game_components['player']
        if event == pygame.QUIT:
            self.de_init()
            sys.exit()
        # keypress handling
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.quit()
            # For now: key presses are handled directly from here.
            # todo: decide what keypresses does (maybe something with a physics engine)
            x, y = 0, 0
            if event.key == K_a:  # left
                player.pos[0] -= 10
            if event.key == K_d:  # right
                player.pos[0] += 10
            if event.key == K_w:  # up
                player.pos[1] -= 10
            if event.key == K_s:  # down
                player.pos[1] += 10
            print('player moved: {}'.format(player.pos))
        # mouse handling
        elif event.type == MOUSEBUTTONDOWN:
            self.add_game_event("attack")

    # load and start game
    def start_game(self):
        if self.music:
            self.music.play()
        self.running = True

        loop_counter = 0

        while self.running:
            # game mechanics
            # handle event amount proportional to the amount of events in queue
            if self.game_event_queue.qsize() < 10:
                while not self.game_event_queue.empty():
                    self.handle_game_event(self.game_event_queue.get())
            elif 20 < self.game_event_queue.qsize() >= 10:
                print("[!]queue is 10 items or more big")
                for _ in range(10):
                    self.handle_game_event(self.game_event_queue.get())
            else:
                print("[!]queue seems to get big, add queue handling code")
                while not self.game_event_queue.empty():
                    self.handle_game_event(self.game_event_queue.get())

            events = [event for event in pygame.event.get()]
            for event in events:
                self.handle_pygame_event(event)

            self.graphics.blit_test(self.game_components['player'])
            self.graphics.blit_all()

            self.last_update = self.clock.tick(Game.FPS)
            loop_counter += 1 # how many loops have been made

class Graphics:
    """Graphics handling code"""
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 640

    RESOURCE_LIST = \
        {'player': r'resources/slice01_01.png',
         'background': r'resources/klaaryass.png'}

    def __init__(self):
        self.dirty_rects = []  # an updated list of rectangles that have yet to be updated on the screen
        self.resources = {}
        self.display = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT), pygame.HWSURFACE)
        pygame.display.set_caption("Salt defender")
        self.load_resources()

    # load game resources (sounds, and graphics)
    def load_resources(self):
        for resource in self.RESOURCE_LIST:
            self.resources[resource] = pygame.image.load(self.RESOURCE_LIST[resource]).convert_alpha()
        self.background = pygame.transform.scale(self.resources['background'], (self.WINDOW_WIDTH, self.WINDOW_HEIGHT))


    def blit_all(self, blittables={}):
        #self.display.fill(pygame.Color('black')) #  fill screen with black
        self.display.blit(self.background, (0, 0))
        pygame.display.flip()

        # Graphical game handling
    def blit_test(self, player):
        # self.display.blit(self.resources['background'], (0,0))
        self.display.blit(player.sprite, player.pos)

def main():
    game = Game()
    game.start_game()

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt as ex:
        print("[!] keyboard interrupt signal received!")