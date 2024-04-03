import pygame
import math
import os

from scripts.util import *

class Canvas:
        def __init__(self, program, WS, size):
                self.program = program

                self.width = size[0]
                self.height = size[1]
                if (self.width > self.height): self.scale = (self.program.WS[0] * 0.7) / self.width
                else : self.scale = (self.program.WS[1] * 0.7) / self.height

                self.pos = [WS[0]/2 - self.width*self.scale/2, WS[1]/2 - self.height*self.scale/2]
                self.panning = False
                self.pan_relation = [0, 0]

                self.image = pygame.Surface((self.width, self.height))
                self.image.fill((255, 255, 255))

                self.undo_history = []
                self.redo_history = []
                self.last_undo_tick = 0
                self.last_redo_tick = 0
                self.undo_interval = 0
                self.redo_interval = 0

                self.last_spot = [None, None]
                self.sketching = False
                self.brush_color = [122, 0, 255]
                self.brush_size = 3

                self.brush_img = pygame.Surface((self.brush_size*2, self.brush_size*2), pygame.SRCALPHA, 32).convert_alpha()
                pygame.draw.circle(self.brush_img, self.brush_color, (self.brush_size, self.brush_size), self.brush_size)

                self.save_path = None

        def save(self, save_as=False):
                if self.save_path != None and not save_as and os.path.isfile(self.save_path):
                        pygame.image.save(self.image, self.save_path)
                else:
                        filepath = choose_file(True)
                        if not filepath: return
                        filepath = filepath.name
                        pygame.image.save(self.image, filepath)
                        self.save_path = filepath
        def load(self):
                filepath = choose_file()
                if not filepath: return
                self.save_path = filepath
                load_img = pygame.image.load(filepath).convert()

                self.width, self.height = load_img.get_size()
                if (self.width > self.height): self.scale = (self.program.WS[0] * 0.7) / self.width
                else : self.scale = (self.program.WS[1] * 0.7) / self.height
                self.pos = [self.program.WS[0]/2 - self.width*self.scale/2, self.program.WS[1]/2 - self.height*self.scale/2]
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
                start_pos = list(map(int, start_pos))
                end_pos = list(map(int, end_pos))
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
                # FLAGS
                if not self.program.mb[1] and not (self.program.mb[0] and pygame.K_SPACE in self.program.holding): self.stop_pan()
                if pygame.K_z in self.program.holding and \
                        (pygame.K_LCTRL in self.program.holding or pygame.K_RCTRL in self.program.holding): self.undo()
                if pygame.K_y in self.program.holding and \
                        (pygame.K_LCTRL in self.program.holding or pygame.K_RCTRL in self.program.holding): self.redo()
                # /FLAGS
                if (self.panning):
                        self.pos = [mp[0] + self.pan_relation[0], mp[1] + self.pan_relation[1]]

                if (self.sketching):
                        self.sketch(mp)
                else: self.last_spot = [None, None]

        def render(self, surf):
                surf.blit(pygame.transform.scale(self.image, (self.width * self.scale, self.height * self.scale)), self.pos)