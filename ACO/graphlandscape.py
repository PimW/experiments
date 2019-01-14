import math

import landscape


class GraphLandscape(landscape.Landscape):
    def __init__(self, landscape_size=400, area=(100, 100)):
        super().__init__(landscape_size, area)
        self.network_points = []
        self.generate_planar_network()

    def generate_planar_network(self):
        total_distances = []
        for distances in self.matrix:
            total_distances.extend(distances)
        sorted_distances = sorted(total_distances)
        cutoff_distance = sorted_distances[len(self.points) * int(len(self.points)**0.4)]

        for x, point_a in enumerate(self.points):
            for y, point_b in enumerate(self.points):
                if x == y:
                    continue
                if self.matrix[x][y] < cutoff_distance:
                    self.edges.append((x, y))
                    self.display.draw_line(self.points[x], self.points[y])

if __name__ == "__main__":
    landscape = GraphLandscape()

    input()