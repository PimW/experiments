import random


class AntColony(object):
    colony_positions = []

    def __init__(self, landscape, position, colony_size=30, base_food=2000, base_probability=0.05, pheromone_per_ant=0.2, pheromone_decay=0.005, pheromone_color=(255,0,0)):
        self.position = position
        AntColony.colony_positions.append(self.position)

        self.colony_size = colony_size
        self.base_probability = base_probability
        self.pheromone_per_ant = pheromone_per_ant
        self.pheromone_decay = pheromone_decay
        self.pheromone_color = pheromone_color

        self.landscape = landscape

        self.pheromone_matrix = {}
        self.new_pheromone_matrix = {}

        self.ants = []
        self.food_count = base_food
        self.delta_food_count = 0

        self.initialize_pheromones()
        self.generate_ants()

    def create_empty_pheromones(self):
        pheromone_matrix = {}

        for edge in self.landscape.edges:
            pheromone_matrix[edge] = 0
            pheromone_matrix[(edge[1], edge[0])] = 0

        return pheromone_matrix

    def initialize_pheromones(self):
        self.pheromone_matrix = self.create_empty_pheromones()

    def clear_pheromones(self):
        self.new_pheromone_matrix = self.create_empty_pheromones()

    def generate_ants(self):
        self.ants = []
        for i in range(self.colony_size):
            self.ants.append([])

    def optimize(self):
        self.create_new_population()

    def create_new_population(self):
        old_food_count = self.food_count
        self.generate_ants()
        self.clear_pheromones()
        for ant in self.ants:
            steps = 0
            current_position = self.position
            ant.append(current_position)
            while current_position not in self.landscape.foods:
                if steps >= 200:
                    break

                possible_paths = self.landscape.get_possible_paths(current_position)

                next_position = self.pick_path(current_position, possible_paths)

                if len(ant) > 1 and next_position == ant[-2]:  # don't walk back
                    continue
                if next_position in ant:
                    subant = ant[:ant.index(next_position)]
                    ant = subant
                ant.append(next_position)
                current_position = next_position
                steps += 1

            if steps >= 200:
                break

            self.landscape.foods[current_position] -= 1
            self.food_count += 1

            if self.landscape.foods[current_position] == 0:
                del self.landscape.foods[current_position]

                new_food_position = random.randint(0, len(self.landscape.points)-1)
                while new_food_position in AntColony.colony_positions or new_food_position in self.landscape.foods:
                    new_food_position = random.randint(0, len(self.landscape.points)-1)
                self.landscape.foods[new_food_position] = 2000

            self.update_ant_pheromones(ant)
        self.delta_food_count = old_food_count - self.food_count

    def pick_path(self, current_position, possible_paths):
        total_pheromones = 0
        for next_position in possible_paths:
            try:
                total_pheromones += self.base_probability + self.pheromone_matrix[(current_position, next_position)]
            except:
                print("Pheromones: ",  self.pheromone_matrix)
                raise
        choice = random.random()
        stop_at = choice * total_pheromones

        pheromones = 0
        for next_position in possible_paths:
            if pheromones >= stop_at:
                return next_position

            pheromones += self.base_probability + self.pheromone_matrix[(current_position, next_position)]

        return possible_paths[-1]

    def update_ant_pheromones(self, ant):
        total_path_length = self.path_length(ant)
        for idx, pos in enumerate(ant[:-1]):
            next_pos = ant[idx + 1]
            try:
                self.new_pheromone_matrix[(pos, next_pos)] += self.pheromone_per_ant/total_path_length
                self.new_pheromone_matrix[(next_pos, pos)] += self.pheromone_per_ant/total_path_length
            except KeyError as e:
                print(e)
                print(ant)
                raise

    def path_length(self, ant):
        total_path_length = 0
        for idx, pos in enumerate(ant[:-1]):
            next_pos = ant[idx + 1]
            total_path_length += self.landscape.distance_matrix[pos][next_pos]
        return total_path_length

    def update_pheromones(self):
        for edge in self.pheromone_matrix:
            old_pheromones = min(self.pheromone_matrix[edge], 1)
            added_pheromones = min(self.new_pheromone_matrix[edge], 1)
            new_pheromone_count = old_pheromones * (1-self.pheromone_decay) + added_pheromones

            self.pheromone_matrix[edge] = new_pheromone_count
            self.pheromone_matrix[(edge[1], edge[0])] = new_pheromone_count