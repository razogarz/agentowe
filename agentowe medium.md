
## **Grid (World) Parameters**

- **Size**: 750x750 cells
    
- **Resource Types**: Grass, Meat
    
- **Max Resources per Cell**:
    
    - `maxGrass = 100`
        
    - `maxMeat = 50`
        
- **Grass Growth**:
    
    - `probaGrass = 0.3` (Initial probability of grass in a cell)
        
    - `growGrass = 5` (Grass regrowth per time step)
        
    - `probaGrowGrass = 0.1` (Chance of grass spreading from neighboring cells)
        
- **Meat Decay**:
    
    - `decreaseMeat = 2` (Meat decays over time per step)
        
- **Initial Distribution**: Clustered distribution of individuals
    
    - `sizeClusterPrey = 10` (Preys start in small groups)
        
    - `sizeClusterPredator = 5` (Predators start in smaller clusters)
        

---

## **Simulation Parameters**

- **Time Step Process**:
    
    1. Perception (detect food, threats, mates)
        
    2. Concept computation (basic FCM activation)
        
    3. Action execution (movement, eating, reproduction)
        
    4. Energy update
        
    5. Population update (births/deaths)
        
    6. Resource updates (grass regrowth, meat decay)
        
    7. Aging
        
- **Individual Attributes**:
    
    - `initNbPrey = 50` (Initial number of preys)
        
    - `initNbPredator = 20` (Initial number of predators)
        
    - `maxEnergyPrey = 100`
        
    - `maxEnergyPredator = 150`
        
    - `ageInterbreedPrey = 10` (Minimum age to reproduce)
        
    - `ageInterbreedPredator = 15`
        
    - `maxSpeedPrey = 5`
        
    - `maxSpeedPredator = 7`
        
    - `energyGrass = 20` (Energy gained by preys from eating grass)
        
    - `energyMeat = 50` (Energy gained by predators from eating meat)
        
- **Food Consumption**:
    
    - Preys **eat grass** (can consume up to `30` units per step)
        
    - Predators **hunt preys** (gain energy from eating them)
        
- **Reproduction**:
    
    - `T = 0.7` (Threshold for reproduction)
        
    - Offspring are placed near parents in the environment
        

---

## **FCM (Fuzzy Cognitive Map) Concepts**

> The medium version **includes a simplified FCM** with key behavioral concepts but avoids excessive complexity.

### **Herbivores (Preys)**

- **Sensitive Concepts**:
    
    - `foodClose`
        
    - `foeClose`
        
    - `energyLow`
        
    - `mateClose`
        
- **Internal Concepts**:
    
    - `fear`
        
    - `hunger`
        
    - `sexualNeeds`
        
- **Motor Concepts**:
    
    - `evasion`
        
    - `searchForFood`
        
    - `breeding`
        

---

### **Carnivores (Predators)**

- **Sensitive Concepts**:
    
    - `preyClose`
        
    - `foodClose`
        
    - `energyLow`
        
    - `mateClose`
        
- **Internal Concepts**:
    
    - `hunting`
        
    - `hunger`
        
    - `sexualNeeds`
        
- **Motor Concepts**:
    
    - `searchForPreys`
        
    - `breeding`
        
    - `resting`