import mesa

class Carnivore(mesa.Agent):
    """
    A carnivore agent
    Can:
    - notice environment
    - hunt herbivores
    - in flocks, hunt omnivores
    - breed

    Can't:
    - 1 on 1 omnivore
    - run away

    """

    def __init__(self, model):
        super().__init__(model)

    def look_around(self):
        pass

    def move(self):
        pass

    def run_away(self):
        pass

    def eat(self):
        pass

    def breed(self):
        print("TEST")
        pass



