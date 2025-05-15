# paley.py
# this is my main file, where the main loop is.

import pygame
# tkinter is used for the color picker, and the file dialogs.
import tkinter
import sys

from scripts.button import *
from scripts.canvas import Canvas

# everything was put into a class for organization and readability.
class Paley:
        def __init__(self):
                self.WS = (1600, 900) # WS = Window Size
                # initiating pygame and setting up the window
                self.display = pygame.display.set_mode(self.WS, pygame.RESIZABLE, depth=32)
                pygame.display.set_caption("Paley Paint")
                self.clock = pygame.time.Clock()
                self.canvas = Canvas(self, self.WS, (1000, 1200))

                # logo image displayed in the top left, rendered every iteration later
                self.title_img = pygame.image.load("images/title.png").convert_alpha()

                root = tkinter.Tk()
                root.withdraw()

                self.mb = [False, False, False] # used for keeping track of whether a mouse button is held down or not
                self.mp = [0, 0] # passed to all the functions in other .py files for usage
                self.busymb = [False, False, False] # keep track if the mouse buttons are busy interacting with an element already.
                self.input_delay = 0 # used to disallow button interaction for a while in button.py

                self.holding = set() # keeps track of all the keys currently held down
                self.ZOOM_PERCENT = [0.9, 1.1] # this is used for increments. when the canvas scale is changed, it will go -10% or +10%, because this is 0.9 and 1.1.

                # keeps consistent spacing. stored in variables for readability.
                x_interval = 100 
                y_interval = 110

                # stores all the button objects.
                self.buttons = [
                        PencilButton(self, [50,200]),
                        EraserButton(self, [50,200+y_interval]),
                        PaintBucketButton(self, [50,200+y_interval*2]),
                        DropperButton(self, [50,200+y_interval*3]),
                        LineButton(self, [50, 200+y_interval*4]),
                        ColorWheelButton(self, [50,200+y_interval*5]),

                        UnfilledRectButton(self, [50+x_interval, 250]),
                        FilledRectButton(self, [50+x_interval, 250+y_interval]),
                        UnfilledEllipseButton(self, [50+x_interval, 250+y_interval*2]),
                        FilledEllipseButton(self, [50+x_interval, 250+y_interval*3]),

                        GuideButton(self, [50+x_interval, 250+y_interval*4]),

                        StickerButton(self, [self.WS[0]-150, 125], "images/poto.png"),
                        StickerButton(self, [self.WS[0]-150, 125+y_interval], "images/poto_joy.png"),
                        StickerButton(self, [self.WS[0]-150, 125+y_interval*2], "images/poto_evil.png"),
                        StickerButton(self, [self.WS[0]-150, 125+y_interval*5], "images/poto_dizzy.png"),
                        StickerButton(self, [self.WS[0]-150, 125+y_interval*3], "images/poto_sleepy.png"),
                        StickerButton(self, [self.WS[0]-150, 125+y_interval*4], "images/poto_cookie.png"),
                ]

                self.filebuttonX = 400+110 # basic variable used to increment the x pos of filebuttons
                # starts off with the filebutton of the empty canvas
                self.filebuttons = [FileButton(self, (400, 25), self.canvas.image, self.canvas.undo_history, self.canvas.redo_history, 0, self.canvas.save_path)]

                self.guide_page = pygame.image.load("images/guide_page.png").convert_alpha()
                self.showing_guide = True
                self.guide_start = 0 # stores the exact time that the guide started showing. used to delay the checking of input that will close the guide.

        def run(self):
                while True:
                        # event checker
                        for event in pygame.event.get():
                                if event.type == pygame.QUIT:
                                        pygame.quit()
                                        sys.exit()

                                if event.type == pygame.WINDOWRESIZED:
                                        # if the window was resized, then update our WS variable
                                        self.WS = pygame.display.get_window_size()

                                if self.showing_guide: # in the case that we're showing the guide, we don't want to interact with buttons.
                                        if event.type not in [1026, 1024] and event.type < 30000: # we got an event.
                                                # print(event.type)
                                                if pygame.time.get_ticks() - self.guide_start >= 250:
                                                        self.showing_guide = False
                                                break # break is called no matter what to avoid the interaction of buttons below

                                if event.type == pygame.KEYDOWN:
                                        self.holding.add(event.key)

                                        if event.key == pygame.K_z: # handles redo
                                                if pygame.K_LCTRL in self.holding or pygame.K_RCTRL in self.holding:
                                                        self.canvas.undo_interval = 600 # sets the interval (see canvas.py for how this is used.)
                                                        self.canvas.undo()
                                        if event.key == pygame.K_y: # handles redo
                                                if pygame.K_LCTRL in self.holding or pygame.K_RCTRL in self.holding:
                                                        self.canvas.redo_interval = 600 # sets the interval (see canvas.py for how this is used.)
                                                        self.canvas.redo()
                                        if event.key == pygame.K_s: # handles saving a file
                                                if pygame.K_LCTRL in self.holding or pygame.K_RCTRL in self.holding:
                                                        if pygame.K_LSHIFT in self.holding or pygame.K_RSHIFT in self.holding:
                                                                self.canvas.save(True) # the true means we want to save as a new file no matter if we already saved it as a file.
                                                        else: self.canvas.save()
                                        if event.key == pygame.K_o: # handles opening a file
                                                if pygame.K_LCTRL in self.holding or pygame.K_RCTRL in self.holding:
                                                        self.canvas.load()
                                        if event.key == pygame.K_n: # handles making a new file with custom canvas size
                                                if (pygame.K_LCTRL in self.holding or pygame.K_RCTRL in self.holding) \
                                                                and (pygame.K_LSHIFT in self.holding or pygame.K_RSHIFT in self.holding):
                                                                        prompt = tkinter.simpledialog.askstring(title="New Canvas", prompt="Enter width and height separated by a comma (no spaces please!)")
                                                                        # try and except is put here in case user entered unusable info.
                                                                        try:
                                                                                width, height = map(int, prompt.split(","))
                                                                                # checks that both of the two are positive
                                                                                if width <= 0 or height <= 0: print("Invalid numbers.")
                                                                                else:
                                                                                        # make a new filebutton and add it to the list!
                                                                                        self.canvas.load_ID = len(self.filebuttons)
                                                                                        self.filebuttons.append(FileButton(self, (self.filebuttonX, 25), self.canvas.image, [], [], len(self.filebuttons), None))
                                                                                        self.filebuttonX += 110
                                                                                        self.canvas.load(self.filebuttons[self.canvas.load_ID].data)
                                                                                        self.canvas.__init__(self, self.WS, (width, height), initial=False)
                                                                        except Exception as e:
                                                                                print("Failed to complete operation: ", e)

                                        if event.key == pygame.K_x: # close the current file
                                                if len(self.filebuttons) > 1:
                                                        # shift the ID's past this one down
                                                        for i in range(self.canvas.load_ID, len(self.filebuttons)):
                                                                self.filebuttons[i].data[3] -= 1

                                                        self.filebuttons.pop(self.canvas.load_ID) # removing the one we don't need anymore

                                                        self.canvas.load(self.filebuttons[0].data, removed=True)

                                                        # update all the positions
                                                        self.filebuttonX = 400
                                                        for button in self.filebuttons:
                                                                button.pos = [self.filebuttonX, 25]
                                                                self.filebuttonX += 110

                                if event.type == pygame.KEYUP:
                                        if event.key in self.holding: self.holding.remove(event.key)

                                        if event.key == pygame.K_z: # stop undoing
                                                self.canvas.last_undo_tick = 0
                                        if event.key == pygame.K_y: # stop redoing
                                                self.canvas.last_redo_tick = 0

                                if event.type == pygame.MOUSEBUTTONDOWN:
                                        if event.button == 1: # LMB
                                                self.mb[0] = True
                                                # check if we should be interacting with a button
                                                flag = False
                                                for button in self.buttons + self.filebuttons:
                                                        if button.update(self.mp, self.mb): flag = True
                                                # otherwise, start drawing on canvas
                                                if not flag:
                                                        if pygame.K_SPACE in self.holding:
                                                                self.canvas.pan(self.mp)
                                                        if not self.busymb[0]:
                                                                self.canvas.drawing = True
                                                                self.canvas.redo_history.clear()
                                                                self.canvas.undo_history.insert(0, self.canvas.image.copy())
                                                                self.busymb[0] = True;
                                        if event.button == 2: # MMB
                                                self.mb[1] = True
                                                # pan the canvas
                                                if not self.busymb[1]:
                                                        self.canvas.pan(self.mp)
                                        if event.button == 3: # RMB
                                                self.mb[2] = True

                                        # ZOOMING
                                        if not pygame.K_LCTRL in self.holding and not pygame.K_RCTRL in self.holding:
                                                # When we zoom in, the scale of the canvas is changed by the zoom percent upwards or downwards.
                                                # distsave and proportion is used to zoom in at where the mouse is, and zoom out where the mouse is.
                                                # the distance from the canvas pos to the mouse pos is proportionate when scaling, so we can use this to calculate
                                                # what the new canvas position should be.
                                                if event.button == 4:
                                                        new_scale = self.canvas.scale * self.ZOOM_PERCENT[1]
                                                        if self.canvas.width * new_scale <= self.WS[0]*2 or self.canvas.height * new_scale <= self.WS[1]*2:
                                                                distsave = [self.mp[0] - self.canvas.pos[0], self.mp[1] - self.canvas.pos[1]]
                                                                proportion = self.canvas.scale / new_scale
                                                                self.canvas.scale = new_scale
                                                                self.canvas.scale = round(self.canvas.scale, 2)
                                                                self.canvas.pos = [self.mp[0] - (distsave[0] / proportion), self.mp[1] - (distsave[1] / proportion)]
                                                if event.button == 5:
                                                        new_scale = self.canvas.scale * self.ZOOM_PERCENT[0]
                                                        if (self.canvas.width * new_scale >= 40 and self.canvas.height * new_scale >= 40) and new_scale > 0:
                                                                distsave = [self.mp[0] - self.canvas.pos[0], self.mp[1] - self.canvas.pos[1]]
                                                                proportion = self.canvas.scale / new_scale
                                                                self.canvas.scale = new_scale
                                                                self.canvas.scale = round(self.canvas.scale, 2)
                                                                self.canvas.pos = [self.mp[0] - (distsave[0] / proportion), self.mp[1] - (distsave[1] / proportion)]
                                        # BRUSH RESIZING
                                        else:
                                                # using the built in function from the canvas object to set brush size bigger or smaller
                                                if event.button == 4:
                                                        self.canvas.set_brush(None if not self.canvas.brush_mode == "eraser" else (255,255,255), min(100, self.canvas.brush_size+1))
                                                if event.button == 5:
                                                        self.canvas.set_brush(None if not self.canvas.brush_mode == "eraser" else (255,255,255), max(1, self.canvas.brush_size-1))

                                if event.type == pygame.MOUSEBUTTONUP: # update the mb variables that the other objects use to function right
                                        if event.button == 1:
                                                self.mb[0] = False
                                                self.busymb[0] = False
                                        if event.button == 2:
                                                self.mb[1] = False
                                                self.busymb[1] = False
                                        if event.button == 3:
                                                self.mb[2] = False
                                                self.busymb[2] = False

                        self.mp = pygame.mouse.get_pos()

                        self.display.fill((25,24,31))

                        ## DRAW AND UPDATE
                        # using built in functions of canvas and buttons
                        self.canvas.update(self.mp, self.mb)
                        self.canvas.render(self.display, self.mp)

                        for button in self.buttons + self.filebuttons:
                                button.update(self.mp, self.mb)
                                button.render(self.display)
                        ##

                        # draw the brush preview in the bottom right. it's scaled by the canvas object.
                        color_preview = self.canvas.brush_img
                        if color_preview.get_width() < 25:
                                color_preview = pygame.transform.scale(color_preview, (25,25))
                        self.display.blit(color_preview, (self.WS[0] - color_preview.get_width()-25, self.WS[1] - color_preview.get_height()-25))
                        self.display.blit(self.title_img, (15,20))

                        if self.showing_guide:
                                self.display.blit(self.guide_page, (300,125))

                        pygame.display.flip()

# make an instance of the program and run it
if __name__ == "__main__":
        Paley().run()