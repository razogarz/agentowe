import mesa

from models.agents.herbivore import Herbivore, Grass


class PPModel(mesa.Model):
    def __init__(
            self,
            initial_herbivores=30,
            max_energy_prey=100,
            age_interbreed_prey=10,
            max_speed_prey=5,
            energy_grass=20,
            reproduction_threshold_prey=15,
            width=75,
            height=75,
            seed=None
    ):
        # Setup simulation
        super().__init__(seed=seed)
        self.num_agents = initial_herbivores
        self.grid = mesa.space.MultiGrid(width, height, True)

        # Simulation parameters
        self.max_energy_prey = max_energy_prey
        self.age_interbreed_prey = age_interbreed_prey
        self.max_speed_prey = max_speed_prey
        self.energy_grass = energy_grass
        self.reproduction_threshold_prey = reproduction_threshold_prey

        # Create agents
        agents = Herbivore.create_agents(self, initial_herbivores)

        x = self.rng.integers(0, self.grid.width, size=(initial_herbivores,))
        y = self.rng.integers(0, self.grid.height, size=(initial_herbivores,))
        for a, i, j in zip(agents, x, y):
            self.grid.place_agent(a, (i, j))

        # Datacollector
        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Herbivore": lambda m: m.num_agents,
            },
            agent_reporters={
                "Energy": "energy",
                "Age": "age",
            },
        )

    def grow_grass(self):
        has_grass_grown = self.rng.random() < 0.35
        if has_grass_grown:
            grass = Grass.create_agents(self, 2)
            x = self.rng.integers(0, self.grid.width, size=(2,))
            y = self.rng.integers(0, self.grid.height, size=(2,))
            for g_a, i, j in zip(grass, x, y):
                self.grid.place_agent(g_a, (i, j))

    def step(self):
        self.datacollector.collect(self)
        self.agents.shuffle_do("step")
        self.grow_grass()
