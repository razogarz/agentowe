import mesa
import random

class Animal(mesa.Agent):
    """Base class for all animals in the simulation"""
    
    def __init__(self, model, energy, max_energy):
        super().__init__(model)
        self.energy = energy
        self.max_energy = max_energy
        self.steps_without_food = 0
    
    def _check_position(self):
        """Check if the agent has a valid position on the grid"""
        return hasattr(self, "pos") and self.pos is not None
    
    def get_neighbors(self, include_center=False):
        """Get neighboring cells if the agent has a valid position"""
        if not self._check_position():
            return []
            
        try:
            return self.model.grid.get_neighborhood(
                self.pos, moore=True, include_center=include_center)
        except Exception as e:
            print(f"Error getting neighbors: {e}")
            return []
    
    def move_to(self, new_pos):
        """Move the agent to a new position"""
        if not self._check_position() or not new_pos:
            return False
            
        try:
            self.model.grid.move_agent(self, new_pos)
            return True
        except Exception as e:
            print(f"Move error: {e}")
            return False
    
    def random_move(self):
        """Move randomly to a neighboring cell"""
        neighbors = self.get_neighbors()
        if neighbors:
            new_pos = random.choice(neighbors)
            return self.move_to(new_pos)
        return False
    
    def die(self):
        """Remove the agent from the grid when it dies"""
        if self._check_position():
            try:
                self.model.grid.remove_agent(self)
            except Exception as e:
                print(f"Death error: {e}")
    
    def reduce_energy(self, hunger_levels):
        """Reduce energy based on hunger levels
        
        Args:
            hunger_levels: List of tuples (threshold, energy_loss)
                in decreasing order of threshold
        """
        for threshold, energy_loss in hunger_levels:
            if self.steps_without_food > threshold:
                self.energy -= energy_loss
                break
                
        # Check if the animal dies from starvation
        if self.energy <= 0:
            self.die()
            return False
        return True

    def place_offspring(self, offspring):
        """Find a place for the offspring near the parent"""
        if not self._check_position():
            return False
            
        try:
            neighbors = self.get_neighbors(include_center=True)
            if neighbors:
                baby_pos = random.choice(neighbors)
                self.model.grid.place_agent(offspring, baby_pos)
                return True
        except Exception as e:
            print(f"Placing offspring error: {e}")
        
        return False 