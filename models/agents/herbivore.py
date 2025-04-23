import mesa
import random
from models.agents.base_agent import Animal
from models.config import (
    HERBIVORE_INIT_ENERGY, 
    HERBIVORE_MAX_ENERGY,
    HERBIVORE_HUNGER_LEVELS,
    HERBIVORE_ENERGY_LOSS_CHANCE,
    HERBIVORE_BREEDING_ENERGY_THRESHOLD,
    HERBIVORE_BREEDING_CHANCE,
    HERBIVORE_BREEDING_ENERGY_COST,
    HERBIVORE_OFFSPRING_ENERGY_FACTOR,
    GRASS_ENERGY_VALUE
)

# Simple Grass class
class Grass(mesa.Agent):
    def __init__(self, model):
        super().__init__(model)
        self.is_grass = True
        
    def step(self):
        # Very simple growth - rare chance to spread to neighbor
        if random.random() < 0.05:
            try:
                # Try to get neighbors
                if hasattr(self, "pos") and self.pos is not None:
                    neighbors = self.model.grid.get_neighborhood(
                        self.pos, moore=True, include_center=False)
                    if neighbors:
                        # Choose a random neighbor cell
                        new_pos = random.choice(neighbors)
                        # Check if it's empty
                        cell_content = self.model.grid.get_cell_list_contents([new_pos])
                        if not any(hasattr(a, 'is_grass') for a in cell_content):
                            # Create and place new grass
                            new_grass = Grass(self.model)
                            self.model.grid.place_agent(new_grass, new_pos)
                            # Don't try to use scheduler
            except Exception as e:
                print(f"Grass growth error: {e}")

class Herbivore(Animal):
    """Herbivore agent that eats grass and can reproduce"""
    
    def __init__(self, model, energy=HERBIVORE_INIT_ENERGY, max_energy=HERBIVORE_MAX_ENERGY):
        super().__init__(model, energy, max_energy)
        self.is_herbivore = True
    
    def step(self):
        """Perform one step of the herbivore's behavior"""
        try:
            # Increment hunger counter
            self.steps_without_food += 1
            
            # Apply hunger effects with configurable levels
            hunger_levels = list(HERBIVORE_HUNGER_LEVELS)
            
            # Special case for the lowest hunger level which has a random chance
            if self.steps_without_food <= hunger_levels[-1][0] and random.random() >= HERBIVORE_ENERGY_LOSS_CHANCE:
                # Skip energy loss this turn (80% chance when not very hungry)
                pass
            else:
                # Apply standard energy reduction based on hunger level
                if not self.reduce_energy(hunger_levels):
                    return  # Animal died of starvation
            
            # Move randomly
            self.random_move()
            
            # Try to eat grass
            self.eat_grass()
            
            # Try to reproduce if energy is high enough
            if self.energy > self.max_energy * HERBIVORE_BREEDING_ENERGY_THRESHOLD:
                if random.random() < HERBIVORE_BREEDING_CHANCE:
                    self.reproduce()
                    
        except Exception as e:
            print(f"Herbivore step error: {e}")
    
    def eat_grass(self):
        """Look for grass in the current cell and eat it if found"""
        if not self._check_position():
            return
            
        try:
            cell_content = self.model.grid.get_cell_list_contents([self.pos])
            for agent in cell_content:
                if hasattr(agent, 'is_grass') and agent.is_grass:
                    # Eat the grass
                    self.energy += GRASS_ENERGY_VALUE
                    self.energy = min(self.energy, self.max_energy)
                    self.model.grid.remove_agent(agent)
                    self.steps_without_food = 0  # Reset hunger counter
                    break
        except Exception as e:
            print(f"Eat error: {e}")
    
    def reproduce(self):
        """Create a new herbivore and place it nearby"""
        try:
            # Calculate energy distribution
            original_energy = self.energy
            self.energy *= HERBIVORE_BREEDING_ENERGY_COST  # Parent keeps 50% energy
            offspring_energy = original_energy * HERBIVORE_BREEDING_ENERGY_COST * HERBIVORE_OFFSPRING_ENERGY_FACTOR
            
            # Create a new herbivore
            baby = Herbivore(self.model, energy=offspring_energy)
            
            # Find place for baby and place it
            self.place_offspring(baby)
            
        except Exception as e:
            print(f"Reproduction error: {e}")

