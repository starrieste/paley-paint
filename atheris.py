import pygame
import tkinter
import math
import sys
import os

from tkinter import filedialog

DIR = [(0, 1), (1, 0), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

def dist(a, b):
        return ((a[0] - b[0])**2 + (a[1] - b[1])**2)**(1/2)

def choose_file(save=False):
        filetypes = [('PNG files', '*.png'), ('JPEG files', '*.jpg'), ('All files', '*.*')]
        if save:
                return filedialog.asksaveasfile(filetypes=filetypes, defaultextension="*.png").name
        return filedialog.askopenfilename(filetypes=filetypes, defaultextension="*.png")

class Canvas:
        def __init__(self, WS, size):
                self.width = size[0]
                self.height = size[1]
                self.image = pygame.Surface((self.width, self.height))
                self.image.fill((255, 255, 255))
                self.pos = [WS[0]/2 - self.width/2, WS[1]/2 - self.height/2]

                self.panning = False
                self.pan_relation = [0, 0]

                self.last_spot = [None, None]
                self.undo_history = []
                self.redo_history = []
                self.last_undo_tick = 0
                self.last_redo_tick = 0
                self.undo_interval = 0
                self.redo_interval = 0

                self.sketching = False
                self.brush_size = 3
                self.brush_color = [122, 0, 255]
                self.brush_img = pygame.Surface((self.brush_size*2, self.brush_size*2), pygame.SRCALPHA, 32).convert_alpha()
                pygame.draw.circle(self.brush_img, self.brush_color, (self.brush_size, self.brush_size), self.brush_size)

                self.save_path = None
                self.scale = 1

        def save(self, save_as=False):
                if self.save_path != None and not save_as and os.path.isfile(self.save_path):
                        pygame.image.save(self.image, self.save_path)
                else:
                        filepath = choose_file(True)
                        if not filepath: return
                        pygame.image.save(self.image, filepath)
                        self.save_path = filepath
        def load(self):
                filepath = choose_file()
                if not filepath: return
                self.save_path = filepath
                load_img = pygame.image.load(filepath).convert()

                self.width, self.height = load_img.get_size()
                self.pos = [self.program.WS[0]/2 - self.width/2, self.program.WS[1]/2 - self.height/2]
                self.image = pygame.Surface(load_img.get_size())
                self.image.blit(load_img, (0, 0))

                self.undo_history.clear()
                self.redo_history.clear()

        # panning
        def pan(self, mp):
                self.panning = True
                self.pan_relation = [self.pos[0] - mp[0], self.pos[1] - mp[1]]
        def stop_pan(self):
                self.panning = False

        # undo and redo
        def undo(self):
                self.sketching = False
                if len(self.undo_history):
                        now = pygame.time.get_ticks()
                        if now - self.last_undo_tick >= self.undo_interval:
                                self.redo_history.insert(0, self.image.copy())
                                self.image = self.undo_history[0].copy()
                                self.undo_history.pop(0)
                                self.undo_interval = max(25, self.undo_interval / 2)
                                self.last_undo_tick = now
        def redo(self):
                self.sketching = False
                if len(self.redo_history):
                        now = pygame.time.get_ticks()
                        if now - self.last_redo_tick >= self.redo_interval:
                                self.undo_history.insert(0, self.image.copy())
                                self.image = self.redo_history[0].copy()
                                self.redo_history.pop(0)
                                self.redo_interval = max(25, self.redo_interval / 2)
                                self.last_redo_tick = now

        def drawline(self, bimg, start_pos, end_pos):
                x, y = start_pos
                self.image.blit(bimg, (end_pos[0] - bimg.get_width()/2, end_pos[1] - bimg.get_height()/2))
                self.image.blit(bimg, (x - bimg.get_width()/2, y - bimg.get_height()/2))
                angle = math.atan2(start_pos[1] - end_pos[1], start_pos[0] - end_pos[0]) + math.pi
                angle = round(angle, 6)
                radius = 1
                while radius < dist(start_pos, end_pos):
                        radius += 1
                        self.image.blit(bimg, (round(x - bimg.get_width()/2 + math.cos(angle)*radius), round(y - bimg.get_height()/2 + math.sin(angle)*radius)))
                self.image.blit(bimg, (start_pos[0] - bimg.get_width()/2, start_pos[1] - bimg.get_height()/2))

        def sketch(self, mp):
                relative_mp = [mp[0] - self.pos[0], mp[1] - self.pos[1]]
                ratio = [relative_mp[0] / (self.width * self.scale), relative_mp[1] / (self.height * self.scale)]
                
                cur_spot = [self.width * ratio[0], self.height * ratio[1]]

                self.drawline(self.brush_img, self.last_spot if not None in self.last_spot else cur_spot, cur_spot)
                #pygame.draw.line(self.image, self.brush_color, cur_spot, self.last_spot if not None in self.last_spot else cur_spot, self.brush_size)
                                        
                self.last_spot = cur_spot

        def update(self, mp):
                if (self.panning):
                        self.pos = [mp[0] + self.pan_relation[0], mp[1] + self.pan_relation[1]]

                if (self.sketching):
                        self.sketch(mp)
                else: self.last_spot = [None, None]

        def render(self, surf):
                surf.blit(pygame.transform.scale(self.image, (self.width * self.scale, self.height * self.scale)), self.pos)

class Atheris:
        def __init__(self):
                self.WS = (1200, 800)
                self.display = pygame.display.set_mode(self.WS, pygame.RESIZABLE, depth=32)
                pygame.display.set_caption("Atheris Paint")
                self.clock = pygame.time.Clock()
                self.canvas = Canvas(self.WS, (800, 600))

                root = tkinter.Tk()
                root.withdraw()

                self.mb = [False, False, False]
                self.mp = [0, 0]

                self.holding = set()
                self.hold_switch = False

                self.ZOOM_PERCENT = [0.9, 1.1]
        
        def run(self):
                while True:
                        for event in pygame.event.get():
                                if event.type == pygame.QUIT:
                                        pygame.quit()
                                        sys.exit()

                                #if event.type == pygame.VIDEORESIZE:
                                #        pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

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
                                        if event.button == 1:
                                                self.mb[0] = True
                                                if 32 in self.holding:
                                                        self.canvas.pan(self.mp)
                                                if not self.canvas.panning:
                                                        self.canvas.sketching = True
                                                        self.canvas.redo_history.clear()
                                                        self.canvas.undo_history.insert(0, self.canvas.image.copy())
                                        if event.button == 2:
                                                self.mb[1] = True
                                                self.canvas.pan(self.mp)
                                        if event.button == 3:
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
                                        if event.button == 2:
                                                self.mb[1] = False
                                        if event.button == 3:
                                                self.mb[2] = False

                        self.mp = pygame.mouse.get_pos()

                        # shortcuts and flags
                        if not self.mb[1] and not (self.mb[0] and pygame.K_SPACE in self.holding): self.canvas.stop_pan()
                        if pygame.K_z in self.holding and (pygame.K_LCTRL in self.holding or pygame.K_RCTRL in self.holding): self.canvas.undo()
                        if pygame.K_y in self.holding and (pygame.K_LCTRL in self.holding or pygame.K_RCTRL in self.holding): self.canvas.redo()
                        # shortcuts and flags

                        self.display.fill((20, 20, 30))
                        
                        self.canvas.update(self.mp)
                        self.canvas.render(self.display)

                        pygame.display.flip()

if __name__ == "__main__":
        Atheris().run()