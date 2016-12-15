#
# graphics handling

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 640

import os
from queue import Queue

import pygame


class Graphics:
    """resources, and Graphics handling"""
    # a list with all sub-resource dirs (the keys are in lower case)
    RESOURCE_DIRS = {resource.lower(): 'resources/' + resource for resource in os.listdir('resources')}

    def __init__(self):
        pygame.font.init()
        # init display
        self.display = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.HWSURFACE)
        pygame.display.set_caption("Mad Salts")
        # resources
        self.resources = {}  # holds the loaded graphical resources
        self.load_all_resources()  # file extensions are not part of the resource names
        # sidescrolling camera
        self.camera_pos = [0, 0]
        self.camera_center_rect = None
        self.dirty_rects = [] # an updated list of rectangles that have yet to be blitted on the screen

    # load graphics resources (sounds, and graphics)
    # doesn't do any conversion. loads as is!
    def load_all_resources(self):
        """Recusively goes through all the resources, and loads them into a list."""
        for resource_name in self.RESOURCE_DIRS:
            resource_dir = self.RESOURCE_DIRS[resource_name]

            resources = os.listdir(resource_dir)
            for resource in resources:
                self.resources[resource[:-4]] = pygame.image.load(resource_dir + '/' + resource)

    # update blitted rectangles
    def update(self):
        if self.rectangles:
            self.update_dirty_rects()


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
        print("[GA] rects blitted: {}".format(self.dirty_rects))  # debugging
        self.dirty_rects.clear()

    def blit(self, sprite, rect):
        self.display.blit(sprite, rect)
        self.dirty_rects.append(rect)

    # Graphical game_components test
    def blit_test(self, player):
        # self.display.blit(self.resources['background'], (0,0))
        return self.display.blit(player.sprite, player.rect)

class Camera(object):
    def __init__(self, camera_func, width, height):
        self.camera_func = camera_func
        self.state = pygame.Rect(0, 0, width, height)

    def apply(self, rect):
        return rect.move(self.state.topleft)

    def update(self, target_rect):
        self.state = self.camera_func(self.state, target_rect)

def simple_camera(camera, player):
    l, t, _, _ = player.rect
    _, _, w, h = camera

    return pygame.Rect(-l + WINDOW_WIDTH/2, -t + WINDOW_HEIGHT/2, w, h)

def complex_camera(camera, target_rect):
    l, t, _, _ = target_rect
    _, _, w, h = camera
    l, t, _, _ = -l + HALF_WIDTH, -t + HALF_HEIGHT, w, h

    l = min(0, l)  # stop scrolling at the left edge
    l = max(-(camera.width - SCREEN_WIDTH), l)  # stop scrolling at the right edge
    t = max(-(camera.height - SCREEN_HEIGHT), t)  # stop scrolling at the bottom
    t = min(0, t)  # stop scrolling at the top
    return pygame.Rect(l, t, w, h)

# only one graphics engine can be initialized at the same time,
graphics_handler = Graphics()