import sys, time
from threading import Thread

from game import Game



def simulate_input(game):
    from events import NewMonsterEvent
    time.sleep(3)
    #game.add_game_event(AddTextEvent(level=game.level, text=MOVEMENT_INSTRUCTIONS, pos=(20, 20), size=(300, 150)))
    #game.add_game_event(create_game_event("Attack", attacker= game.image.player, pos=(20, 20)))
    game.add_game_event(NewMonsterEvent(type='Schagel', pos=(300, 50), size=(58, 52), level=game.level))

def rectangle_test():
    import pygame
    a = pygame.Rect((0, 0), (1280, 720))
    b = pygame.Rect((200, 400), (300, 460))
    print("clamp: " + str(b.clamp(a))) # intersect

    a = pygame.Rect((0, 0), (1280, 720))
    b = pygame.Rect((1200, 700), (300, 460))
    print("contains: " + str(a.contains(b)))  # has to be completely contained

    a = pygame.Rect((100, 100), (1200, 720))
    b = pygame.Rect((0, 0), (1280, 720))
    print("adding top-left: " + str(a.topleft+b.topleft))

    a = pygame.Rect((1, 1), (1280, 720))
    print("inflate: " + str(a.inflate(2, 2)))

    a = pygame.Rect((1, 1), (1280, 720))
    print("throw: " + str(a.throw(0.6, 0.6))) # doesn't throw when number is lower than 0





# game is a global variable
def main():
    #rectangle_test()
    #exit()
    #display_level1(int(input("which level number to display: "))) # only inits level, and displays it

    game = Game()
    #Thread(target=simulate_input, args=[game]).start()
    game.launch()


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt as ex:
        print("[!] keyboard interrupt signal received!")
