import mesa
import random
import math
from models.agents.base_agent import Animal
from models.fuzzy_brain import HerbivoreBrain
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

# Import for type checking only, not at runtime to avoid circular imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models.agents.predator import Predator

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
        self.brain = HerbivoreBrain()  # Initialize fuzzy brain
        self.sprint_cooldown = 0  # Cooldown tracker for sprint ability
    
    def step(self):
        """Perform one step of the herbivore's behavior"""
        try:
            # Update sprint cooldown
            if self.sprint_cooldown > 0:
                self.sprint_cooldown -= 1
                
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
            
            # Reduced scanning range for predators - was too good at detecting
            predator_info = self._scan_for_predators(radius=3)  # Reduced from 5 to 3
            
            # Get environmental inputs
            inputs = self._gather_inputs(predator_info)
            
            # Get decision from fuzzy brain
            decision = self.brain.decide(inputs)
            
            # Act based on decision
            self._execute_decision(decision)
                    
        except Exception as e:
            print(f"Herbivore step error: {e}")
    
    def _scan_for_predators(self, radius=5):
        """Scan surroundings for predators with enhanced detection"""
        if not self._check_position():
            return {"detected": False, "closest_dist": float('inf'), "predator_cells": []}
            
        try:
            # Get a wider view of surroundings
            neighborhood = self.model.grid.get_neighborhood(
                self.pos, moore=True, include_center=False, radius=radius)
                
            # Track predator positions and closest distance
            predator_cells = []
            closest_dist = float('inf')
            
            for cell in neighborhood:
                cell_content = self.model.grid.get_cell_list_contents([cell])
                for agent in cell_content:
                    if hasattr(agent, 'is_predator') and agent.is_predator:
                        dist = self._calculate_distance(self.pos, cell)
                        predator_cells.append((cell, dist))  # Store both cell and distance
                        closest_dist = min(closest_dist, dist)
            
            return {
                "detected": len(predator_cells) > 0,
                "closest_dist": closest_dist,
                "predator_cells": predator_cells
            }
                
        except Exception as e:
            print(f"Predator scanning error: {e}")
            return {"detected": False, "closest_dist": float('inf'), "predator_cells": []}
    
    def _gather_inputs(self, predator_info=None):
        """Gather environmental inputs for the fuzzy brain"""
        # Default values
        inputs = {
            "energy": self.energy / self.max_energy,  # Normalized energy
            "food_proximity": 6,  # Default: no food visible
            "predator_proximity": 6  # Default: no predators visible
        }
        
        if not self._check_position():
            return inputs
            
        try:
            # Get surrounding cells
            neighborhood = self.model.grid.get_neighborhood(
                self.pos, moore=True, include_center=False, radius=3)
                
            # Check for food (grass)
            closest_food_dist = float('inf')
            for cell in neighborhood:
                cell_content = self.model.grid.get_cell_list_contents([cell])
                for agent in cell_content:
                    if hasattr(agent, 'is_grass') and agent.is_grass:
                        dist = self._calculate_distance(self.pos, cell)
                        closest_food_dist = min(closest_food_dist, dist)
            
            # Update food proximity (convert to 0-6 scale, 0 = here, 6 = not visible)
            if closest_food_dist != float('inf'):
                inputs["food_proximity"] = min(6, closest_food_dist)
            
            # Use predator info if provided, otherwise check for predators
            if predator_info and predator_info["detected"]:
                inputs["predator_proximity"] = min(6, predator_info["closest_dist"])
            else:
                # Check for predators in the immediate area
                closest_predator_dist = float('inf')
                for cell in neighborhood:
                    cell_content = self.model.grid.get_cell_list_contents([cell])
                    for agent in cell_content:
                        if hasattr(agent, 'is_predator') and agent.is_predator:
                            dist = self._calculate_distance(self.pos, cell)
                            closest_predator_dist = min(closest_predator_dist, dist)
                
                # Update predator proximity (convert to 0-6 scale, 0 = here, 6 = not visible)
                if closest_predator_dist != float('inf'):
                    inputs["predator_proximity"] = min(6, closest_predator_dist)
                
        except Exception as e:
            print(f"Herbivore input gathering error: {e}")
            
        return inputs
    
    def _calculate_distance(self, pos1, pos2):
        """Calculate Manhattan distance between two positions"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def _execute_decision(self, decision):
        """Execute the decision from the fuzzy brain"""
        # Handle movement decision
        movement = decision.get("movement", "wander")
        
        if movement == "sprint":
            # Emergency escape mode
            if self.sprint_cooldown <= 0:
                # Higher energy cost for sprinting
                emergency_cost = 0.08 * self.max_energy  # Increased from 5% to 8% of max energy
                self.energy = max(0, self.energy - emergency_cost)
                
                # Perform sprint escape (enhanced fleeing)
                self._sprint_from_predators()
                
                # Set cooldown
                self.sprint_cooldown = 5  # Increased from 3 to 5 turns
            else:
                # Can't sprint, do regular flee
                self._evade_predators()
        elif movement == "flee":
            self._evade_predators()
        elif movement == "seek_food":
            self._find_food()
        elif movement == "seek_partner":
            self._seek_partner()
        else:  # wander
            self.random_move()
            
        # Eat grass in current cell (regardless of movement decision)
        self.eat_grass()
        
        # Handle breeding decision
        if decision.get("breed", False) and random.random() < HERBIVORE_BREEDING_CHANCE:
            self.reproduce()
    
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
    
    def _find_food(self):
        """Move toward the closest grass"""
        if not self._check_position():
            return
            
        try:
            # Get nearby cells
            neighborhood = self.model.grid.get_neighborhood(
                self.pos, moore=True, include_center=False)
                
            # Look for cells with grass
            food_cells = []
            for cell in neighborhood:
                cell_content = self.model.grid.get_cell_list_contents([cell])
                if any(hasattr(agent, 'is_grass') for agent in cell_content):
                    food_cells.append(cell)
            
            # If food found, move toward it
            if food_cells:
                target_cell = random.choice(food_cells)
                self.move_to(target_cell)
            else:
                # No food in immediate vicinity, random move
                self.random_move()
                
        except Exception as e:
            print(f"Find food error: {e}")
    
    def _evade_predators(self):
        """Move away from nearby predators with improved but not too effective escape logic"""
        if not self._check_position():
            return
            
        try:
            # Get predator information with narrower scan
            predator_info = self._scan_for_predators(radius=3)  # Reduced from 5 to 3
            
            if not predator_info["detected"]:
                # No predators detected, move randomly
                self.random_move()
                return
                
            # 25% chance to make a suboptimal escape decision when not in immediate danger
            if predator_info["closest_dist"] >= 3 and random.random() < 0.25:
                self.random_move()
                return
                
            # Get all nearby cells for potential movement
            neighborhood = self.model.grid.get_neighborhood(
                self.pos, moore=True, include_center=False)  # Reduced from radius 2 to immediate neighbors
                
            # Evaluate safety of each cell
            safe_cells = []
            cell_scores = {}
            
            for cell in neighborhood:
                # Skip cells that are occupied by other agents that would block movement
                cell_content = self.model.grid.get_cell_list_contents([cell])
                if any(hasattr(agent, 'blocks_movement') for agent in cell_content):
                    continue
                    
                # Calculate score for this cell (higher is better)
                score = 0
                
                # Factor 1: Distance from predators (most important)
                min_pred_dist = float('inf')
                for pred_cell, pred_dist in predator_info["predator_cells"]:
                    dist_to_pred = self._calculate_distance(cell, pred_cell)
                    min_pred_dist = min(min_pred_dist, dist_to_pred)
                
                if min_pred_dist != float('inf'):
                    # Higher score for cells further from predators
                    score += min_pred_dist * 4  # Reduced from 5 to 4
                
                # Factor 2: Prefer cells that move away from current position relative to predator
                # (i.e., if predator is south, prefer north cells)
                if len(predator_info["predator_cells"]) > 0:
                    # Find the closest predator
                    closest_pred = min(predator_info["predator_cells"], key=lambda x: x[1])
                    closest_pred_pos = closest_pred[0]
                    
                    # Calculate vector from predator to current position
                    away_vector = (self.pos[0] - closest_pred_pos[0], self.pos[1] - closest_pred_pos[1])
                    
                    # Calculate vector from current position to candidate cell
                    move_vector = (cell[0] - self.pos[0], cell[1] - self.pos[1])
                    
                    # Dot product to see if we're moving in similar direction to "away vector"
                    dot_product = away_vector[0] * move_vector[0] + away_vector[1] * move_vector[1]
                    score += max(0, dot_product * 2)  # Reduced from 3 to 2
                
                # Factor 3: Prefer cells with food
                has_food = False
                for agent in cell_content:
                    if hasattr(agent, 'is_grass') and agent.is_grass:
                        has_food = True
                        break
                
                if has_food:
                    score += 3  # Increased from 2 to 3 - more emphasis on food
                
                # Store the score for this cell
                cell_scores[cell] = score
                safe_cells.append(cell)
            
            # Choose cell with best score if we have options
            if safe_cells:
                # Sort by score (highest first)
                best_cells = sorted(safe_cells, key=lambda c: cell_scores[c], reverse=True)
                
                # Take the best cell or one of the top cells with more randomness
                if len(best_cells) > 2:
                    # Choose from top cells with more randomness
                    # 60% chance to pick best cell, 40% chance for a random choice from top 3
                    if random.random() < 0.6:
                        target_cell = best_cells[0]
                    else:
                        target_cell = random.choice(best_cells[:3])
                else:
                    # Take the best cell if we don't have many options
                    target_cell = best_cells[0]
                
                self.move_to(target_cell)
            else:
                # No safe cells found, just try to move randomly
                self.random_move()
                
        except Exception as e:
            print(f"Evade predators error: {e}")
    
    def _sprint_from_predators(self):
        """Emergency escape with limited movement range"""
        if not self._check_position():
            return
            
        try:
            # Get predator information
            predator_info = self._scan_for_predators(radius=3)  # Reduced from 5 to 3
            
            if not predator_info["detected"]:
                # No predators detected, just do regular movement
                self.random_move()
                return
                
            # Find the closest predator
            closest_pred = min(predator_info["predator_cells"], key=lambda x: x[1])
            closest_pred_pos = closest_pred[0]
            
            # Calculate the direction vector away from predator
            away_vector = (self.pos[0] - closest_pred_pos[0], self.pos[1] - closest_pred_pos[1])
            
            # Normalize and scale the vector (for longer movement)
            magnitude = math.sqrt(away_vector[0]**2 + away_vector[1]**2)
            if magnitude > 0:
                away_vector = (away_vector[0]/magnitude, away_vector[1]/magnitude)
            
            # Calculate target position (only 1 cell away in the direction away from predator)
            # When predator is very close (dist <= 2), try to move 2 cells
            move_dist = 1
            if closest_pred[1] <= 2:  # Only get 2-cell sprint when predator is very close
                move_dist = 2
                
            # Using integer positions and rounding
            target_x = self.pos[0] + round(away_vector[0] * move_dist)
            target_y = self.pos[1] + round(away_vector[1] * move_dist)
            
            # Ensure target is within grid bounds
            target_x = max(0, min(self.model.grid.width - 1, target_x))
            target_y = max(0, min(self.model.grid.height - 1, target_y))
            
            target_pos = (target_x, target_y)
            
            # 30% chance to fail the longer 2-cell sprint
            if move_dist == 2 and random.random() < 0.3:
                # Fall back to 1-cell move in the right direction
                cell_x = self.pos[0] + round(away_vector[0])
                cell_y = self.pos[1] + round(away_vector[1])
                cell_x = max(0, min(self.model.grid.width - 1, cell_x))
                cell_y = max(0, min(self.model.grid.height - 1, cell_y))
                target_pos = (cell_x, cell_y)
            
            # Get a path of cells to move through
            path = self._get_path_to(target_pos)
            
            if path and len(path) > 0:
                # Move along the path
                move_to = path[0]
                if len(path) > 1 and move_dist == 2:
                    # Try to move 2 cells for sprint
                    second_cell = path[1]
                    # Check if second cell is empty or has only grass
                    cell_content = self.model.grid.get_cell_list_contents([second_cell])
                    if not any(hasattr(agent, 'blocks_movement') for agent in cell_content):
                        move_to = second_cell
                
                self.move_to(move_to)
            else:
                # Fall back to evade if no path
                self._evade_predators()
                
        except Exception as e:
            print(f"Sprint error: {e}")
    
    def _get_path_to(self, target_pos):
        """Generate a path from current position to target"""
        if not self._check_position():
            return []
            
        # Simple path generation - get cells in a line toward target
        path = []
        current = self.pos
        
        # Get neighborhood in larger radius
        neighborhood = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False, radius=2)
            
        # Find cells that are progressively closer to target
        while neighborhood:
            # Find the cell closest to target
            closest = min(neighborhood, key=lambda cell: self._calculate_distance(cell, target_pos))
            
            # Add to path and prepare for next iteration
            path.append(closest)
            
            # If we've reached target or are getting farther, stop
            if closest == target_pos or self._calculate_distance(closest, target_pos) >= self._calculate_distance(current, target_pos):
                break
                
            # Update for next step
            current = closest
            neighborhood = self.model.grid.get_neighborhood(
                current, moore=True, include_center=False)
            
        return path
    
    def _seek_partner(self):
        """Move toward other herbivores for potential reproduction"""
        if not self._check_position():
            return
            
        try:
            # Get nearby cells within a larger radius
            neighborhood = self.model.grid.get_neighborhood(
                self.pos, moore=True, include_center=False, radius=3)
                
            # Look for cells with other herbivores
            partner_cells = []
            for cell in neighborhood:
                cell_content = self.model.grid.get_cell_list_contents([cell])
                herbivores_in_cell = [agent for agent in cell_content 
                                    if hasattr(agent, 'is_herbivore') and agent.is_herbivore and agent != self]
                if herbivores_in_cell:
                    # Add with priority proportional to number of potential partners
                    partner_cells.extend([cell] * len(herbivores_in_cell))
            
            # If potential partners found, move toward one
            if partner_cells:
                # Choose weighted by concentration of potential partners
                target_cell = random.choice(partner_cells)
                self.move_to(target_cell)
            else:
                # No potential partners in immediate vicinity, random move
                self.random_move()
                
        except Exception as e:
            print(f"Seek partner error: {e}")
    
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

