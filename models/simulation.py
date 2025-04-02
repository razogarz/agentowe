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
            reproduction_threshold_prey=15,
            reproduction_threshold_predator=20,
            seed=None
    ):
        super().__init__(seed=seed)

        self.max_energy_prey = max_energy_prey
        self.max_energy_predator = max_energy_predator
        self.age_interbreed_prey = age_interbreed_prey
        self.age_interbreed_predator = age_interbreed_predator
        self.max_speed_prey = max_speed_prey
        self.max_speed_predator = max_speed_predator
        self.energy_grass = energy_grass
        self.energy_meat = energy_meat
        self.reproduction_threshold_prey = reproduction_threshold_prey
        self.reproduction_threshold_predator = reproduction_threshold_predator

        herbivores = Herbivore.create_agents(self, initial_herbivores)
        carnivores = Carnivore.create_agents(self, initial_carnivores)

    def perception(self):
        self.agents.shuffle_do("perceive")

    def concept_computation(self):
        pass

    def action(self):
        pass

    def energy_update(self):
        pass

    def population_update(self):
        pass

    def resource_update(self):
        pass

    def aging(self):
        for agent in self.agents:
            agent.age += 1

    def step(self):
        steps = self.agents.shuffle_do("step")

