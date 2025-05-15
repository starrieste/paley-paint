# canvas.py
# canvas object holds all properties for the canvas
# brushes are managed here, and all blitting onto canvas, as well as saving and handling data

import pygame
import math
import os

from scripts.util import *
from scripts.button import FileButton

class Canvas:
        def __init__(self, program, WS, size, initial=True):
                # used to reference variables outside of this object
                self.program = program

                self.width = size[0]
                self.height = size[1]
                if (self.width > self.height): self.scale = (self.program.WS[0] * 0.7) / self.width # auto-calculate a good scale
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
                # so, as we're holding down ctrl z or ctrl y, we want to start slow, and go faster and faster to do the action.
                # this is why the interval is a variable that will get smaller and smaller.
                self.undo_interval = 0
                self.redo_interval = 0

                self.last_spot = (None, None)
                self.drawing = False
                self.crosshair_img = pygame.image.load("images/crosshair.png").convert_alpha()
                self.crosshair_img.set_colorkey((0,0,0))
                self.show_crosshair = False

                self.plot_a = None
                self.plot_b = None

                self.load_ID = 0
                self.placing_sticker = False
                self.sticker_img = None
                self.sticker_name = None

                # the main file will run __init__ canvas several times, so we only want to
                # initialize the brush if it's the first time we're running __init__.
                if initial: 
                        self.brush_color = (0,0,0)
                        self.brush_size = 10
                        self.set_brush(self.brush_color, self.brush_size)
                        self.save_path = None
                        self.brush_mode = "pencil"
                        self.brush_toggle = False

        def set_brush(self, color, size):
                # I ran into an error here once while testing... but I can't recreate it.
                # So I threw an error catcher here for damage control just in case it's encountered again.
                try:
                        self.brush_size = size;
                        if color == None: color = self.brush_color
                        if size > 1:
                                # the brush img is a surface with a circle on it
                                # the brush preview is a greyed out hollow circle
                                self.brush_img = pygame.Surface((self.brush_size*2, self.brush_size*2), pygame.SRCALPHA, 32).convert_alpha()
                                pygame.draw.circle(self.brush_img, color, (self.brush_size, self.brush_size), self.brush_size)
                                self.brush_preview = pygame.Surface((self.brush_size*2, self.brush_size*2), pygame.SRCALPHA, 32).convert_alpha()
                                pygame.draw.circle(self.brush_preview, (111,111,111), (self.brush_size, self.brush_size), self.brush_size, width=2)
                        else: # if the brush is size 1 then the brush preview is just a square of color showing where the pixel is placed.
                                self.brush_img = pygame.Surface((1,1))
                                self.brush_img.fill(color)

                                self.brush_preview = pygame.Surface((1,1))
                                self.brush_preview.fill(color)
                except Exception as e:
                        print("Unexpected error while setting brush: ", e, color)
        
        def save(self, save_as=False):
                if self.save_path != None and not save_as and os.path.isfile(self.save_path):
                        pygame.image.save(self.image, self.save_path)
                else:
                        filepath = choose_file(True)
                        if not filepath: return # cancel if the user cancelled
                        filepath = filepath.name
                        pygame.image.save(self.image, filepath)
                        self.save_path = filepath

        def load(self, load_data=None, removed=False):
                # if the tag removed is true, then the current file was closed and we shouldn't save progress.
                if load_data == None: # we should choose a file to load
                        filepath = choose_file()
                        if not filepath: return # cancel if the user cancelled
                        self.save_path = filepath
                        load_img = pygame.image.load(filepath).convert_alpha()

                        if not removed:
                                self.program.filebuttons[self.load_ID].data = [self.image, self.undo_history, self.redo_history, self.load_ID, self.save_path]

                        self.undo_history = []
                        self.redo_history = []

                        self.load_ID = len(self.program.filebuttons)
                        self.program.filebuttons.append(FileButton(self.program, (self.program.filebuttonX,25), self.image, self.undo_history, self.redo_history, self.load_ID, self.save_path))
                        self.program.filebuttonX += 110

                        self.width, self.height = load_img.get_size()
                        if (self.width > self.height): self.scale = (self.program.WS[0] * 0.7) / self.width
                        else : self.scale = (self.program.WS[1] * 0.7) / self.height
                        self.pos = [self.program.WS[0]/2 - self.width*self.scale/2, self.program.WS[1]/2 - self.height*self.scale/2]
                        self.image = pygame.Surface(load_img.get_size())
                        self.image.blit(load_img, (0, 0))

                else: # we are loading from a surf, load_data should contain [canvas_img, undo_history, redo_history]
                        if not removed:
                                self.program.filebuttons[self.load_ID].data = [self.image, self.undo_history, self.redo_history, self.load_ID, self.save_path]

                        self.image, self.undo_history, self.redo_history, self.load_ID, self.save_path = load_data

                        self.width, self.height = load_data[0].get_size()
                        if (self.width > self.height): self.scale = (self.program.WS[0] * 0.7) / self.width
                        else : self.scale = (self.program.WS[1] * 0.7) / self.height
                        self.pos = [self.program.WS[0]/2 - self.width*self.scale/2, self.program.WS[1]/2 - self.height*self.scale/2]
                        

        # panning
        def pan(self, mp):
                self.panning = True
                self.pan_relation = [self.pos[0] - mp[0], self.pos[1] - mp[1]]

        # undo and redo
        def undo(self):
                self.drawing = False
                if len(self.undo_history):
                        now = pygame.time.get_ticks()
                        if now - self.last_undo_tick >= self.undo_interval:
                                self.redo_history.insert(0, self.image.copy())
                                self.image = self.undo_history[0].copy()
                                self.undo_history.pop(0)
                                self.undo_interval = max(25, self.undo_interval / 2)
                                self.last_undo_tick = now
        def redo(self):
                self.drawing = False
                if len(self.redo_history):
                        now = pygame.time.get_ticks()
                        if now - self.last_redo_tick >= self.redo_interval:
                                self.undo_history.insert(0, self.image.copy())
                                self.image = self.redo_history[0].copy()
                                self.redo_history.pop(0)
                                self.redo_interval = max(25, self.redo_interval / 2)
                                self.last_redo_tick = now

        def drawline(self, bimg, start_pos, end_pos, surf): # custom line drawer function
                start_pos = list(map(int, start_pos))
                end_pos = list(map(int, end_pos))
                x, y = start_pos
                surf.blit(bimg, (end_pos[0] - bimg.get_width()/2, end_pos[1] - bimg.get_height()/2))
                surf.blit(bimg, (x - bimg.get_width()/2, y - bimg.get_height()/2))
                angle = math.atan2(start_pos[1] - end_pos[1], start_pos[0] - end_pos[0]) + math.pi
                radius = 0
                while radius < int(dist(start_pos, end_pos)):
                        radius += 0.5
                        # put one pixel if brush size is 1, otherwise blit the brush image
                        # technically I could use the brush image anyway, but I was debugging and changed it and I don't want to change anything now
                        if (self.brush_size == 1):
                                surf.set_at((round(x - bimg.get_width()/2 + math.cos(angle)*radius), round(y - bimg.get_height()/2 + math.sin(angle)*radius)), self.brush_color)
                        surf.blit(bimg, (round(x - bimg.get_width()/2 + math.cos(angle)*radius), round(y - bimg.get_height()/2 + math.sin(angle)*radius)))
                surf.blit(bimg, (start_pos[0] - bimg.get_width()/2, start_pos[1] - bimg.get_height()/2))

        def sketch(self, mp, cur_spot):
                # every frame we draw a line from the last known spot to the current known spot
                self.drawline(self.brush_img, self.last_spot if not None in self.last_spot else cur_spot, cur_spot, self.image)
                self.last_spot = cur_spot

        def splash(self, mp, cur_spot):
                # here is just a bunch of checks that make sure we're good to go before lagging out the entire program
                if not self.drawing: return
                if self.brush_toggle: return
                if cur_spot[0] < 0 or cur_spot[0] >= self.width or cur_spot[1] < 0 or cur_spot[1] >= self.height: return
                if (self.image.get_at(cur_spot)[:2] == tuple(map(int, self.brush_color))[:2]): return
                self.brush_toggle = True
                if cur_spot[0] < 0 or cur_spot[0] > self.width or cur_spot[1] < 0 or cur_spot[1] > self.height: return

                pxarray = pygame.PixelArray(self.image)

                # basic breadth first search to flood fill
                DIR = [(0, -1), (0, 1), (-1, 0), (1, 0)]
                visited = {}
                queue = []
                queue.append(cur_spot)
                visited[cur_spot] = True
                og_color = pxarray[cur_spot[0]][cur_spot[1]]

                while len(queue):
                        cur = queue[0]
                        queue.pop(0)
                        pxarray[cur[0]][cur[1]] = self.brush_color
                        for d in DIR:
                                nxt = (cur[0] + d[0], cur[1] + d[1])
                                if nxt[0] >= 0 and nxt[0] < self.width and nxt[1] >= 0 and nxt[1] < self.height:
                                        if not nxt in visited and pxarray[nxt[0]][nxt[1]] == og_color:
                                                queue.append(nxt)
                                                visited[nxt] = True

                del pxarray
                self.drawing = False

        def update(self, mp, mb):
                self.scaled_width, self.scaled_height = self.width * self.scale, self.height * self.scale
                hover = mp[0] >= self.pos[0] and mp[0] - self.pos[0] <= self.scaled_width and mp[1] >= self.pos[1] and mp[1] - self.pos[1] <= self.scaled_height

                # flags
                if not mb[0]: 
                        self.drawing = False
                        self.brush_toggle = False
                if not mb[1] and not (mb[0] and pygame.K_SPACE in self.program.holding): self.panning = False
                if pygame.K_z in self.program.holding and \
                        (pygame.K_LCTRL in self.program.holding or pygame.K_RCTRL in self.program.holding): self.undo()
                if pygame.K_y in self.program.holding and \
                        (pygame.K_LCTRL in self.program.holding or pygame.K_RCTRL in self.program.holding): self.redo()
                ##

                if (self.panning):
                        self.pos = [mp[0] + self.pan_relation[0], mp[1] + self.pan_relation[1]]

                # handle drawing
                if not self.program.mb[0]:
                        self.drawing = False

                relative_mp = [mp[0] - self.pos[0], mp[1] - self.pos[1]]
                ratio = [relative_mp[0] / (self.width * self.scale), relative_mp[1] / (self.height * self.scale)]
                cur_spot = (int(self.width * ratio[0]+1), int(self.height * ratio[1]+1))
                # doing different things based on which brush mode we're in
                if self.drawing:
                        if self.panning: return
                        if self.brush_mode in ("pencil", "eraser"):
                                self.sketch(mp, cur_spot)
                        if self.brush_mode == "bucket":
                                self.splash(mp, cur_spot)
                        if self.brush_mode == "dropper":
                                if hover: 
                                        self.brush_color = self.image.get_at(cur_spot)
                                        self.program.canvas.set_brush(self.brush_color, self.program.canvas.brush_size)
                        if self.brush_mode == "sticker":
                                self.placing_sticker = True
                        else: self.placing_sticker = False
                        if self.brush_mode in ("line", "unfilled_rect", "filled_rect", "unfilled_ellipse", "filled_ellipse"):
                                if self.plot_a == None:
                                        self.plot_a = cur_spot
                                self.plot_b = cur_spot
                        else: self.plot_a = None
                else: 
                        self.last_spot = (None, None)

                        if self.placing_sticker and self.sticker_img != None:
                                cur_spot2 = [int(self.width * ratio[0] - self.sticker_img.get_width()/2+1), int(self.height * ratio[1] - self.sticker_img.get_height()/2+1)]
                                self.image.blit(self.sticker_img, cur_spot2)
                                self.placing_sticker = False
                        
                        if self.plot_a != None:
                                if self.brush_mode == "line":
                                        self.drawline(self.brush_img, self.plot_a, self.plot_b, self.image)
                                if self.brush_mode == "unfilled_rect":
                                        w, h = max(self.plot_a[0], self.plot_b[0]) - min(self.plot_a[0], self.plot_b[0]), \
                                                max(self.plot_a[1], self.plot_b[1]) - min(self.plot_a[1], self.plot_b[1])
                                        pygame.draw.rect(self.image, self.brush_color, \
                                                (min(self.plot_a[0], self.plot_b[0]), min(self.plot_a[1], self.plot_b[1]), w, h), \
                                                        width=self.brush_size)
                                if self.brush_mode == "filled_rect":
                                        w, h = max(self.plot_a[0], self.plot_b[0]) - min(self.plot_a[0], self.plot_b[0]), \
                                                max(self.plot_a[1], self.plot_b[1]) - min(self.plot_a[1], self.plot_b[1])
                                        pygame.draw.rect(self.image, self.brush_color, \
                                                (min(self.plot_a[0], self.plot_b[0]), min(self.plot_a[1], self.plot_b[1]), w, h))
                                if self.brush_mode == "unfilled_ellipse":
                                        w, h = max(self.plot_a[0], self.plot_b[0]) - min(self.plot_a[0], self.plot_b[0]), \
                                                max(self.plot_a[1], self.plot_b[1]) - min(self.plot_a[1], self.plot_b[1])
                                        pygame.draw.ellipse(self.image, self.brush_color, \
                                                (min(self.plot_a[0], self.plot_b[0]), min(self.plot_a[1], self.plot_b[1]), w, h), \
                                                        width=self.brush_size)
                                if self.brush_mode == "filled_ellipse":
                                        w, h = max(self.plot_a[0], self.plot_b[0]) - min(self.plot_a[0], self.plot_b[0]), \
                                                max(self.plot_a[1], self.plot_b[1]) - min(self.plot_a[1], self.plot_b[1])
                                        pygame.draw.ellipse(self.image, self.brush_color, \
                                                (min(self.plot_a[0], self.plot_b[0]), min(self.plot_a[1], self.plot_b[1]), w, h))

                        self.plot_a = None
                ##

                flag = False
                for button in self.program.buttons + self.program.filebuttons:
                        if button.update(self.program.mp, self.program.mb):
                                flag = True

                # handle mouse visibility
                if not hover or flag or self.program.showing_guide:
                        pygame.mouse.set_visible(True)
                        self.show_crosshair = False
                else:
                        if self.brush_mode in ["bucket","dropper", "unfilled_rect", "unfilled_ellipse", "filled_rect", "filled_ellipse"]:
                                self.show_crosshair = True
                                pygame.mouse.set_visible(False)
                        else: 
                                if self.brush_size > 1:
                                        pygame.mouse.set_visible(False)
                                self.show_crosshair = False
                ##

                # save all the info to the current tab
                self.program.filebuttons[self.load_ID].icon = pygame.transform.scale(self.image, (50,50))
                self.program.filebuttons[self.load_ID].undo_history = self.undo_history.copy()
                self.program.filebuttons[self.load_ID].redo_history = self.redo_history.copy()
                self.program.filebuttons[self.load_ID].save_path = self.save_path

        def render(self, surf, mp):
                # check if a button is being interacted with
                flag = False
                for button in self.program.buttons + self.program.filebuttons:
                        if button.update(self.program.mp, self.program.mb):
                                flag = True

                # a copy of the canvas is used to render the brush previews
                self.imagec = self.image.copy()
                relative_mp = [mp[0] - self.pos[0], mp[1] - self.pos[1]]
                ratio = [relative_mp[0] / (self.width * self.scale), relative_mp[1] / (self.height * self.scale)]
                cur_spot = [int(self.width * ratio[0] - self.brush_size+1), int(self.height * ratio[1] - self.brush_size+1)]

                if self.plot_a != None:
                        if self.brush_mode == "line":
                                self.drawline(self.brush_img, self.plot_a, self.plot_b, self.imagec)
                        if self.brush_mode == "unfilled_rect":
                                w, h = max(self.plot_a[0], self.plot_b[0]) - min(self.plot_a[0], self.plot_b[0]), \
                                        max(self.plot_a[1], self.plot_b[1]) - min(self.plot_a[1], self.plot_b[1])
                                pygame.draw.rect(self.imagec, self.brush_color, \
                                        (min(self.plot_a[0], self.plot_b[0]), min(self.plot_a[1], self.plot_b[1]), w, h), \
                                                width=self.brush_size)
                        if self.brush_mode == "filled_rect":
                                w, h = max(self.plot_a[0], self.plot_b[0]) - min(self.plot_a[0], self.plot_b[0]), \
                                        max(self.plot_a[1], self.plot_b[1]) - min(self.plot_a[1], self.plot_b[1])
                                pygame.draw.rect(self.imagec, self.brush_color, \
                                        (min(self.plot_a[0], self.plot_b[0]), min(self.plot_a[1], self.plot_b[1]), w, h))
                        if self.brush_mode == "unfilled_ellipse":
                                w, h = max(self.plot_a[0], self.plot_b[0]) - min(self.plot_a[0], self.plot_b[0]), \
                                        max(self.plot_a[1], self.plot_b[1]) - min(self.plot_a[1], self.plot_b[1])
                                pygame.draw.ellipse(self.imagec, self.brush_color, \
                                        (min(self.plot_a[0], self.plot_b[0]), min(self.plot_a[1], self.plot_b[1]), w, h), \
                                                width=self.brush_size)
                        if self.brush_mode == "filled_ellipse":
                                w, h = max(self.plot_a[0], self.plot_b[0]) - min(self.plot_a[0], self.plot_b[0]), \
                                        max(self.plot_a[1], self.plot_b[1]) - min(self.plot_a[1], self.plot_b[1])
                                pygame.draw.ellipse(self.imagec, self.brush_color, \
                                        (min(self.plot_a[0], self.plot_b[0]), min(self.plot_a[1], self.plot_b[1]), w, h))

                if self.placing_sticker and self.sticker_img != None:
                        # a different cur_spot is used because the other cur_spot isn't offset by the image size
                        cur_spot2 = [int(self.width * ratio[0] - self.sticker_img.get_width()/2+1), int(self.height * ratio[1] - self.sticker_img.get_height()/2+1)]
                        self.imagec.blit(self.sticker_img, cur_spot2)

                # deciding whether to show the crosshair 
                if not flag and not pygame.mouse.get_visible() and not self.show_crosshair: self.imagec.blit(self.brush_preview, cur_spot)
                surf.blit(pygame.transform.scale(self.imagec, (self.scaled_width, self.scaled_height)), self.pos)
                if self.show_crosshair or self.brush_size == 1: surf.blit(self.crosshair_img, (mp[0] - self.crosshair_img.get_width()/2, mp[1] - self.crosshair_img.get_height()/2))
