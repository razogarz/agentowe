import mesa
import random
import math


class Carnivore(mesa.Agent):
    """
    A carnivore agent.

    Capabilities:
    - Perceive its surroundings for potential prey:
         * Herbivores (preferred prey)
         * Omnivores (only successfully hunted in groups)
    - Hunt (i.e., eat) prey while staying in place.
    - Move toward prey if not present in the current cell.
    - Breed when energy is sufficient.

    Limitations:
    - Cannot hunt omnivores successfully on its own.
    - Does not run away (apex predator behavior).
    """

    def __init__(self, unique_id, model, energy=15):
        super().__init__(unique_id, model)
        self.energy = energy
        self.age = 0

    def look_around(self):
        """
        Scan the Moore neighborhood for potential prey.
        Returns:
            prey (list): List of herbivore agents in neighboring cells.
            omnivores (list): List of omnivore agents in neighboring cells.
        """
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False)
        # Assume herbivores have an attribute "is_herbivore" set to True
        prey = [agent for agent in neighbors if getattr(agent, "is_herbivore", False)]
        # Assume omnivores have an attribute "is_omnivore" set to True
        omnivores = [agent for agent in neighbors if getattr(agent, "is_omnivore", False)]
        return prey, omnivores

    def move(self):
        """
        Move randomly to an adjacent cell.
        """
        possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        if possible_steps:
            new_position = random.choice(possible_steps)
            self.model.grid.move_agent(self, new_position)

    def move_towards(self, target_pos):
        """
        Move one step towards the given target position.
        """
        x, y = self.pos
        target_x, target_y = target_pos
        # Determine step direction (simple step by 1)
        step_x = 1 if target_x > x else -1 if target_x < x else 0
        step_y = 1 if target_y > y else -1 if target_y < y else 0
        new_position = (x + step_x, y + step_y)
        if not self.model.grid.out_of_bounds(new_position):
            self.model.grid.move_agent(self, new_position)
        else:
            self.move()  # Fallback to random move

    def hunt(self):
        """
        Hunt prey in the current cell. The carnivore stays in place while hunting.
        Priority:
         1. If a herbivore is present, hunt one (successful hunt).
         2. Else, if an omnivore is present and there is more than one carnivore
            in the current cell (i.e., in a flock), hunt one.
        Returns:
            bool: True if a successful hunt occurred, False otherwise.
        """
        cell_agents = self.model.grid.get_cell_list_contents([self.pos])
        # Identify herbivores and omnivores in the current cell.
        local_herbivores = [agent for agent in cell_agents if getattr(agent, "is_herbivore", False)]
        local_omnivores = [agent for agent in cell_agents if getattr(agent, "is_omnivore", False)]

        if local_herbivores:
            # Hunt one herbivore
            target = random.choice(local_herbivores)
            self.energy += target.energy_value  # Gain energy from prey
            self.model.grid.remove_agent(target)
            self.model.schedule.remove(target)
            return True
        elif local_omnivores:
            # To successfully hunt an omnivore, require at least one other carnivore in the same cell
            local_carnivores = [agent for agent in cell_agents if isinstance(agent, Carnivore)]
            if len(local_carnivores) >= 2:
                target = random.choice(local_omnivores)
                self.energy += target.energy_value
                self.model.grid.remove_agent(target)
                self.model.schedule.remove(target)
                return True
        return False

    def breed(self):
        """
        Reproduce if energy is above a reproduction threshold.
        The carnivore stays in place to breed (placing offspring in an adjacent free cell).
        """
        reproduction_threshold = 20  # Example threshold; adjust as needed
        if self.energy >= reproduction_threshold:
            possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
            free_cells = [pos for pos in possible_steps if self.model.grid.is_cell_empty(pos)]
            if free_cells:
                new_pos = random.choice(free_cells)
                offspring_energy = self.energy / 2
                self.energy /= 2  # Split energy with offspring
                offspring = Carnivore(self.model.next_id(), self.model, energy=offspring_energy)
                self.model.grid.place_agent(offspring, new_pos)
                self.model.schedule.add(offspring)

    def run_away(self):
        """
        Carnivores do not run away. Method is defined for compatibility.
        """
        pass

    def step(self):
        """
        Defines the agent's behavior in a single time step:
        1. Increase age and reduce energy due to metabolism.
        2. Try to hunt in the current cell:
            - If prey is available (herbivores or, in groups, omnivores), stay and hunt.
        3. If no prey is present in the current cell:
            - Look in the neighborhood:
                * If herbivores are detected, move towards the nearest one.
                * Otherwise, move randomly.
            - After moving, try hunting in the new cell.
        4. Attempt to breed if energy is sufficient.
        5. Die if energy falls to zero or below.
        """
        self.age += 1
        # Metabolic energy loss
        self.energy -= 1

        if self.energy <= 0:
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)
            return

        # Attempt to hunt in the current cell
        if not self.hunt():
            # Look around for prey in neighboring cells
            prey, omnivores = self.look_around()
            if prey:
                # Move towards the nearest herbivore
                closest_prey = min(prey,
                                   key=lambda agent: abs(agent.pos[0] - self.pos[0]) + abs(agent.pos[1] - self.pos[1]))
                self.move_towards(closest_prey.pos)
            elif omnivores:
                # Attempt to join group: if not enough carnivores in current cell,
                # move towards omnivores hoping to find a flock.
                self.move_towards(omnivores[0].pos)
            else:
                # No prey detected: random move
                self.move()
            # After moving, try to hunt in the new cell
            self.hunt()

        # Attempt to reproduce
        self.breed()
