import mesa
import random
from models.config import GRASS_SPREAD_CHANCE

class Grass(mesa.Agent):
    """Simple Grass agent that can grow and spread to neighboring cells"""
    
    def __init__(self, model):
        super().__init__(model)
        self.is_grass = True
        
    def step(self):
        """Try to spread to a neighboring cell with a small chance"""
        if random.random() < GRASS_SPREAD_CHANCE:
            self._try_spread()
    
    def _try_spread(self):
        """Attempt to spread to a neighboring empty cell"""
        try:
            if hasattr(self, "pos") and self.pos is not None:
                # Get neighboring cells
                neighbors = self.model.grid.get_neighborhood(
                    self.pos, moore=True, include_center=False)
                
                if not neighbors:
                    return
                    
                # Choose a random neighbor cell
                new_pos = random.choice(neighbors)
                
                # Check if it's empty (no grass)
                cell_content = self.model.grid.get_cell_list_contents([new_pos])
                if not any(hasattr(a, 'is_grass') for a in cell_content):
                    # Create and place new grass
                    new_grass = Grass(self.model)
                    self.model.grid.place_agent(new_grass, new_pos)
        except Exception as e:
            print(f"Grass growth error: {e}") 