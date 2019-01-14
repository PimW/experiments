import sys
import pygame


class Display(object):
    def __init__(self, size=(900, 900)):
        pygame.init()
        self.size = size
        self.screen = pygame.display.set_mode(size)
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((127, 127, 127))
        self.clear()
        self.display()

    def __enter__(self):
        self.clear()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.display()

    def clear(self):
        self.screen.blit(self.background, (0, 0))

    def display(self):
        pygame.display.flip()

    def draw_points(self, points, color=(0, 0, 0), point_size=5):
        for point in points:
            self.draw_point(point, color, point_size)

    def draw_point(self, point, point_color=(0, 0, 0), point_size=5):
        pygame.draw.circle(self.screen, point_color, (point[0] * 8 + 50, point[1] * 8 + 50), point_size)

    def draw_line(self, point_a, point_b, color=(0, 0, 255), line_width=1):
        point_a = (point_a[0]*8 + 50, point_a[1]*8 + 50)
        point_b = (point_b[0] * 8 + 50, point_b[1] * 8 + 50)
        pygame.draw.line(self.screen, color, point_a, point_b, line_width)