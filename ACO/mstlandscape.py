import landscape


class MSTLandscape(landscape.Landscape):
    def __init__(self, landscape_size=400, area=(100,100)):
        super().__init__(landscape_size, area)
        self.network_points = []
        self.generate_mst_network()

    def generate_mst_network(self):
        self.tree_points = [0]

        while len(self.tree_points) < len(self.points):
            (tree_point, closest_point) = self.find_closest_point_to_tree()
            self.tree_points.append(closest_point)
            self.edges.append((tree_point, closest_point))
            self.display.draw_line(self.points[tree_point], self.points[closest_point])

    def find_closest_point_to_tree(self):
        min_distance = (self.area[0]**2 + self.area[1]**2)**0.5
        min_tree_idx = -1
        min_idx = -1
        for point in self.tree_points:
            (idx, distance) = self.find_closest_point_to_point(point)
            if distance < min_distance and idx not in self.tree_points:
                min_distance = distance
                min_idx = idx
                min_tree_idx = point
        return (min_tree_idx, min_idx)

    def find_closest_point_to_point(self, point):
        min_distance = (self.area[0]**2 + self.area[1]**2)**0.5
        min_idx = -1
        for idx in range(len(self.points)):
            if idx in self.tree_points:
                continue
            if self.matrix[point][idx] < min_distance:
                min_idx = idx
                min_distance = self.matrix[point][idx]
        return (min_idx, min_distance)

if __name__ == "__main__":
    landscape = MSTLandscape()

    input()