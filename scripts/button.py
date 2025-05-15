# button.py
# holds a lot of classes that inherit from button, which contains the basic functions like
# dragging of the buttons, the action, rendering, and stuff.

import pygame
import tkinter
import tkinter.colorchooser

# main button class
class Button:
        def __init__(self, program, icon, pos):
                self.program = program
                self.image = pygame.image.load("images/circle_button.png").convert_alpha()
                self.highlight_image = pygame.image.load("images/circle_button_highlight.png").convert_alpha()
                self.icon = icon

                self.width, self.height = self.image.get_size()

                self.pos = list(pos)
                self.hover = False
                self.drag = False
                self.drag_relation = [0, 0]
                self.highlight = False # makes the button yellow if true

        def update(self, mp, mb):
                # input delay to make sure the user doesn't do stuff they didn't want to
                if pygame.time.get_ticks() - self.program.input_delay < 200: return
                # make sure the button can't go off screen
                self.pos[0] = min(self.pos[0], self.program.WS[0] - self.width)
                self.pos[0] = max(self.pos[0], 0)
                self.pos[1] = min(self.pos[1], self.program.WS[1] - self.height)
                self.pos[1] = max(self.pos[1], 0)

                # calculate whether the mouse is currently on the button
                if mp[0] >= self.pos[0] and mp[0] - self.pos[0] <= self.width and \
                        mp[1] >= self.pos[1] and mp[1] - self.pos[1] <= self.height:
                                self.hover = True
                else: self.hover = False
                
                # we should begin dragging the button
                if self.hover and mb[2] and not self.drag and not self.program.busymb[2]:
                        self.program.busymb[2] = True
                        self.start_drag(mp)
                
                if self.drag:
                        self.pos = [mp[0] + self.drag_relation[0], mp[1] + self.drag_relation[1]]
                if not mb[2]: 
                        self.drag = False
                
                if mb[0] and self.hover and not self.program.busymb[0]:
                        self.action()

                if self.hover:
                        return True

                return False

        def start_drag(self, mp):
                # drag relation saves the distance from the button pos to mouse pos.
                # every time the mouse moves and we're still dragging, the button will follow by using this relation.
                self.drag_relation = [self.pos[0] - mp[0], self.pos[1] - mp[1]]
                self.drag = True

        def action(self): # this gets run when the button is pressed
                pass

        def render(self, surf): # render the button to the screen
                self.imagec = self.image.copy() # a copy of the image. I added this at some point just in case but it does nothing important.
                self.highlight_imagec = self.highlight_image.copy()
                self.imagec.blit(self.icon, (self.width/2 - self.icon.get_width()/2, self.height/2 - self.icon.get_height()/2))
                self.highlight_imagec.blit(self.icon, (self.width/2 - self.icon.get_width()/2, self.height/2 - self.icon.get_height()/2))
                surf.blit(self.imagec if not self.highlight else self.highlight_imagec, self.pos)

# all other buttons inherit the main button's properties

class FileButton(Button): # button that saves data on history, id, progress, and save file and stuff
        def __init__(self, program, pos, canvas_img, undo_history, redo_history, ID, save_file):
                # a tiny version of the canvas is used as the icon for the button.
                icon = pygame.transform.scale(canvas_img,(50,50))
                super().__init__(program, icon, pos)
                self.data = [canvas_img, undo_history, redo_history, ID, save_file]
        def action(self): 
                self.program.canvas.load(self.data)
        def update(self, mp, mb):
                flag = super().update(mp, mb)
                if self.program.canvas.load_ID == self.data[3]: self.highlight = True
                else: self.highlight = False
                return flag

class ColorWheelButton(Button):
        def __init__(self, program, pos):
                icon = pygame.image.load("images/color_wheel.png").convert_alpha()
                super().__init__(program, icon, pos)
        def action(self): 
                # ask user for a color and set the canvas's brush to the new color
                inputcolor = tkinter.colorchooser.askcolor(title="Choose color")[0]
                self.program.canvas.set_brush(inputcolor, self.program.canvas.brush_size)
                self.program.canvas.brush_color = inputcolor
                self.program.input_delay = pygame.time.get_ticks()

class PencilButton(Button):
        def __init__(self, program, pos):
                icon = pygame.image.load("images/pencil.png").convert_alpha()
                super().__init__(program, icon, pos)
        def action(self): 
                self.program.canvas.brush_mode = "pencil"
                self.program.canvas.set_brush(None, self.program.canvas.brush_size)
        def update(self, mp, mb):
                # the button will be highlighted under the right conditions.
                # this applies to all the other buttons that you would expect highlighted.
                flag = super().update(mp, mb)
                if self.program.canvas.brush_mode == "pencil": self.highlight = True
                else: self.highlight = False
                return flag

# the other buttons are pretty self explanatory, with all their own id strings, and icons and stuff.
# the buttons mostly don't actually do much by themself, just toggle the canvas's brush modes and more.

class PaintBucketButton(Button):
        def __init__(self, program, pos):
                icon = pygame.image.load("images/bucket.png").convert_alpha()
                super().__init__(program, icon, pos)
        def action(self): self.program.canvas.brush_mode = "bucket"
        def update(self, mp, mb):
                flag = super().update(mp, mb)
                if self.program.canvas.brush_mode == "bucket": self.highlight = True
                else: self.highlight = False
                return flag

class EraserButton(Button):
        def __init__(self, program, pos):
                icon = pygame.image.load("images/eraser.png").convert_alpha()
                super().__init__(program, icon, pos)
        def action(self): 
                self.program.canvas.brush_mode = "eraser"
                # the eraser is actually just a white brush... :P
                self.program.canvas.set_brush((255,255,255), self.program.canvas.brush_size)
        def update(self, mp, mb):
                flag = super().update(mp, mb)
                if self.program.canvas.brush_mode == "eraser": self.highlight = True
                else: self.highlight = False
                return flag

class DropperButton(Button):
        def __init__(self, program, pos):
                icon = pygame.image.load("images/dropper.png").convert_alpha()
                super().__init__(program, icon, pos)
        def action(self):
                self.program.canvas.brush_mode = "dropper"
        def update(self, mp, mb):
                flag = super().update(mp, mb)
                if self.program.canvas.brush_mode == "dropper": self.highlight = True
                else: self.highlight = False
                return flag
        

class LineButton(Button):
        def __init__(self, program, pos):
                icon = pygame.image.load("images/line.png").convert_alpha()
                super().__init__(program, icon, pos)
        def action(self):
                self.program.canvas.brush_mode = "line"
        def update(self, mp, mb):
                flag = super().update(mp, mb)
                if self.program.canvas.brush_mode == "line": self.highlight = True
                else: self.highlight = False
                return flag

class UnfilledRectButton(Button):
        def __init__(self, program, pos):
                icon = pygame.image.load("images/unfilled_rect.png").convert_alpha()
                super().__init__(program, icon, pos)
        def action(self):
                self.program.canvas.brush_mode = "unfilled_rect"
        def update(self, mp, mb):
                flag = super().update(mp, mb)
                if self.program.canvas.brush_mode == "unfilled_rect": self.highlight = True
                else: self.highlight = False
                return flag

class FilledRectButton(Button):
        def __init__(self, program, pos):
                icon = pygame.image.load("images/filled_rect.png").convert_alpha()
                super().__init__(program, icon, pos)
        def action(self):
                self.program.canvas.brush_mode = "filled_rect"
        def update(self, mp, mb):
                flag = super().update(mp, mb)
                if self.program.canvas.brush_mode == "filled_rect": self.highlight = True
                else: self.highlight = False
                return flag

class UnfilledEllipseButton(Button):
        def __init__(self, program, pos):
                icon = pygame.image.load("images/unfilled_ellipse.png").convert_alpha()
                super().__init__(program, icon, pos)
        def action(self):
                self.program.canvas.brush_mode = "unfilled_ellipse"
        def update(self, mp, mb):
                flag = super().update(mp, mb)
                if self.program.canvas.brush_mode == "unfilled_ellipse": self.highlight = True
                else: self.highlight = False
                return flag

class FilledEllipseButton(Button):
        def __init__(self, program, pos):
                icon = pygame.image.load("images/filled_ellipse.png").convert_alpha()
                super().__init__(program, icon, pos)
        def action(self):
                self.program.canvas.brush_mode = "filled_ellipse"
        def update(self, mp, mb):
                flag = super().update(mp, mb)
                if self.program.canvas.brush_mode == "filled_ellipse": self.highlight = True
                else: self.highlight = False
                return flag

class GuideButton(Button): # button that opens the guide
        def __init__(self, program, pos):
                icon = pygame.image.load("images/guide.png").convert_alpha()
                super().__init__(program, icon, pos)
        def action(self):
                self.program.showing_guide = True
                self.program.mb = [0,0,0]
                self.program.guide_start = pygame.time.get_ticks()
        def update(self, mp, mb):
                flag = super().update(mp, mb)
                return flag

class StickerButton(Button): # button that puts down stickers
        def __init__(self, program, pos, icon_path):
                icon = pygame.image.load(icon_path).convert_alpha()
                self.picture = icon.copy()
                icon = pygame.transform.scale(icon, (80,80))
                self.sticker_name = icon_path.split("/")[1]
                super().__init__(program, icon, pos)
        def action(self):
                self.program.canvas.brush_mode = "sticker"
                self.program.canvas.sticker_img = self.picture
                self.program.canvas.sticker_name = self.sticker_name
        def update(self, mp, mb):
                flag = super().update(mp, mb)
                if self.program.canvas.brush_mode == "sticker" and self.program.canvas.sticker_name == self.sticker_name: self.highlight = True
                else: self.highlight = False
                return flag