from queue import Queue, Full
from threading import Thread
from time import sleep

from settings import *


class EventHandler(Queue, Thread):
    def __init__(self):
        super(EventHandler, self).__init__()
        Thread.__init__(self)

    # adds
    def add(self, event):
        try:
            if INFO:
                print("[G] event added: {}".format(event.TYPE))
            self.put_nowait(event)
            # default behaviour is to dispose of the event when the queue is full
        except Full:
            if WARNING:
                print("[!] warning, event queue is full, event disposed: {}".format(event.TYPE))

    def handle_events(self):
        if self.qsize() < 10:
            while not self.empty():
                event = self.get()
                event.handle()
        elif 20 < self.qsize() >= 10:
            if WARNING:
                print("[!]queue is 10 items or more large")
            for _ in range(10):
                event = self.get()
                event.handle()
        else:
            if WARNING:
                print("[!]queue seems to get big, add queue handling code")
            while not self.empty():
                event = self.get()
                event.handle()

    def run(self):
        self.running = True
        while self.running:
            while not self.has_event():
                sleep(0.1)
            else:
                self.handle_game_events()

event_handler = EventHandler()