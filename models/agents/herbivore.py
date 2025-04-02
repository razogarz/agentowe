import mesa
import random
import math

class Herbivore(mesa.Agent):
    def __init__(self, unique_id, model, energy=10, hunger=1):
        super().__init__(unique_id, model)
        self.energy = energy
        self.hunger = hunger
        self.age = 0

    def fuzzy_decision(self):
        pass

    def eat(self):
        self.hunger = min(self.hunger + 0.2, 1)
        return

    def move(self):

        possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        if possible_steps:
            new_position = random.choice(possible_steps)
            self.model.grid.move_agent(self, new_position)

    def breed(self):
        """
        Reproduce if energy is above a reproduction threshold.
        The herbivore stays in place to breed (if there's an adjacent empty cell).
        """
        reproduction_threshold = 15  # Example threshold value
        if self.energy >= reproduction_threshold:
            possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
            free_cells = [pos for pos in possible_steps if self.model.grid.is_cell_empty(pos)]
            if free_cells:
                new_pos = random.choice(free_cells)
                offspring_energy = self.energy / 2
                self.energy /= 2  # Parent gives half its energy to offspring
                offspring = Herbivore(self.model.next_id(), self.model, energy=offspring_energy)
                self.model.grid.place_agent(offspring, new_pos)
                self.model.schedule.add(offspring)

    def die(self):
        """
        Remove the herbivore from the simulation if energy is depleted.
        """
        self.model.grid.remove_agent(self)
        self.model.schedule.remove(self)

    # def look_around(self):
    #     neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False)
    #     # Assuming food agents have an attribute 'energy_value' and predators have 'is_predator'
    #     food = [agent for agent in neighbors if hasattr(agent, "energy_value")]
    #     predators = [agent for agent in neighbors if getattr(agent, "is_predator", False)]
    #     return food, predators
    #
    # def move_towards_food(self, food):
    #     x, y = self.pos
    #     # Use Manhattan distance for simplicity
    #     closest_food = min(food, key=lambda agent: abs(agent.pos[0] - x) + abs(agent.pos[1] - y))
    #     food_x, food_y = closest_food.pos
    #     # Compute step direction toward food
    #     step_x = 1 if food_x > x else -1 if food_x < x else 0
    #     step_y = 1 if food_y > y else -1 if food_y < y else 0
    #     new_position = (x + step_x, y + step_y)
    #     if not self.model.grid.out_of_bounds(new_position):
    #         self.model.grid.move_agent(self, new_position)
    #     else:
    #         self.move()  # fallback to random move if out-of-bounds
    #
    # def run_away(self):
    #     """
    #     Move away from predators.
    #     Computes a direction vector opposite to the average location of nearby predators.
    #     """
    #     _, predators = self.look_around()
    #     if predators:
    #         x, y = self.pos
    #         dx, dy = 0, 0
    #         for predator in predators:
    #             pred_x, pred_y = predator.pos
    #             dx += (x - pred_x)
    #             dy += (y - pred_y)
    #         magnitude = math.sqrt(dx**2 + dy**2)
    #         if magnitude == 0:
    #             self.move()  # If overlapping, fallback to random move
    #         else:
    #             step_x = 1 if dx > 0 else -1 if dx < 0 else 0
    #             step_y = 1 if dy > 0 else -1 if dy < 0 else 0
    #             new_position = (x + step_x, y + step_y)
    #             if not self.model.grid.out_of_bounds(new_position):
    #                 self.model.grid.move_agent(self, new_position)
    #             else:
    #                 self.move()  # fallback

    def step(self):
        """
        The sequence of actions in one time step:
        1. Increase age and reduce energy (metabolic cost).
        2. Try to eat food in the current cell (staying in place while eating).
        3. If no food is available in place:
           - If predators are nearby, run away.
           - Otherwise, if food is detected in neighboring cells, move toward it.
           - If neither, move randomly.
        4. After moving (if applicable), check again to eat if food is now present.
        5. Attempt to breed if energy is sufficient.
        6. Die if energy falls to or below zero.
        """
        # Metabolic cost
        self.age += 1
        self.energy -= 1  # Adjust metabolic cost as needed

        if self.energy <= 0:
            self.die()
            return  # Exit step if dead

        # Attempt to eat in the current cell
        ate = self.eat()

        # Look around regardless of whether eating occurred, to check for threats and opportunities
        food, predators = self.look_around()

        if predators:
            self.run_away()
        elif not ate and food:
            # If there was no food in the current cell, try moving toward food
            self.move_towards_food(food)
            # After moving, attempt to eat in the new cell
            self.eat()
        elif not predators and not food:
            # No food or predators: move randomly
            self.move()

        # Reproduction attempt after moving/eating
        self.breed()
