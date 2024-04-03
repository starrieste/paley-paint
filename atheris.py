import pygame
import tkinter
import sys

from scripts.canvas import Canvas
from scripts.docker import Docker

class Atheris:
        def __init__(self):
                self.WS = (1600, 900)
                self.display = pygame.display.set_mode(self.WS, pygame.RESIZABLE, depth=32)
                pygame.display.set_caption("Atheris Paint")
                self.clock = pygame.time.Clock()
                self.canvas = Canvas(self, self.WS, (1000, 1200))

                root = tkinter.Tk()
                root.withdraw()

                self.mb = [False, False, False]
                self.mp = [0, 0]

                self.holding = set()
                self.hold_switch = False

                self.ZOOM_PERCENT = [0.9, 1.1]

                self.docker_left = Docker(self, (38,36,50), [0, 0])

        
        def run(self):
                while True:
                        for event in pygame.event.get():
                                if event.type == pygame.QUIT:
                                        pygame.quit()
                                        sys.exit()

                                if event.type == pygame.WINDOWRESIZED:
                                        self.WS = pygame.display.get_window_size()

                                if event.type == pygame.KEYDOWN:
                                        self.holding.add(event.key)

                                        if event.key == pygame.K_z:
                                                if pygame.K_LCTRL in self.holding or pygame.K_RCTRL in self.holding:
                                                        self.canvas.undo_interval = 600
                                                        self.canvas.undo()
                                        if event.key == pygame.K_y:
                                                if pygame.K_LCTRL in self.holding or pygame.K_RCTRL in self.holding:
                                                        self.canvas.redo_interval = 600
                                                        self.canvas.redo()
                                        if event.key == pygame.K_s:
                                                if pygame.K_LCTRL in self.holding or pygame.K_RCTRL in self.holding:
                                                        if pygame.K_LSHIFT in self.holding or pygame.K_RSHIFT in self.holding:
                                                                self.canvas.save(True)
                                                        else: self.canvas.save()
                                        if event.key == pygame.K_o:
                                                if pygame.K_LCTRL in self.holding or pygame.K_RCTRL in self.holding:
                                                        self.canvas.load()

                                if event.type == pygame.KEYUP:
                                        self.holding.remove(event.key)

                                        if event.key == pygame.K_z:
                                                self.canvas.last_undo_tick = 0
                                        if event.key == pygame.K_y:
                                                self.canvas.last_redo_tick = 0

                                if event.type == pygame.MOUSEBUTTONDOWN:
                                        if event.button == 1: # LMB
                                                self.mb[0] = True
                                                if not self.docker_left.check_grab(self.mp):
                                                        if 32 in self.holding:
                                                                self.canvas.pan(self.mp)
                                                        if not self.canvas.panning and not self.docker_left.grab and not self.docker_left.hover:
                                                                self.canvas.sketching = True
                                                                self.canvas.redo_history.clear()
                                                                self.canvas.undo_history.insert(0, self.canvas.image.copy())
                                        if event.button == 2: # MMB
                                                self.mb[1] = True
                                                self.canvas.pan(self.mp)
                                        if event.button == 3: # RMB
                                                self.mb[2] = True
                                        if event.button == 4:
                                                new_scale = self.canvas.scale * self.ZOOM_PERCENT[1]
                                                if self.canvas.width * new_scale <= self.WS[0]*2 or \
                                                                self.canvas.height * new_scale <= self.WS[1]*2:

                                                        distsave = [self.mp[0] - self.canvas.pos[0], self.mp[1] - self.canvas.pos[1]]
                                                        proportion = self.canvas.scale / new_scale
                                                        self.canvas.scale = new_scale
                                                        self.canvas.scale = round(self.canvas.scale, 2)
                                                        self.canvas.pos = [self.mp[0] - (distsave[0] / proportion), self.mp[1] - (distsave[1] / proportion)]
                                        if event.button == 5:
                                                new_scale = self.canvas.scale * self.ZOOM_PERCENT[0]
                                                if (self.canvas.width * new_scale >= 40 and \
                                                                self.canvas.height * new_scale >= 40) and new_scale > 0:

                                                        distsave = [self.mp[0] - self.canvas.pos[0], self.mp[1] - self.canvas.pos[1]]
                                                        proportion = self.canvas.scale / new_scale
                                                        self.canvas.scale = new_scale
                                                        self.canvas.scale = round(self.canvas.scale, 2)
                                                        self.canvas.pos = [self.mp[0] - (distsave[0] / proportion), self.mp[1] - (distsave[1] / proportion)]

                                if event.type == pygame.MOUSEBUTTONUP:
                                        if event.button == 1:
                                                self.mb[0] = False
                                                self.canvas.sketching = False
                                                self.docker_left.ungrab()
                                        if event.button == 2:
                                                self.mb[1] = False
                                        if event.button == 3:
                                                self.mb[2] = False

                        self.mp = pygame.mouse.get_pos()

                        self.display.fill((25,24,31))
                        
                        self.canvas.update(self.mp)
                        self.canvas.render(self.display)

                        self.docker_left.update(self.mp, self.mb)
                        self.docker_left.render(self.display)

                        pygame.display.flip()

if __name__ == "__main__":
        Atheris().run()