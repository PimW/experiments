import random
import time

import pygame

from display import Display

from colony import AntColony


class Landscape(object):
    def __init__(self, landscape_size=100, area=(100, 100), colony_count=4, food_count=10):
        self.points = []
        self.adjacency_list = {}
        self.edges = set()
        self.colonies = []
        self.foods = {}
        self.area = area

        self.distance_matrix = []
        self.network_points = []

        self.generate_points(landscape_size, area)
        self.calculate_distance_matrix()

        self.display = Display()

        self.generate_landscape()
        self.create_adjacency_list()

        self.generate_colonies(colony_count)
        self.generate_food(food_count)

    def generate_landscape(self):
        raise NotImplementedError()

    def generate_colonies(self, colony_count):
        pheromone_colors = [
            (255,0,0),
            (0,255,0),
            (0,0,255),
            (127,127,0)
        ]
        while len(self.colonies) < colony_count:
            colony_pos = random.randint(0, len(self.points))
            if colony_pos not in self.foods:
                self.colonies.append(AntColony(self, colony_pos, pheromone_color=pheromone_colors[len(self.colonies)]))

    def generate_food(self, food_count):
        for i in range(food_count):
            self.foods[i] = 2000

    def create_empty_matrix(self, size):
        matrix = []
        for x in range(size[0]):
            row = []
            for y in range(size[1]):
                row.append(0)
            matrix.append(row)
        return matrix

    def generate_points(self, landscape_size, area):
        while len(self.points) < landscape_size:
            new_point = (random.randint(0, area[0]), random.randint(0, area[1]))
            if new_point not in self.points:
                self.points.append(new_point)

    def calculate_distance_matrix(self):
        self.distance_matrix = self.create_empty_matrix((len(self.points), len(self.points)))
        for x, point_a in enumerate(self.points):
            for y, point_b in enumerate(self.points):
                self.distance_matrix[x][y] = self.distance(point_a, point_b)

    def create_adjacency_list(self):
        for edge in self.edges:
            # TODO: setting again is not necessary
            self.adjacency_list[edge[0]] = self.adjacency_list.get(edge[0], [])
            self.adjacency_list[edge[0]].append(edge[1])

            self.adjacency_list[edge[1]] = self.adjacency_list.get(edge[1], [])
            self.adjacency_list[edge[1]].append(edge[0])

    def distance(self, point_a, point_b):
        return ((point_a[0] - point_b[0])**2 + (point_a[1] - point_b[1])**2)**0.5

    def draw_points(self):
        self.display.draw_points(self.points, color=(50,50,50))

    def draw_colonies(self):
        for colony in self.colonies:
            self.display.draw_point(self.points[colony.position], point_color=colony.pheromone_color, point_size=10)

    def draw_foods(self):
        for idx in self.foods:
            food_ratio = (self.foods[idx]/2000.0)
            self.display.draw_point(self.points[idx], point_color=(0, 255*food_ratio, 0), point_size=5+round(3*food_ratio))

    def draw_pheromones(self):
        pass

    def draw_lines(self):
        for edge in self.edges:
            total_pheromone_level = 0
            partial_colors = [[], [], []]
            for colony in self.colonies:
                pheromone_level = colony.pheromone_matrix[edge]
                total_pheromone_level += pheromone_level
                for i in range(3):
                    component = max(255 - (pheromone_level * (255 - colony.pheromone_color[i])), 0)
                    partial_colors[i].append(component)

            edge_color = (
                min(partial_colors[0]), #/ (len(partial_colors[0])),
                min(partial_colors[1]), #/ (len(partial_colors[1])),
                min(partial_colors[2]) #/ (len(partial_colors[2]))
            )

            self.display.draw_line(
                self.points[edge[0]],
                self.points[edge[1]],
                color=edge_color,
                line_width=round(1+total_pheromone_level*6)
            )

    def draw(self):
        with self.display:
            self.draw_lines()
            self.draw_points()

            self.draw_colonies()
            self.draw_foods()
            self.draw_pheromones()

    def simulate_population(self):
        for colony in self.colonies:
            colony.optimize()
        for colony in self.colonies:
            colony.update_pheromones()

    def simulate(self):
        count = 0
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: exit()
            self.simulate_population()
            self.draw()
            print("Iteration: {0}".format(count))
            count += 1

    def get_possible_paths(self, current_location):
        try:
            return self.adjacency_list[current_location]
        except KeyError as e:
            print(e)
            print(self.adjacency_list)
            raise

if __name__ == "__main__":
    landscape = Landscape()

    input()
