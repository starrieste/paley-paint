import pygame

class Widget:
        def __init__(self, image_path, pos):
                self.image = pygame.image.load(image_path).convert()
                self.pos = pos

                self.hover = False

        def update(self, mp, mb):
                pass

class Docker:
        def __init__(self, program, color, pos):
                self.program = program
                self.pos = pos
                self.color = color
                self.width = 80
                self.og_width = 80
                self.image = pygame.Surface((self.width, self.program.WS[1]))
                self.image.fill(color)
                self.widgets = []

                self.widgets.append(Widget("images/color_wheel.png", self.pos))

                for i, widget in enumerate(self.widgets):
                        widget.pos = [self.pos[0] + 10, self.pos[1] + i * 10]

                self.grab = False
                self.og_pos = 0
                self.hover = False

        def check_grab(self, mp):
                if abs(mp[0] - (self.pos[0] + self.width)) <= 5:
                        self.grab = True
                        self.og_width = self.width
                        self.og_pos = mp[0]
        def ungrab(self): self.grab = False

        def update(self, mp, mb):
                if mp[0] - self.pos[0] <= self.width and mp[1] - self.pos[1] <= self.program.display.get_height() \
                        and mp[0] >= self.pos[0] and mp[1] >= self.pos[1]: self.hover = True
                else: self.hover = False
                if self.grab: self.width = max(60, self.og_width + mp[0] - self.og_pos)
                self.image = pygame.Surface((self.width, self.program.WS[1]))
                self.image.fill(self.color)


                for widget in self.widgets:
                        widget.update(mp, mb)

        def render(self, surf):
                surf.blit(self.image, self.pos)
                for widget in self.widgets:
                        surf.blit(widget.image, (self.pos[0] + widget.pos[0], self.pos[1] + widget.pos[1]))