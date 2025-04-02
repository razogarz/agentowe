from mesa.space import MultiGrid


class Grid(MultiGrid):
    def __init__(
            self,
            width=750,
            height=750,
            torus=True,
            grass_grow_prob=0.1,
            size_cluster_prey=10,
            size_cluster_predator=10
    ):
        super().__init__(width, height, torus=torus)
        self.grass_grow_prob = grass_grow_prob
        self.size_cluster_prey = size_cluster_prey
        self.size_cluster_predator = size_cluster_predator

    def place_agents(self, agents):
        for agent in agents:
            self.place_agent(agent)

