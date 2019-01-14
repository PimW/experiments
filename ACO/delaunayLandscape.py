import math
import pygame

import landscape
from delaunay2D import Delaunay2D


class DelaunayLandscape(landscape.Landscape):
    def __init__(self, landscape_size=400, area=(100, 100)):
        super().__init__(landscape_size, area)

    def generate_landscape(self):
        delaunay = Delaunay2D(center=(self.area[0]/2, self.area[1]/2), radius=70)
        for point in self.points:
            delaunay.addPoint(point)
        triangles = delaunay.exportTriangles()

        for triangle in triangles:
            edge1 = (triangle[0], triangle[1])
            edge2 = (triangle[1], triangle[2])
            edge3 = (triangle[0], triangle[2])
            self.edges.add(edge1)
            self.edges.add(edge2)
            self.edges.add(edge3)


if __name__ == "__main__":
    landscape = DelaunayLandscape()
    landscape.simulate()
