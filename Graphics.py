#
# graphics handlin

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 640

import os, sys
from queue import Queue

import pygame
from pygame.locals import *

class Graphics:
    """Graphics handling code"""
    # a list with all sub-resource dirs (the keys are in lower case)
    RESOURCE_DIRS = {resource.lower(): 'resources/' + resource for resource in os.listdir('resources')}

    def __init__(self):
        pygame.font.init()
        # init display
        self.display = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.HWSURFACE)
        pygame.display.set_caption("Mad Salts")
        # resources
        self.resources = {}  # holds the loaded graphical resources
        self.load_resources()  # file extensions are not part of the resource names
        # sidescrolling camera
        self.camera_pos = [0, 0]
        self.camera_center_rect = None
        self.dirty_rects = [] # an updated list of rectangles that have yet to be blitted on the screen

    # load game resources (sounds, and graphics)
    def load_resources(self):
        for resource_name in self.RESOURCE_DIRS:
            resource_dir = self.RESOURCE_DIRS[resource_name]

            resources = os.listdir(resource_dir)
            for resource in resources:
                self.resources[resource[:-4]] = pygame.image.load(resource_dir + '/' + resource)

    # update blitted rectangles
    def update(self):
        if self.rectangles:
            self.update_dirty_rects()
        else:
            pass

    # takes a string, returns a blittable text label
    # word wrapping should be done mannually by making multiple labels
    def make_text(self, text, position, color):
        if type(text) != str:
            raise TypeError("Text must be a string!")
        return self.font.render(text, 1, color)

    # accepts a set of blittable objects
    # order matters! first with the background, and last is the foreground
    def display_all(self):
        #self.display.fill(pygame.Color('black')) #  fill screen with black
        try:
            if self.dirty_rects.not_empty:
                self.display.update([rect for rect in self.dirty_rects.empty()])
        except Queue.Empty:
            pass
        pygame.display.flip()

    # all rectangles that have changed on the display get blitted
    def update_dirty_rects(self):
        # gets all dirty rects out of the Queue, and blits them
        pygame.display.update([rect for rect in self.dirty_rects])
        self.dirty_rects.clear()

    def blit(self, sprite, rect):
        self.display.blit(sprite, rect)
        self.dirty_rects.append(rect)

    # Graphical game_components test
    def blit_test(self, player):
        # self.display.blit(self.resources['background'], (0,0))
        return self.display.blit(player.sprite, player.rect)

# only one graphics engine can be initialized at the same time,
graphics_handler = Graphics()