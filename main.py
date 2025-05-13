import pygame
import sys
import time
import numpy as np
import matplotlib.pyplot as plt
import os
import datetime
from models.simulation import PPModel  # Import your Mesa model
from models.agents.grass import Grass  # Updated import
from models.agents.herbivore import Herbivore  # Updated import
from models.agents.predator import Predator  # Import the predator class

# Simulation parameters
GRID_CELL_SIZE = 10  # Size (in pixels) for each grid cell.
STEP_DELAY = 0.1  # Delay between simulation steps (in seconds).
WINDOW_MARGIN = 20  # Margin around the grid display.


def draw_grid(screen, model):
    """
    Draws the grid, coloring each cell's background based on grass count
    and drawing agents as colored circles:
    - Herbivores: blue circles
    - Predators: red circles
    - Grass: green background
    """
    width, height = model.grid.width, model.grid.height

    # Loop over grid cells
    for x in range(width):
        for y in range(height):
            # Get agents in the cell:
            cell_agents = model.grid.get_cell_list_contents((x, y))

            # Count Grass, Herbivores, and Predators
            num_grass = sum(1 for agent in cell_agents if isinstance(agent, Grass))
            num_herbivores = sum(1 for agent in cell_agents if isinstance(agent, Herbivore))
            num_predators = sum(1 for agent in cell_agents if isinstance(agent, Predator))

            # Determine cell color: base black, then add green if grass is present.
            # The more grass agents, the brighter the green (capped at full green).
            green_intensity = min(255, int(num_grass * 75))  # adjust scaling factor as needed
            cell_color = (0, green_intensity, 0)

            # Calculate pixel rectangle for the cell:
            rect = pygame.Rect(WINDOW_MARGIN + x * GRID_CELL_SIZE,
                               WINDOW_MARGIN + y * GRID_CELL_SIZE,
                               GRID_CELL_SIZE, GRID_CELL_SIZE)

            pygame.draw.rect(screen, cell_color, rect)

            # Draw herbivores as blue circles
            if num_herbivores > 0:
                center = (WINDOW_MARGIN + x * GRID_CELL_SIZE + GRID_CELL_SIZE // 2,
                          WINDOW_MARGIN + y * GRID_CELL_SIZE + GRID_CELL_SIZE // 2)
                radius = GRID_CELL_SIZE // 2 - 1
                pygame.draw.circle(screen, (0, 0, 255), center, radius)  # Blue for herbivores

            # Draw predators as red circles (on top of herbivores if both present)
            if num_predators > 0:
                center = (WINDOW_MARGIN + x * GRID_CELL_SIZE + GRID_CELL_SIZE // 2,
                          WINDOW_MARGIN + y * GRID_CELL_SIZE + GRID_CELL_SIZE // 2)
                radius = GRID_CELL_SIZE // 2 - 1
                pygame.draw.circle(screen, (255, 0, 0), center, radius)  # Red for predators

            # Draw grid cell border for clarity.
            pygame.draw.rect(screen, (40, 40, 40), rect, 1)


def save_simulation_data(model, filename=None):
    """
    Save the simulation data to a CSV file
    """
    # Get data from datacollector
    data = model.datacollector.get_model_vars_dataframe()
    
    # Create directory for data if it doesn't exist
    os.makedirs('simulation_data', exist_ok=True)
    
    # Generate filename with timestamp if not provided
    if filename is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"simulation_data/predator_prey_sim_{timestamp}.csv"
    
    # Save to CSV
    data.to_csv(filename)
    print(f"Data saved to {filename}")
    
    return filename


def plot_simulation_data(model, save_plots=False, data_file=None):
    """
    Plot various graphs of the simulation data after the simulation ends
    """
    # Get data from the datacollector
    data = model.datacollector.get_model_vars_dataframe()
    
    # Create a figure with subplots
    plt.figure(figsize=(15, 10))
    
    # Plot 1: Population changes over time
    plt.subplot(2, 2, 1)
    plt.plot(data.index, data["Herbivore Population"], 'b-', label='Herbivores')
    plt.plot(data.index, data["Predator Population"], 'r-', label='Predators')
    plt.plot(data.index, data["Grass Coverage"], 'g-', label='Grass Coverage (%)')
    plt.title('Population Changes Over Time')
    plt.xlabel('Time Steps')
    plt.ylabel('Count / Coverage')
    plt.legend()
    plt.grid(True)
    
    # Plot 2: Predator vs Prey Relationship
    plt.subplot(2, 2, 2)
    plt.scatter(data["Herbivore Population"], data["Predator Population"], 
                c=data.index, cmap='viridis', alpha=0.7)
    plt.title('Predator vs Prey Population')
    plt.xlabel('Herbivore Population')
    plt.ylabel('Predator Population')
    plt.grid(True)
    plt.colorbar(label='Time Step')
    
    # Plot 3: Running averages
    window_size = min(20, len(data))  # For moving average, use smaller of 20 or data length
    
    if window_size > 1:
        rolling_herb = data["Herbivore Population"].rolling(window=window_size).mean()
        rolling_pred = data["Predator Population"].rolling(window=window_size).mean()
        rolling_grass = data["Grass Coverage"].rolling(window=window_size).mean()
        
        plt.subplot(2, 2, 3)
        plt.plot(data.index[window_size-1:], rolling_herb[window_size-1:], 'b-', 
                label=f'Herbivores ({window_size}-step Avg)')
        plt.plot(data.index[window_size-1:], rolling_pred[window_size-1:], 'r-', 
                label=f'Predators ({window_size}-step Avg)')
        plt.plot(data.index[window_size-1:], rolling_grass[window_size-1:], 'g-', 
                label=f'Grass Coverage ({window_size}-step Avg)')
        plt.title(f'Moving Averages (Window: {window_size} steps)')
        plt.xlabel('Time Steps')
        plt.ylabel('Average Value')
        plt.legend()
        plt.grid(True)
    
    # Plot 4: Relative compositions
    plt.subplot(2, 2, 4)
    # Calculate total for normalization - note grass is a percentage already
    # We'll just stack them visually but keep their original values
    plt.stackplot(data.index, 
                 [data["Grass Coverage"], data["Herbivore Population"], data["Predator Population"]], 
                 labels=['Grass Coverage', 'Herbivores', 'Predators'],
                 colors=['green', 'blue', 'red'], alpha=0.7)
    plt.title('Ecosystem Composition')
    plt.xlabel('Time Steps')
    plt.ylabel('Value')
    plt.legend(loc='upper left')
    plt.grid(True)
    
    # Add overall title
    plt.suptitle('Predator-Prey Simulation Results', fontsize=16)
    plt.tight_layout(rect=[0, 0, 1, 0.96])  # Adjust for suptitle
    
    # Calculate and display summary statistics
    mean_herbivore = data["Herbivore Population"].mean()
    mean_predator = data["Predator Population"].mean()
    mean_grass = data["Grass Coverage"].mean()
    
    max_herbivore = data["Herbivore Population"].max()
    max_predator = data["Predator Population"].max()
    max_grass = data["Grass Coverage"].max()
    
    min_herbivore = data["Herbivore Population"].min()
    min_predator = data["Predator Population"].min()
    min_grass = data["Grass Coverage"].min()
    
    print("\n--- Simulation Summary Statistics ---")
    print(f"Total time steps: {len(data)}")
    print("\nAverage Population/Coverage:")
    print(f"  Herbivores: {mean_herbivore:.2f}")
    print(f"  Predators: {mean_predator:.2f}")
    print(f"  Grass Coverage: {mean_grass:.2f}%")
    
    print("\nMaximum Population/Coverage:")
    print(f"  Herbivores: {max_herbivore}")
    print(f"  Predators: {max_predator}")
    print(f"  Grass Coverage: {max_grass:.2f}%")
    
    print("\nMinimum Population/Coverage:")
    print(f"  Herbivores: {min_herbivore}")
    print(f"  Predators: {min_predator}")
    print(f"  Grass Coverage: {min_grass:.2f}%")
    
    # Save plots if requested
    if save_plots:
        # Create directory for plots if it doesn't exist
        os.makedirs('simulation_plots', exist_ok=True)
        
        # Generate filename based on the data file if available
        if data_file:
            base_filename = os.path.splitext(os.path.basename(data_file))[0]
            plot_filename = f"simulation_plots/{base_filename}_plots.png"
        else:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            plot_filename = f"simulation_plots/predator_prey_sim_{timestamp}_plots.png"
        
        plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
        print(f"Plots saved to {plot_filename}")
    
    plt.show()


def run_interactive_simulation():
    # Initialize Mesa model with balanced parameters
    model = PPModel(
        initial_herbivores=30,  # Fewer herbivores
        initial_predators=5,    # Fewer predators
        width=75, 
        height=75
    )

    # Initialize Pygame.
    pygame.init()
    grid_width, grid_height = model.grid.width, model.grid.height
    window_width = grid_width * GRID_CELL_SIZE + 2 * WINDOW_MARGIN
    window_height = grid_height * GRID_CELL_SIZE + 2 * WINDOW_MARGIN

    screen = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption("Predator-Prey Simulation")

    clock = pygame.time.Clock()

    running = True
    step_mode = False  # Change to True if you want the simulation to wait for a key press each step
    
    # Display controls
    print("\n--- Predator-Prey Simulation Controls ---")
    print("Space: Pause/Step simulation")
    print("S: Save current simulation data to CSV")
    print("Q: Quit simulation and show plots")

    while running:
        # Process Pygame events.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Process key presses
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    step_mode = not step_mode
                    print("Simulation " + ("paused" if step_mode else "resumed"))
                elif event.key == pygame.K_s:
                    # Save data when 's' is pressed
                    data_file = save_simulation_data(model)
                elif event.key == pygame.K_q:
                    # Quit and show plots when 'q' is pressed
                    running = False

        # In automatic mode, we update every STEP_DELAY seconds.
        if not step_mode:
            time.sleep(STEP_DELAY)
            # Advance the simulation by one step.
            model.step()
        else:
            # If in pause mode, just wait
            clock.tick(10)  # Lower frame rate while waiting.

        # Clear the screen.
        screen.fill((0, 0, 0))
        # Draw the grid state.
        draw_grid(screen, model)
        
        # Draw status information on the screen
        step_count = len(model.datacollector.get_model_vars_dataframe())
        font = pygame.font.SysFont('Arial', 16)
        text = font.render(f"Step: {step_count} | {'PAUSED' if step_mode else 'RUNNING'}", True, (255, 255, 255))
        screen.blit(text, (10, 5))
        
        # Update the display
        pygame.display.flip()

    pygame.quit()
    
    # Save final data
    data_file = save_simulation_data(model)
    
    # Plot data after simulation ends
    plot_simulation_data(model, save_plots=True, data_file=data_file)
    
    # Exit the program after plots are closed
    sys.exit()


if __name__ == "__main__":
    run_interactive_simulation()