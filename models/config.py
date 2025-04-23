"""
Configuration parameters for the simulation
"""

# Grass parameters
GRASS_SPREAD_CHANCE = 0.05
GRASS_ENERGY_VALUE = 20

# Herbivore parameters
HERBIVORE_INIT_ENERGY = 50
HERBIVORE_MAX_ENERGY = 100
HERBIVORE_HUNGER_LEVELS = [
    (20, 0.4),  # Severely hungry
    (10, 0.2),  # Hungry
    (0, 0.1)    # Normal hunger (with 20% chance)
]
HERBIVORE_ENERGY_LOSS_CHANCE = 0.2  # Only lose energy 20% of the time when not very hungry
HERBIVORE_BREEDING_ENERGY_THRESHOLD = 0.9  # 90% of max energy
HERBIVORE_BREEDING_CHANCE = 0.1  # 10% chance
HERBIVORE_BREEDING_ENERGY_COST = 0.5  # 50% energy cost
HERBIVORE_OFFSPRING_ENERGY_FACTOR = 0.8  # 80% of parent's energy

# Predator parameters
PREDATOR_INIT_ENERGY = 80
PREDATOR_MAX_ENERGY = 150
PREDATOR_HUNGER_LEVELS = [
    (15, 0.8),  # Severely hungry
    (7, 0.4),   # Hungry
    (0, 0.2)    # Normal hunger
]
PREDATOR_BREEDING_ENERGY_THRESHOLD = 0.9  # 90% of max energy
PREDATOR_BREEDING_CHANCE = 0.05  # 5% chance
PREDATOR_BREEDING_ENERGY_COST = 0.5  # 50% energy cost
PREDATOR_OFFSPRING_ENERGY_FACTOR = 0.4  # 40% of parent's original energy
PREDATOR_BREEDING_COOLDOWN = 40  # Steps before can breed again
PREDATOR_PREY_ENERGY_VALUE = 30  # Energy gained from eating a herbivore 