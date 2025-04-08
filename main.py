import pygame
import sys
import time
import numpy as np
from models.simulation import PPModel  # Import your Mesa model
from models.agents.herbivore import Grass, Herbivore  # Import your agent classes

# Simulation parameters
GRID_CELL_SIZE = 10  # Size (in pixels) for each grid cell.
STEP_DELAY = 0.1  # Delay between simulation steps (in seconds).
WINDOW_MARGIN = 20  # Margin around the grid display.


def draw_grid(screen, model):
    """
    Draws the grid, coloring each cell's background based on grass count
    and drawing herbivore agents as red circles.
    """
    width, height = model.grid.width, model.grid.height

    # Loop over grid cells
    for x in range(width):
        for y in range(height):
            # Get agents in the cell:
            cell_agents = model.grid.get_cell_list_contents((x, y))

            # Count Grass and Herbivores
            num_grass = sum(1 for agent in cell_agents if isinstance(agent, Grass))
            num_herbivores = sum(1 for agent in cell_agents if isinstance(agent, Herbivore))

            # Determine cell color: base black, then add green if grass is present.
            # The more grass agents, the brighter the green (capped at full green).
            green_intensity = min(255, int(num_grass * 75))  # adjust scaling factor as needed
            cell_color = (0, green_intensity, 0)

            # Calculate pixel rectangle for the cell:
            rect = pygame.Rect(WINDOW_MARGIN + x * GRID_CELL_SIZE,
                               WINDOW_MARGIN + y * GRID_CELL_SIZE,
                               GRID_CELL_SIZE, GRID_CELL_SIZE)

            pygame.draw.rect(screen, cell_color, rect)

            # If there are herbivores, draw a red circle in the center of the cell.
            if num_herbivores > 0:
                center = (WINDOW_MARGIN + x * GRID_CELL_SIZE + GRID_CELL_SIZE // 2,
                          WINDOW_MARGIN + y * GRID_CELL_SIZE + GRID_CELL_SIZE // 2)
                radius = GRID_CELL_SIZE // 2 - 1
                pygame.draw.circle(screen, (255, 0, 0), center, radius)

            # Draw grid cell border for clarity.
            pygame.draw.rect(screen, (40, 40, 40), rect, 1)


def run_interactive_simulation():
    # Initialize Mesa model with appropriate parameters.
    model = PPModel(initial_herbivores=30, width=75, height=75)

    # Initialize Pygame.
    pygame.init()
    grid_width, grid_height = model.grid.width, model.grid.height
    window_width = grid_width * GRID_CELL_SIZE + 2 * WINDOW_MARGIN
    window_height = grid_height * GRID_CELL_SIZE + 2 * WINDOW_MARGIN

    screen = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption("Interactive Agent Simulation")

    clock = pygame.time.Clock()

    running = True
    step_mode = False  # Change to True if you want the simulation to wait for a key press each step

    while running:
        # Process Pygame events.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Press spacebar to step the simulation if in manual mode.
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    step_mode = True

        # In automatic mode, we update every STEP_DELAY seconds.
        if not step_mode:
            time.sleep(STEP_DELAY)

        # Advance the simulation by one step.
        model.step()

        # Clear the screen.
        screen.fill((0, 0, 0))
        # Draw the grid state.
        draw_grid(screen, model)
        pygame.display.flip()

        # If in step mode (manual stepping), wait until the spacebar is pressed.
        if step_mode:
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        waiting = False
                        running = False
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        waiting = False
                clock.tick(10)  # Lower frame rate while waiting.

            step_mode = False  # Reset step mode.

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    run_interactive_simulation()