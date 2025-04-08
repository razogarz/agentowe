import matplotlib.pyplot as plt
import numpy as np
from models.agents.herbivore import Grass, Herbivore  # Direct import


def visualize_grid(model):
    """
    Visualizes the simulation grid for a given Mesa model.

    For each cell in the grid:
      - The cell's green intensity indicates the abundance of Grass agents.
      - A white number overlaid indicates the count of Herbivore agents.
    """
    width, height = model.grid.width, model.grid.height

    # Create an RGB image array initialized to zeros
    grid_rgb = np.zeros((height, width, 3))

    # Create an array to store herbivore counts for overlaying
    herbivore_counts = np.zeros((height, width), dtype=int)

    # Iterate over each cell in the grid
    for x in range(width):
        for y in range(height):
            cell_agents = model.grid.get_cell_list_contents((x, y))

            # Count the number of Grass agents on the cell
            num_grass = sum(1 for agent in cell_agents if isinstance(agent, Grass))

            # Count the number of Herbivore agents on the cell
            num_herbivores = sum(1 for agent in cell_agents if isinstance(agent, Herbivore))
            herbivore_counts[y, x] = num_herbivores

            # Set green intensity based on grass abundance (adjust scaling if needed)
            green_intensity = min(1.0, num_grass * 0.3)
            grid_rgb[y, x, 1] = green_intensity

    # Create the plot
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.imshow(grid_rgb, origin='lower', interpolation='none')
    ax.set_title("Simulation Grid\n(Green intensity: grass amount; Numbers: herbivore count)")

    # Overlay the herbivore counts as text on each cell
    for x in range(width):
        for y in range(height):
            if herbivore_counts[y, x] > 0:
                ax.text(x, y, str(herbivore_counts[y, x]), color='white',
                        ha='center', va='center', fontsize=8, fontweight='bold')

    # Draw a grid for clarity
    ax.set_xticks(np.arange(-0.5, width, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, height, 1), minor=True)
    ax.grid(which='minor', color='gray', linestyle='-', linewidth=0.5)
    ax.tick_params(which="minor", size=0)
    ax.set_xticklabels([])
    ax.set_yticklabels([])

    plt.show()