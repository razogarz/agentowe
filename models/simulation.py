import mesa

from models.agents.herbivore import Herbivore
from models.agents.carnivore import Carnivore
from models.grid import Grid


class PPModel(mesa.Model):
    def __init__(
            self,
            initial_herbivores=100,
            initial_carnivores=50,
            max_energy_prey=100,
            max_energy_predator=150,
            age_interbreed_prey=10,
            age_interbreed_predator=15,
            max_speed_prey=5,
            max_speed_predator=7,
            energy_grass=20,
            energy_meat=50,
            seed=None
    ):
        super().__init__(seed=seed)
        herbivores = Herbivore.create_agents(self, initial_herbivores)
        carnivores = Carnivore.create_agents(self, initial_carnivores)

        self.max_energy_prey = max_energy_prey
        self.max_energy_predator = max_energy_predator
        self.age_interbreed_prey = age_interbreed_prey
        self.age_interbreed_predator = age_interbreed_predator
        self.max_speed_prey = max_speed_prey
        self.max_speed_predator = max_speed_predator
        self.energy_grass = energy_grass
        self.energy_meat = energy_meat


    def step(self):
        steps = self.agents.shuffle_do("step")

        for s in range(len(steps)):

