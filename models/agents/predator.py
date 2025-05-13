import random
from models.agents.base_agent import Animal
from models.fuzzy_brain import PredatorBrain
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

# Import for type checking only, not at runtime to avoid circular imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models.agents.herbivore import Herbivore

class Predator(Animal):
    """Predator agent that hunts herbivores and reproduces"""
    
    def __init__(self, model, energy=PREDATOR_INIT_ENERGY, max_energy=PREDATOR_MAX_ENERGY):
        super().__init__(model, energy, max_energy)
        self.is_predator = True
        self.breeding_cooldown = 0
        self.brain = PredatorBrain()  # Initialize fuzzy brain
    
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
            
            # Get environmental inputs for the brain
            inputs = self._gather_inputs()
            
            # Get decision from fuzzy brain
            decision = self.brain.decide(inputs)
            
            # Execute the decision
            self._execute_decision(decision)
                
        except Exception as e:
            print(f"Predator step error: {e}")
    
    def _gather_inputs(self):
        """Gather environmental inputs for the fuzzy brain"""
        # Default values
        inputs = {
            "energy": self.energy / self.max_energy,  # Normalized energy
            "prey_proximity": 6,  # Default: no prey visible
            "prey_count": 0  # Default: no prey visible
        }
        
        if not self._check_position():
            return inputs
            
        try:
            # Get surrounding cells
            neighborhood = self.model.grid.get_neighborhood(
                self.pos, moore=True, include_center=False, radius=4)
                
            # Check for prey (herbivores)
            closest_prey_dist = float('inf')
            prey_count = 0
            
            for cell in neighborhood:
                cell_content = self.model.grid.get_cell_list_contents([cell])
                for agent in cell_content:
                    if hasattr(agent, 'is_herbivore') and agent.is_herbivore:
                        prey_count += 1
                        dist = self._calculate_distance(self.pos, cell)
                        closest_prey_dist = min(closest_prey_dist, dist)
            
            # Update prey proximity (convert to 0-6 scale, 0 = here, 6 = not visible)
            if closest_prey_dist != float('inf'):
                inputs["prey_proximity"] = min(6, closest_prey_dist)
            
            # Update prey count
            inputs["prey_count"] = prey_count
                
        except Exception as e:
            print(f"Predator input gathering error: {e}")
            
        return inputs
    
    def _calculate_distance(self, pos1, pos2):
        """Calculate Manhattan distance between two positions"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def _execute_decision(self, decision):
        """Execute the decision from the fuzzy brain"""
        # Handle hunting decision
        hunting = decision.get("hunting", "conserve")
        
        if hunting == "chase":
            # Aggressive chase - try to hunt immediately, then move
            if not self.hunt():
                self._chase_prey()
        elif hunting == "stalk":
            # Stealthy approach - move toward prey
            self._stalk_prey()
            # Try to hunt after moving
            self.hunt()
        else:  # conserve
            # Just move randomly to conserve energy
            self.random_move()
            # Still try to hunt if we happen to end up near prey
            self.hunt()
            
        # Handle breeding decision
        if decision.get("breed", False) and random.random() < PREDATOR_BREEDING_CHANCE and self.breeding_cooldown == 0:
            self.reproduce()
    
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
    
    def _chase_prey(self):
        """Aggressively move toward nearest prey"""
        if not self._check_position():
            return
            
        try:
            # Get nearby cells with larger radius for chasing
            neighborhood = self.model.grid.get_neighborhood(
                self.pos, moore=True, include_center=False, radius=3)
                
            # Look for cells with prey
            prey_cells = []
            prey_distances = {}
            
            for cell in neighborhood:
                cell_content = self.model.grid.get_cell_list_contents([cell])
                for agent in cell_content:
                    if hasattr(agent, 'is_herbivore') and agent.is_herbivore:
                        dist = self._calculate_distance(self.pos, cell)
                        prey_cells.append(cell)
                        prey_distances[cell] = dist
                        break  # Only need one herbivore per cell
            
            # If prey spotted, move toward the closest one
            if prey_cells:
                # Sort by distance
                closest_cells = sorted(prey_cells, key=lambda c: prey_distances[c])
                
                if closest_cells:
                    # Move to the closest prey cell or its neighbor
                    target_cell = closest_cells[0]
                    
                    # If we can move directly to the prey cell
                    if self._calculate_distance(self.pos, target_cell) == 1:
                        self.move_to(target_cell)
                    else:
                        # Otherwise, find the neighboring cell that brings us closer
                        immediate_neighbors = self.model.grid.get_neighborhood(
                            self.pos, moore=True, include_center=False)
                        
                        best_cell = None
                        best_distance = float('inf')
                        
                        for neighbor in immediate_neighbors:
                            dist_to_prey = self._calculate_distance(neighbor, target_cell)
                            if dist_to_prey < best_distance:
                                best_distance = dist_to_prey
                                best_cell = neighbor
                        
                        if best_cell:
                            self.move_to(best_cell)
                        else:
                            self.random_move()
                else:
                    self.random_move()
            else:
                # No prey spotted, random movement
                self.random_move()
                
        except Exception as e:
            print(f"Chase prey error: {e}")
    
    def _stalk_prey(self):
        """Stealthily move toward prey"""
        if not self._check_position():
            return
            
        try:
            # Similar to chase but with more careful movement
            neighborhood = self.model.grid.get_neighborhood(
                self.pos, moore=True, include_center=False, radius=2)
                
            # Look for cells with prey
            prey_cells = []
            for cell in neighborhood:
                cell_content = self.model.grid.get_cell_list_contents([cell])
                if any(hasattr(agent, 'is_herbivore') and agent.is_herbivore for agent in cell_content):
                    prey_cells.append(cell)
            
            # If prey spotted, move toward it cautiously
            if prey_cells:
                target_cell = random.choice(prey_cells)
                
                # Get immediate neighbors
                immediate_neighbors = self.model.grid.get_neighborhood(
                    self.pos, moore=True, include_center=False)
                
                # Find neighbor that brings us closer to prey
                best_cell = None
                best_distance = float('inf')
                
                for neighbor in immediate_neighbors:
                    dist_to_prey = self._calculate_distance(neighbor, target_cell)
                    if dist_to_prey < best_distance:
                        best_distance = dist_to_prey
                        best_cell = neighbor
                
                if best_cell:
                    self.move_to(best_cell)
                else:
                    self.random_move()
            else:
                # No prey spotted, random movement
                self.random_move()
                
        except Exception as e:
            print(f"Stalk prey error: {e}")
    
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