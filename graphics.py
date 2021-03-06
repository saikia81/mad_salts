# graphics handling

import os  # resource management

import pygame
from configurations import *

class Graphics:
    """Graphical resources, Graphics handling, and display control"""
    # a list with all sub-resource dirs (the keys are in lower case)
    RESOURCE_DIRS = {resource.lower(): 'resources/' + resource for resource in os.listdir('resources')}

    def __init__(self):

        # init modules
        pygame.font.init()
        # init display
        self.screen = None
        # sidescrolling camera
        self.camera = None

        # resources
        self.resources = {}  # holds the loaded graphical resources grouped (by directory)
        self.load_resources()  # loads all resources; file extensions are not part of the name

        self.dirty_rects = []  # an updated list of rectangles that have yet to be updated on the screen

    def init_screen(self,window_resolution=None):
        if window_resolution is not None:
            self.CAMERA_WIDTH, self.CAMERA_HEIGHT = window_resolution
        self.screen = pygame.display.set_mode((CAMERA_WIDTH, CAMERA_HEIGHT), pygame.HWSURFACE)
        pygame.display.set_caption("Mad Salts")
        if INFO:
            print("window on screen initialized, with res: {}".format((CAMERA_WIDTH, CAMERA_HEIGHT)))


    def set_camera(self, camera):
        print("[SC] camera set: {}".format(camera))
        self.camera = camera

    def unset_camera(self):
        self.camera = None

    def blit_to_camera(self, surface, rect, camera_rect):
        if GRAPHICS_DEBUG:
            print(f"[GE] rect:{rect}\tblitted to:{camera}")
        if camera_rect.colliderect(rect):
            x0, y0 = rect.topleft
            x1, y1 = camera_rect.topleft
            dest = (x0 - x1, y0 - y1) # topleft of object - topleft of the camera
            self.screen.blit(surface, dest)
        else:
            if WARNING:
                print(f"[GE] '{surface}' not on camera: '{rect}'")

    def update_camera(self):
        self.screen.update()

    # load graphics resources (sounds, and graphics)
    # doesn't do any conversion. loads as is!
    def load_resources(self):
        """Goes through all the resource dirs, and loads the resources into a dict"""
        for resource_type in self.RESOURCE_DIRS:
            resource_dir = self.RESOURCE_DIRS[resource_type]
            resources = os.listdir(resource_dir)
            for resource in resources:
                self.resources[resource[:-4]] = pygame.image.load(os.path.join(resource_dir, resource))

    # update blitted (aka 'dirty') rectangles on every frame
    def update(self):
        if self.dirty_rects:
            self.update_dirty_rects()

    # takes a string, returns a blittable text label
    # word wrapping should be done by making multiple labels
    def make_text(self, text, color=(0, 0, 0)):
        raise NotImplementedError()
        if type(text) != str:
            raise TypeError("Text must be a string!")
        return self.font.render(text, 1, color)

    def add_text_overlay(self):
        pass

    # accepts a set of blittable objects
    # order matters! first with the background, and last is the foreground
    def display_all(self):
        # self.screen.fill(pygame.Color('black')) #  fill screen with black
        if len(self.dirty_rects) > 0:
            self.screen.update([rect for rect in self.dirty_rects.empty()])
        pygame.display.flip()

    # all rectangles that have changed on the display get updated
    def update_dirty_rects(self):
        """Updates every rectangle in game for rectangle in dirty rectangles"""
        pygame.display.update(self.dirty_rects)  # update is faster when all rectangles are passed at once
        if DEBUG:
            print("[GA] rects blitted: {}".format(self.dirty_rects))  # debugging
        self.dirty_rects.clear()

    # blits image to the display surface, and adds the rectangle to a list
    def blit(self, surface, rect, area=None):

        self.screen.blit(surface, rect, area)
        self.dirty_rects.append(rect)
        if DEBUG:
            print("[GE] blitted: {}, rect: {}".format(surface, rect))

    def display(self, image, rect):
        self.blit(image, rect)
        self.dirty_rects
        raise NotImplementedError("\nfinish this first!")

    # Graphical components test
    def blit_test(self, player):
        # self.screen.blit(self.resources['background'], (0,0))
        return self.screen.blit(player.sprite, player.rect)

# a camera surface that can be blitted on to the display
class Camera:
    def __init__(self, camera_func, target_rect, level_limit):
        self.camera_func = camera_func
        self.rect = pygame.Rect((0, 0), (CAMERA_WIDTH, CAMERA_HEIGHT))
        self.extreme_point = level_limit
        self.update(target_rect)  # this must be the last line, because it uses the state to define the next
        if INFO:
            print(f"[CA] Initiated {repr(self)}")

    def __repr__(self):
        x, y, w, h = self.rect
        return f"pos:{(x, y)}, size:{(w, h)}"

    def apply(self, rect):
        return rect.throw(self.state)

    def update(self, target_rect):
        half_camera_width = CAMERA_WIDTH / 2
        half_camera_height = CAMERA_HEIGHT / 2
        cx, cy = target_rect.center

        if 0 > cx - half_camera_width:
        #if cx > 300:
            self.rect.left = 0
        #elif cx < 300:
        elif self.extreme_point[0] < cx + half_camera_width:
            self.rect.right = self.extreme_point[0]
        else:
            self.rect.left = cx - half_camera_width

        if 0 > cy - half_camera_height:
            self.rect.top = 0
        elif self.extreme_point[1] < cy + half_camera_height:
            self.rect.bottom = self.extreme_point[1]
        else:
            self.rect.centery = cy
        if DEBUG:
            print("[CA] update: {}".format(self.rect))


def simple_camera(camera, target_rect):
    _, _, w, h = camera.rect
    x, y, _, _ = target_rect

    camera.rect = pygame.Rect(-x + CAMERA_WIDTH / 2, -y + CAMERA_HEIGHT / 2, w, h)


def complex_camera(camera, target_rect):

    x, y, _, _ = target_rect
    _, _, w, h = camera.rect
    x, y = x - camera.rect.width/2, camera.rect.height/2 - y

    x = max(0, x)  # stop scrolling at the left edge
    x = min(-(camera.rect.width - camera.extreme_point[0]), x)  # stop scrolling at the right edge
    y = max(-(camera.rect.height - camera.extreme_point[1]), y)  # stop scrolling at the bottom
    y = min(0, y)  # stop scrolling at the top
    camera.rect = pygame.Rect(x, y, w, h)


# only one graphics engine can be initialized at the same time, for now
# the controller has to be imported into the namespace of the program (from Graphics import controller)
controller = Graphics()
