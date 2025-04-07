import mesa
import skfuzzy.control as ctrl
import numpy as np

class Herbivore(mesa.Agent):
    def __init__(
            self,
            model,
            energy=50,
            max_energy_prey=100,
    ):
        super().__init__(model)
        self.energy = energy
        self.age = 0
        self.max_energy_prey = max_energy_prey

    def eat(self):
        # Check if the agent is on a grass tile
        agents_on_tile = self.model.grid.get_cell_list_contents([self.pos])
        is_grass = False
        grass_to_be_eaten = None
        for agent in agents_on_tile:
            if isinstance(agent, Grass):
                is_grass = True
                grass_to_be_eaten = agent
                break
        if is_grass:
            self.energy = min(self.energy + self.model.energy_grass, self.model.max_energy_prey)
            self.model.grid.remove_agent(grass_to_be_eaten)
            return True

        return False

    def move(self):
        self.energy -= 2
        possible_steps = self.model.grid.get_neighborhood(
                    self.pos,
                    moore=True,
                    include_center=False)
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def step(self):
        has_eaten = self.eat()

        if not has_eaten:
            self.move()

    # def create_fuzzy_map(self, area_of_sight):
    #     food = ctrl.Antecedent(np.linspace(0, 1, area_of_sight), 'food')
    #     energy = ctrl.Antecedent(np.linspace(0, 1, area_of_sight), 'energy')
    #     mate = ctrl.Antecedent(np.linspace(0, 1, area_of_sight), 'mate')
    #     decision = ctrl.Consequent(np.linspace(0, 1, area_of_sight), 'decision')
    #
    #     # sensitive concepts
    #     food.automf(names=['close', 'far'])
    #     energy.automf(names=['low', 'medium', 'high'])
    #     mate.automf(names=['close', 'far'])
    #     decision.automf(names=['evasion', 'search_for_food', 'breeding'])
    #
    #     # internal concepts
    #     fear = ctrl.Antecedent(np.linspace(0, 1, area_of_sight), 'fear')
    #     hunger = ctrl.Antecedent(np.linspace(0, 1, area_of_sight), 'hunger')
    #     sexual_need = ctrl.Antecedent(np.linspace(0, 1, area_of_sight), 'sexual_need')
    #
    #     fear.automf(names=['low', 'medium', 'high'])
    #     hunger.automf(names=['low', 'medium', 'high'])
    #     sexual_need.automf(names=['low', 'medium', 'high'])
    #
    #     # motor concepts
    #     evasion = ctrl.Consequent(np.linspace(0, 1, area_of_sight), 'evasion')
    #     search_for_food = ctrl.Consequent(np.linspace(0, 1, area_of_sight), 'search_for_food')
    #     breeding = ctrl.Consequent(np.linspace(0, 1, area_of_sight), 'breeding')
    #
    #     evasion.automf(names=['low', 'medium', 'high'])
    #     search_for_food.automf(names=['low', 'medium', 'high'])
    #     breeding.automf(names=['low', 'medium', 'high'])
    #
    #     # Define fuzzy rules
    #     rules = [
    #         ctrl.Rule(hunger['high'] & food['close'], search_for_food['high']),
    #         ctrl.Rule(hunger['medium'] & food['far'], search_for_food['medium']),
    #         ctrl.Rule(hunger['low'], search_for_food['low']),
    #         ctrl.Rule(fear['high'], evasion['high']),
    #         ctrl.Rule(fear['medium'], evasion['medium']),
    #         ctrl.Rule(fear['low'], evasion['low']),
    #         ctrl.Rule(sexual_need['high'] & mate['close'], breeding['high']),
    #         ctrl.Rule(sexual_need['medium'] & mate['far'], breeding['medium']),
    #         ctrl.Rule(sexual_need['low'], breeding['low']),
    #     ]
    #
    #     # Create control system and simulation
    #     decision_ctrl = ctrl.ControlSystem(rules)
    #     decision_sim = ctrl.ControlSystemSimulation(decision_ctrl)
    #
    #     return decision_sim


class Grass(mesa.Agent):
    def __init__(self, model):
        super().__init__(model)
        self.growth_rate = 1
        self.max_growth = 10

    def step(self):
        # use prob to try to grow
        # if self.random.random() < 0.1:
        #     print("Imma grass and imma chilling")
        pass

