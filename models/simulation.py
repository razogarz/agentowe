import mesa
import numpy as np

from models.agents.grass import Grass
from models.agents.herbivore import Herbivore
from models.agents.predator import Predator
from models.config import (
    HERBIVORE_INIT_ENERGY, 
    HERBIVORE_MAX_ENERGY,
    PREDATOR_INIT_ENERGY,
    PREDATOR_MAX_ENERGY,
    GRASS_ENERGY_VALUE,
    PREDATOR_PREY_ENERGY_VALUE
)
from models.visualize_grid import visualize_grid


class PPModel(mesa.Model):
    def __init__(
            self,
            initial_herbivores=30,
            initial_predators=10,
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
            width=75,
            height=75,
            seed=None
    ):
        # Setup simulation
        super().__init__(seed=seed)
        self.num_herbivores = initial_herbivores
        self.num_predators = initial_predators
        self.grid = mesa.space.MultiGrid(width, height, True)
        self.width = width
        self.height = height

        # Simulation parameters
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

        # Create herbivores
        self.initialize_herbivores(initial_herbivores)
        
        # Create predators
        self.initialize_predators(initial_predators)
        
        # Create initial grass
        self.initialize_grass(initial_amount=width * height // 10)  # 10% of the grid has grass initially

        # Datacollector
        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Grass Coverage": self.compute_grass_coverage,
                "Herbivore Population": self.compute_herbivore_population,
                "Predator Population": self.compute_predator_population,
            }
        )

    def initialize_herbivores(self, count):
        """Create initial herbivores and place them on the grid"""
        for i in range(count):
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            herbivore = Herbivore(self, energy=self.random.randint(30, 70))
            self.grid.place_agent(herbivore, (x, y))
    
    def initialize_predators(self, count):
        """Create initial predators and place them on the grid"""
        for i in range(count):
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            predator = Predator(self, energy=self.random.randint(60, 100))
            self.grid.place_agent(predator, (x, y))
    
    def initialize_grass(self, initial_amount):
        """Create initial grass and place it on the grid"""
        for i in range(initial_amount):
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            grass = Grass(self)
            self.grid.place_agent(grass, (x, y))

    def grow_grass(self):
        """Grow new grass with some probability - adjusted for balance"""
        # Calculate current grass coverage as a percentage
        current_grass_coverage = self.compute_grass_coverage()
        
        # Adaptive grass growth - faster when grass is scarce, slower when plentiful
        if current_grass_coverage < 10:
            # Very little grass, grow more rapidly
            growth_chance = 0.4
            max_new_patches = 6
        elif current_grass_coverage < 20:
            # Moderate grass, normal growth
            growth_chance = 0.25
            max_new_patches = 3
        else:
            # Lots of grass, slow growth
            growth_chance = 0.15
            max_new_patches = 1
            
        # Try to grow grass based on current coverage
        if self.random.random() < growth_chance:
            num_new_grass = self.random.randint(1, max_new_patches)
            for _ in range(num_new_grass):
                # Try to find an empty spot for new grass
                # More attempts in sparse environments, fewer in dense ones
                max_tries = 5
                for _ in range(max_tries):
                    x = self.random.randrange(self.grid.width)
                    y = self.random.randrange(self.grid.height)
                    # Check if cell is empty of grass
                    cell_contents = self.grid.get_cell_list_contents([(x, y)])
                    if not any(isinstance(agent, Grass) for agent in cell_contents):
                        grass = Grass(self)
                        self.grid.place_agent(grass, (x, y))
                        break

    def step(self):
        """Execute one step of the model"""
        # Collect data
        self.datacollector.collect(self)
        
        # Process all agents
        all_agents = self.get_all_agents()
        self.random.shuffle(all_agents)  # Randomize order for fairness
        
        for agent in all_agents:
            if agent.pos is not None:  # Only process agents still on grid
                agent.step()
        
        # Grow new grass
        self.grow_grass()
    
    def get_all_agents(self):
        """Get all agents from the grid"""
        agent_list = []
        for contents, (x, y) in self.grid.coord_iter():
            agent_list.extend(contents)
        return agent_list
    
    def compute_grass_coverage(self):
        """Compute the percentage of grid covered by grass"""
        grass_count = sum(1 for agent in self.get_all_agents() if isinstance(agent, Grass))
        return (grass_count / (self.width * self.height)) * 100
    
    def compute_herbivore_population(self):
        """Count the number of herbivores"""
        return sum(1 for agent in self.get_all_agents() if isinstance(agent, Herbivore))
    
    def compute_predator_population(self):
        """Count the number of predators"""
        return sum(1 for agent in self.get_all_agents() if isinstance(agent, Predator))