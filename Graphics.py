#
# graphics handling

import os
from queue import Queue

import pygame


class Graphics:
    """Graphical resources, Graphics handling, and display controller"""
    # a list with all sub-resource dirs (the keys are in lower case)
    RESOURCE_DIRS = {resource.lower(): 'resources/' + resource for resource in os.listdir('resources')}

    CAMERA_WIDTH = 1280
    CAMERA_HEIGHT = 720

    def __init__(self):
        # init display
        self.display = pygame.display.set_mode((self.CAMERA_WIDTH, self.CAMERA_HEIGHT), pygame.HWSURFACE)
        # sidescrolling camera
        self.camera = None
        pygame.display.set_caption("Mad Salts")
        # resources
        self.resources = {}  # holds the loaded graphical resources grouped (by directory)
        self.load_resources()  # loads all resources; file extensions are not part of the name
        self.dirty_rects = []  # an updated list of rectangles that have yet to be updated on the screen

    def set_camera(self, camera):
        print("[SC] camera set: {}".format(camera))
        self.camera = camera

    def unset_camera(self):
        self.camera = None

    def blit_to_camera(self, sprite, rect, camera):
        if type(camera) is Camera:
            print(str(rect) + ", " + str(sprite)+ ", " + str(camera))
            #if pygame.Rect.colliderect(rect, camera.rect):
                # rect = rect.move(camera.rect.topleft)
            self.blit(sprite, pygame.Rect.clamp(camera.rect, rect))
        else:
            TypeError("'camera' has to be of the type 'Camera'")

    def update_camera(self):
        self.display.update()

    # load graphics resources (sounds, and graphics)
    # doesn't do any conversion. loads as is!
    def load_resources(self):
        """Goes through all the resource dirs, and loads the resources into a dict"""
        for resource_type in self.RESOURCE_DIRS:
            resource_dir = self.RESOURCE_DIRS[resource_type]
            resources = os.listdir(resource_dir)
            for resource in resources:
                self.resources[resource[:-4]] = pygame.image.load(resource_dir + '/' + resource)

    # update blitted (aka 'dirty') rectangles on every frame
    def update(self):
        if self.dirty_rects:
            self.update_dirty_rects()

    # takes a string, returns a blittable text label
    # word wrapping should be done manually by making multiple labels
    def make_text(self, text, color):
        if type(text) != str:
            raise TypeError("Text must be a string!")
        return self.font.render(text, 1, color)

    # accepts a set of blittable objects
    # order matters! first with the background, and last is the foreground
    def display_all(self):
        # self.display.fill(pygame.Color('black')) #  fill screen with black
        try:
            if self.dirty_rects.not_empty:
                self.display.update([rect for rect in self.dirty_rects.empty()])
        except Queue.Empty:
            pass
        pygame.display.flip()

    # all rectangles that have changed on the display get updated
    def update_dirty_rects(self):
        """Updates every rectangle in game for rectangle in dirty rectangles"""
        pygame.display.update(self.dirty_rects)  # update is faster when all rectangles are passed at once
        print("[GA] rects blitted: {}".format(self.dirty_rects))  # debugging
        self.dirty_rects.clear()

    # blits image to the display surface, and adds the rectangle to a list
    def blit(self, sprite, rect):
        self.display.blit(sprite, rect)
        self.dirty_rects.append(rect)
        # print("[GE] blitted: {}, rect: {}".format(sprite, rect))

    # Graphical components test
    def blit_test(self, player):
        # self.display.blit(self.resources['background'], (0,0))
        return self.display.blit(player.sprite, player.rect)

# a camera surface that can be blitted on to the display
class Camera():
    def __init__(self, camera_func, target_rect, level_limit):
        self.camera_func = camera_func
        self.rect = pygame.Rect((0, 0), (Graphics.CAMERA_WIDTH, Graphics.CAMERA_HEIGHT))
        self.extreme_point = level_limit
        print('[CA] ' + repr(self.rect))

    def __repr__(self):
        x, y, w, h = self.rect
        return "Camera; pos: " + str((x, y)) + ", size:  " + str((w, h))

    def apply(self, rect):
        return rect.move(self.state.topleft)

    def update(self, target_rect):
        self.camera_func(self, target_rect)
        print("[CA] update: {}".format(self.rect))


def simple_camera(camera, target_rect):
    _, _, w, h = camera.rect
    x, y, _, _ = target_rect
    camera.rect = pygame.Rect(x, y, w, h)


def complex_camera(camera, target_rect):
    l, t, _, _ = target_rect
    _, _, w, h = camera.rect
    l, t, _, _ = -l + camera.extreme_point[0], -t + camera.extreme_point[1], w, h

    l = min(0, l)  # stop scrolling at the left edge
    l = max(-(camera.rect.width - camera.extreme_point[0]), l)  # stop scrolling at the right edge
    t = max(-(camera.rect.height - camera.extreme_point[1]), t)  # stop scrolling at the bottom
    t = min(0, t)  # stop scrolling at the top
    camera.rect = pygame.Rect(l, t, w, h)


# only one graphics engine can be initialized at the same time, for now
# the controller has to be imported into the namespace of the program (from Graphics import controller)
controller = Graphics()
