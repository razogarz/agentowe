import random
from models.agents.base_agent import Animal
from models.config import (
    PREDATOR_INIT_ENERGY,
    PREDATOR_MAX_ENERGY,
    PREDATOR_HUNGER_LEVELS,
    PREDATOR_BREEDING_ENERGY_THRESHOLD,
    PREDATOR_BREEDING_CHANCE,
    PREDATOR_BREEDING_ENERGY_COST,
    PREDATOR_OFFSPRING_ENERGY_FACTOR,
    PREDATOR_BREEDING_COOLDOWN,
    PREDATOR_PREY_ENERGY_VALUE
)

class Predator(Animal):
    """Predator agent that hunts herbivores and reproduces"""
    
    def __init__(self, model, energy=PREDATOR_INIT_ENERGY, max_energy=PREDATOR_MAX_ENERGY):
        super().__init__(model, energy, max_energy)
        self.is_predator = True
        self.breeding_cooldown = 0
    
    def step(self):
        """Perform one step of predator behavior"""
        try:
            # Update breeding cooldown
            if self.breeding_cooldown > 0:
                self.breeding_cooldown -= 1
            
            # Increment hunger counter
            self.steps_without_food += 1
            
            # Apply hunger effects with predator's hunger levels
            if not self.reduce_energy(PREDATOR_HUNGER_LEVELS):
                return  # Animal died of starvation
            
            # Try to hunt prey
            prey_found = self.hunt()
            
            # Move if no prey was found
            if not prey_found:
                self.move()
            
            # Try to reproduce if conditions are met
            if (self.energy > self.max_energy * PREDATOR_BREEDING_ENERGY_THRESHOLD and 
                    self.breeding_cooldown == 0 and 
                    random.random() < PREDATOR_BREEDING_CHANCE):
                self.reproduce()
                
        except Exception as e:
            print(f"Predator step error: {e}")
    
    def hunt(self):
        """Try to find and eat herbivores in the current cell"""
        if not self._check_position():
            return False
            
        try:
            # Check current cell for herbivores
            cell_content = self.model.grid.get_cell_list_contents([self.pos])
            for agent in cell_content:
                if hasattr(agent, 'is_herbivore') and agent.is_herbivore:
                    # Eat the herbivore
                    self.energy += PREDATOR_PREY_ENERGY_VALUE
                    self.energy = min(self.energy, self.max_energy)
                    self.steps_without_food = 0  # Reset hunger
                    
                    # Remove the eaten herbivore
                    self.model.grid.remove_agent(agent)
                    return True
            
            # No prey found in current cell
            return False
        except Exception as e:
            print(f"Hunt error: {e}")
            return False
    
    def move(self):
        """Move toward prey if visible, otherwise move randomly"""
        if not self._check_position():
            return
            
        try:
            # Get neighboring cells
            neighbors = self.get_neighbors()
            
            if not neighbors:
                return
                
            # Look for cells with prey
            prey_cells = []
            for cell in neighbors:
                cell_content = self.model.grid.get_cell_list_contents([cell])
                if any(hasattr(agent, 'is_herbivore') for agent in cell_content):
                    prey_cells.append(cell)
            
            # If prey spotted, move toward it
            if prey_cells:
                target_cell = random.choice(prey_cells)
                if self.move_to(target_cell):
                    # Try to hunt immediately after moving
                    self.hunt()
            else:
                # Random movement if no prey spotted
                self.random_move()
                
        except Exception as e:
            print(f"Move error: {e}")
    
    def reproduce(self):
        """Create a new predator with breeding cooldown"""
        try:
            # Calculate energy distribution
            original_energy = self.energy
            self.energy *= PREDATOR_BREEDING_ENERGY_COST  # Parent keeps 50% energy
            
            # Offspring energy calculation 
            offspring_energy = original_energy * PREDATOR_OFFSPRING_ENERGY_FACTOR
            
            # Reset breeding cooldown
            self.breeding_cooldown = PREDATOR_BREEDING_COOLDOWN
            
            # Create baby predator
            baby = Predator(self.model, energy=offspring_energy)
            
            # Find place for baby and place it
            self.place_offspring(baby)
            
        except Exception as e:
            print(f"Reproduction error: {e}") 