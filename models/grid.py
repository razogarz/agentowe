from mesa.space import MultiGrid


class Grid(MultiGrid):
    def __init__(
            self,
            width=750,
            height=750,
            max_grass_per_cell=100,
            max_meat_per_cell=50,
            torus=True,
            grass_grow_prob=0.1,
            grass_grow_per_step=1,
            grass_grow_prob_from_adjacent=0.1,
            decrease_meat_prob=0.1,
            size_cluster_prey=10,
            size_cluster_predator=10
    ):
        super().__init__(width, height, torus=torus)
        self.max_grass_per_cell = max_grass_per_cell
        self.max_meat_per_cell = max_meat_per_cell
        self.grass_grow_prob = grass_grow_prob
        self.grass_grow_per_step = grass_grow_per_step
        self.grass_grow_prob_from_adjacent = grass_grow_prob_from_adjacent
        self.decrease_meat_prob = decrease_meat_prob
        self.size_cluster_prey = size_cluster_prey
        self.size_cluster_predator = size_cluster_predator


    def is_cell_empty(self, pos):
        x, y = pos
        return len(self[x][y]) == 0

    def place_agents(self, agents):
        for agent in agents:
            self.place_agent(agent)

