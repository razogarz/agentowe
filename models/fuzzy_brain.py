"""
Fuzzy Logic Based Decision Making for Predator-Prey Agents

This module implements a fuzzy logic system for making decisions
in the predator-prey simulation. It provides a more nuanced behavior
than simple if-else rules.
"""

import random
import numpy as np
from collections import defaultdict

class FuzzyVariable:
    """
    Represents a fuzzy variable with multiple fuzzy sets
    """
    def __init__(self, name, sets=None):
        self.name = name
        self.sets = sets or {}  # Dictionary of set_name: membership_function
        
    def add_set(self, name, membership_function):
        """Add a fuzzy set with its membership function"""
        self.sets[name] = membership_function
        
    def fuzzify(self, value):
        """
        Calculate membership degrees for a crisp value
        Returns a dictionary of {set_name: membership_degree}
        """
        result = {}
        for set_name, membership_function in self.sets.items():
            result[set_name] = membership_function(value)
        return result


class FuzzyRule:
    """
    Represents a fuzzy rule like:
    IF energy IS low AND prey IS near THEN move IS fast
    """
    def __init__(self, antecedents, consequent, weight=1.0):
        """
        Initialize a fuzzy rule
        
        Args:
            antecedents: Dictionary of {variable_name: set_name}
            consequent: Tuple of (variable_name, set_name, action)
            weight: Rule weight between 0 and 1
        """
        self.antecedents = antecedents
        self.consequent = consequent
        self.weight = weight
        
    def evaluate(self, fuzzified_inputs):
        """
        Evaluate the rule given fuzzified inputs
        Returns the firing strength of the rule
        """
        # Get all membership degrees for antecedents
        degrees = []
        for var_name, set_name in self.antecedents.items():
            if var_name in fuzzified_inputs and set_name in fuzzified_inputs[var_name]:
                degrees.append(fuzzified_inputs[var_name][set_name])
            else:
                # If any antecedent is not satisfied, the rule doesn't fire
                return 0.0
                
        # Use the minimum for AND operation (Mamdani method)
        if degrees:
            return min(degrees) * self.weight
        return 0.0


class FuzzyBrain:
    """
    Base class for fuzzy logic based decision making
    """
    def __init__(self):
        self.input_variables = {}
        self.output_variables = {}
        self.rules = []
        
    def add_input_variable(self, name, sets=None):
        """Add an input variable to the fuzzy system"""
        var = FuzzyVariable(name, sets)
        self.input_variables[name] = var
        return var
        
    def add_output_variable(self, name, sets=None):
        """Add an output variable to the fuzzy system"""
        var = FuzzyVariable(name, sets)
        self.output_variables[name] = var
        return var
        
    def add_rule(self, antecedents, consequent, weight=1.0):
        """Add a fuzzy rule to the system"""
        rule = FuzzyRule(antecedents, consequent, weight)
        self.rules.append(rule)
        
    def fuzzify_inputs(self, input_values):
        """
        Convert crisp input values to fuzzy values
        
        Args:
            input_values: Dictionary of {variable_name: crisp_value}
            
        Returns:
            Dictionary of {variable_name: {set_name: membership_degree}}
        """
        fuzzified = {}
        for var_name, value in input_values.items():
            if var_name in self.input_variables:
                fuzzified[var_name] = self.input_variables[var_name].fuzzify(value)
        return fuzzified
        
    def infer(self, fuzzified_inputs):
        """
        Apply fuzzy inference to get output values
        """
        # Dictionary to hold firing strengths for each output variable and set
        output_strengths = defaultdict(lambda: defaultdict(float))
        
        # Evaluate all rules
        for rule in self.rules:
            firing_strength = rule.evaluate(fuzzified_inputs)
            if firing_strength > 0:
                output_var, output_set, action = rule.consequent
                # Use maximum for rules with same consequent
                current = output_strengths[output_var][output_set]
                output_strengths[output_var][output_set] = max(current, firing_strength)
                
        return output_strengths, self._get_actions(output_strengths)
    
    def _get_actions(self, output_strengths):
        """
        Extract actions from output strengths - override in subclasses
        """
        return {}
        
    def decide(self, input_values):
        """
        Make a decision based on input values
        Returns a dictionary of actions and their values
        """
        fuzzified = self.fuzzify_inputs(input_values)
        _, actions = self.infer(fuzzified)
        return actions


class HerbivoreBrain(FuzzyBrain):
    """
    Fuzzy brain implementation for herbivores
    """
    def __init__(self):
        super().__init__()
        self._setup_variables()
        self._setup_rules()
        
    def _setup_variables(self):
        # Input Variables
        
        # Energy level
        energy = self.add_input_variable("energy")
        energy.add_set("low", lambda x: max(0, min(1, (0.3 - x) / 0.3)) if x < 0.3 else 0)
        energy.add_set("medium", lambda x: max(0, min((x - 0.1) / 0.3, (0.7 - x) / 0.3)) if 0.1 <= x <= 0.7 else 0)
        energy.add_set("high", lambda x: max(0, min(1, (x - 0.5) / 0.5)) if x > 0.5 else 0)
        energy.add_set("full", lambda x: max(0, min(1, (x - 0.85) / 0.15)) if x > 0.85 else 0)  # Added "full" state
        
        # Food proximity
        food = self.add_input_variable("food_proximity")
        food.add_set("far", lambda x: max(0, min(1, (3 - x) / 3)) if x < 3 else 0)
        food.add_set("medium", lambda x: max(0, min((x - 1) / 2, (5 - x) / 2)) if 1 <= x <= 5 else 0)
        food.add_set("near", lambda x: max(0, min(1, (x - 3) / 3)) if x > 3 else 0)
        
        # Predator proximity - REDUCED detection ranges to be more balanced
        predator = self.add_input_variable("predator_proximity")
        # Reduced detection ranges to make herbivores less effective at escaping
        predator.add_set("far", lambda x: max(0, min(1, (4 - x) / 4)) if x < 4 else 0)  # Reduced from 5 to 4
        predator.add_set("medium", lambda x: max(0, min((x - 1.5) / 2.5, (6 - x) / 2.5)) if 1.5 <= x <= 6 else 0)  # Adjusted range
        predator.add_set("near", lambda x: max(0, min(1, (x - 3) / 3)) if x > 3 else 0)  # Reduced from 4 to 3
        # Very near detection remains the same for imminent danger
        predator.add_set("very_near", lambda x: max(0, min(1, (2 - x) / 2)) if x < 2 else 0)  # Reduced from 3 to 2
        
        # Output Variables
        
        # Movement behavior
        movement = self.add_output_variable("movement")
        movement.add_set("flee", lambda x: 0)  # Just a placeholder, actual value doesn't matter
        movement.add_set("sprint", lambda x: 0)  # New emergency escape mode - faster but costs more energy
        movement.add_set("wander", lambda x: 0)
        movement.add_set("seek_food", lambda x: 0)
        movement.add_set("seek_partner", lambda x: 0)  # New movement option for finding partners
        
        # Reproduction tendency
        reproduction = self.add_output_variable("reproduction")
        reproduction.add_set("no", lambda x: 0)
        reproduction.add_set("yes", lambda x: 0)
        
    def _setup_rules(self):
        # Movement rules
        
        # When predator is very near, sprint away (emergency escape)
        self.add_rule(
            {"predator_proximity": "very_near"},
            ("movement", "sprint", "sprint"),
            weight=1.0  # Highest priority - immediate danger
        )
        
        # When predator is near, flee regardless of other conditions
        self.add_rule(
            {"predator_proximity": "near"},
            ("movement", "flee", "flee"),
            weight=0.85  # Reduced from 0.9
        )
        
        # When predator is at medium distance, flee if energy is low or medium (reduced weights)
        self.add_rule(
            {"predator_proximity": "medium", "energy": "low"},
            ("movement", "flee", "flee"),
            weight=0.7  # Reduced from 0.8
        )
        
        self.add_rule(
            {"predator_proximity": "medium", "energy": "medium"},
            ("movement", "flee", "flee"),
            weight=0.6  # Reduced from 0.7
        )
        
        # New rule: Medium energy, medium predator distance, and food is near -> seek food (instead of fleeing)
        self.add_rule(
            {"energy": "medium", "predator_proximity": "medium", "food_proximity": "near"},
            ("movement", "seek_food", "seek_food"),
            weight=0.65  # Slightly higher than fleeing with medium energy
        )
        
        # Low energy and food near -> seek food
        self.add_rule(
            {"energy": "low", "food_proximity": "near", "predator_proximity": "far"},
            ("movement", "seek_food", "seek_food"),
            weight=0.9
        )
        
        # Low energy and food medium -> seek food
        self.add_rule(
            {"energy": "low", "food_proximity": "medium", "predator_proximity": "far"},
            ("movement", "seek_food", "seek_food"),
            weight=0.8
        )
        
        # Medium energy and food near -> seek food
        self.add_rule(
            {"energy": "medium", "food_proximity": "near", "predator_proximity": "far"},
            ("movement", "seek_food", "seek_food"),
            weight=0.7
        )
        
        # Medium energy and no immediate danger -> wander
        self.add_rule(
            {"energy": "medium", "predator_proximity": "far"},
            ("movement", "wander", "wander"),
            weight=0.6
        )
        
        # High energy and no immediate danger -> seek partners
        self.add_rule(
            {"energy": "high", "predator_proximity": "far"},
            ("movement", "seek_partner", "seek_partner"),
            weight=0.7  # Higher weight than wandering
        )
        
        # Full energy and no immediate danger -> seek partners with high priority
        self.add_rule(
            {"energy": "full", "predator_proximity": "far"},
            ("movement", "seek_partner", "seek_partner"),
            weight=0.9  # Very high priority when full
        )
        
        # Full energy and medium predator distance -> still seek partners
        self.add_rule(
            {"energy": "full", "predator_proximity": "medium"},
            ("movement", "seek_partner", "seek_partner"),
            weight=0.6  # Will seek even with some risk
        )
        
        # Reproduction rules - MODIFIED to increase breeding chance
        
        # High energy and no predators -> consider reproduction (increased weight)
        self.add_rule(
            {"energy": "high", "predator_proximity": "far"},
            ("reproduction", "yes", "breed"),
            weight=0.9  # Increased from 0.7
        )
        
        # Full energy -> always try to reproduce
        self.add_rule(
            {"energy": "full"},
            ("reproduction", "yes", "breed"),
            weight=1.0  # Maximum priority when full
        )
        
        # Medium energy and no predators -> still consider reproduction (new rule)
        self.add_rule(
            {"energy": "medium", "predator_proximity": "far"},
            ("reproduction", "yes", "breed"),
            weight=0.6  # New rule to increase breeding
        )
        
        # Not high energy or predators nearby -> don't reproduce
        self.add_rule(
            {"energy": "low"},
            ("reproduction", "no", "no_breed"),
            weight=0.7  # Reduced from 0.8 to allow more breeding
        )
        
        self.add_rule(
            {"predator_proximity": "near"},
            ("reproduction", "no", "no_breed"),
            weight=0.9
        )
        
    def _get_actions(self, output_strengths):
        """Convert inference results to concrete actions"""
        actions = {}
        
        # Determine movement action
        movement_options = output_strengths.get("movement", {})
        max_strength = 0
        best_movement = "wander"  # Default
        
        for move, strength in movement_options.items():
            if strength > max_strength:
                max_strength = strength
                if move == "sprint":
                    best_movement = "sprint"  # Emergency escape takes precedence
                elif move == "flee":
                    best_movement = "flee"
                elif move == "seek_food":
                    best_movement = "seek_food"
                elif move == "seek_partner":
                    best_movement = "seek_partner"
                else:
                    best_movement = "wander"
                    
        actions["movement"] = best_movement
        
        # Determine reproduction action - MODIFIED
        repro_options = output_strengths.get("reproduction", {})
        breed_strength = repro_options.get("yes", 0)
        no_breed_strength = repro_options.get("no", 0)
        
        # Lower threshold for breeding (from 0.5 to 0.3)
        if breed_strength > no_breed_strength and breed_strength > 0.3:
            actions["breed"] = True
        else:
            actions["breed"] = False
            
        return actions


class PredatorBrain(FuzzyBrain):
    """
    Fuzzy brain implementation for predators
    """
    def __init__(self):
        super().__init__()
        self._setup_variables()
        self._setup_rules()
        
    def _setup_variables(self):
        # Input Variables
        
        # Energy level
        energy = self.add_input_variable("energy")
        energy.add_set("low", lambda x: max(0, min(1, (0.3 - x) / 0.3)) if x < 0.3 else 0)
        energy.add_set("medium", lambda x: max(0, min((x - 0.1) / 0.3, (0.7 - x) / 0.3)) if 0.1 <= x <= 0.7 else 0)
        energy.add_set("high", lambda x: max(0, min(1, (x - 0.5) / 0.5)) if x > 0.5 else 0)
        
        # Prey proximity - MODIFIED to increase perceived proximity
        prey = self.add_input_variable("prey_proximity")
        # Modified membership functions to consider prey at closer proximity (more aggressive)
        prey.add_set("far", lambda x: max(0, min(1, (4 - x) / 4)) if x < 4 else 0)  # Increased upper bound
        prey.add_set("medium", lambda x: max(0, min((x - 1) / 2, (6 - x) / 2)) if 1 <= x <= 6 else 0)  # Expanded range
        prey.add_set("near", lambda x: max(0, min(1, (x - 2) / 4)) if x > 2 else 0)  # Reduced lower threshold
        
        # Prey count (in vicinity)
        prey_count = self.add_input_variable("prey_count")
        prey_count.add_set("few", lambda x: max(0, min(1, (2 - x) / 2)) if x < 2 else 0)
        prey_count.add_set("some", lambda x: max(0, min((x - 1) / 2, (5 - x) / 2)) if 1 <= x <= 5 else 0)
        prey_count.add_set("many", lambda x: max(0, min(1, (x - 3) / 3)) if x > 3 else 0)
        
        # Output Variables
        
        # Hunting behavior
        hunting = self.add_output_variable("hunting")
        hunting.add_set("conserve", lambda x: 0)  # Just a placeholder
        hunting.add_set("stalk", lambda x: 0)
        hunting.add_set("chase", lambda x: 0)
        
        # Reproduction tendency
        reproduction = self.add_output_variable("reproduction")
        reproduction.add_set("no", lambda x: 0)
        reproduction.add_set("yes", lambda x: 0)
        
    def _setup_rules(self):
        # Hunting rules - MODIFIED to increase aggressiveness
        
        # Low energy and prey near -> chase aggressively (increased weight)
        self.add_rule(
            {"energy": "low", "prey_proximity": "near"},
            ("hunting", "chase", "chase"),
            weight=1.0  # Increased from 0.9
        )
        
        # Low energy and prey medium -> stalk prey
        self.add_rule(
            {"energy": "low", "prey_proximity": "medium"},
            ("hunting", "chase", "chase"),  # Changed from stalk to chase
            weight=0.9  # Increased from 0.8
        )
        
        # Medium energy and prey near -> chase
        self.add_rule(
            {"energy": "medium", "prey_proximity": "near"},
            ("hunting", "chase", "chase"),
            weight=0.9  # Increased from 0.8
        )
        
        # Medium energy and many prey -> chase
        self.add_rule(
            {"energy": "medium", "prey_count": "many"},
            ("hunting", "chase", "chase"),
            weight=0.8  # Increased from 0.7
        )
        
        # Medium energy and some prey -> stalk (new rule)
        self.add_rule(
            {"energy": "medium", "prey_count": "some"},
            ("hunting", "stalk", "stalk"),
            weight=0.7  # New rule
        )
        
        # High energy and prey near -> chase (new rule)
        self.add_rule(
            {"energy": "high", "prey_proximity": "near"},
            ("hunting", "chase", "chase"),
            weight=0.9  # New rule for more aggressive behavior
        )
        
        # High energy, prey far and few -> conserve energy
        self.add_rule(
            {"energy": "high", "prey_proximity": "far", "prey_count": "few"},
            ("hunting", "conserve", "conserve"),
            weight=0.5  # Reduced from 0.6 to make less likely to conserve
        )
        
        # Any energy level, prey nearby -> chase
        self.add_rule(
            {"prey_proximity": "near"},
            ("hunting", "chase", "chase"),
            weight=0.8  # Increased from 0.7
        )
        
        # Reproduction rules
        
        # High energy -> consider reproduction
        self.add_rule(
            {"energy": "high"},
            ("reproduction", "yes", "breed"),
            weight=0.7
        )
        
        # Low/medium energy -> don't reproduce
        self.add_rule(
            {"energy": "low"},
            ("reproduction", "no", "no_breed"),
            weight=0.9
        )
        
        self.add_rule(
            {"energy": "medium"},
            ("reproduction", "no", "no_breed"),
            weight=0.6
        )
        
    def _get_actions(self, output_strengths):
        """Convert inference results to concrete actions"""
        actions = {}
        
        # Determine hunting action
        hunting_options = output_strengths.get("hunting", {})
        max_strength = 0
        best_hunting = "conserve"  # Default
        
        for hunt, strength in hunting_options.items():
            if strength > max_strength:
                max_strength = strength
                if hunt == "chase":
                    best_hunting = "chase"
                elif hunt == "stalk":
                    best_hunting = "stalk"
                else:
                    best_hunting = "conserve"
                    
        actions["hunting"] = best_hunting
        
        # Determine reproduction action
        repro_options = output_strengths.get("reproduction", {})
        breed_strength = repro_options.get("yes", 0)
        no_breed_strength = repro_options.get("no", 0)
        
        # Only breed if the yes strength is higher and above threshold
        if breed_strength > no_breed_strength and breed_strength > 0.5:
            actions["breed"] = True
        else:
            actions["breed"] = False
            
        return actions 