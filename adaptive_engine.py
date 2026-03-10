import math
from typing import List
from models import UserResponse

class AdaptiveEngine:
    @staticmethod
    def calculate_probability(ability: float, difficulty: float) -> float:
        """
        Calculates the probability of a correct response based on IRT (1PL Model).
        P(theta) = 1 / (1 + exp(-(theta - difficulty)))
        """
        return 1 / (1 + math.exp(-(ability - difficulty)))

    @staticmethod
    def update_ability(current_ability: float, difficulty: float, is_correct: bool) -> float:
        """
        Updates the ability score using a simplified Maximum Likelihood Estimation approach.
        theta_new = theta_old + K * (Outcome - P(correct))
        K is a dampening factor to prevent extreme jumps.
        """
        k_factor = 0.5  # Sensitivity of update
        p_correct = AdaptiveEngine.calculate_probability(current_ability, difficulty)
        outcome = 1.0 if is_correct else 0.0
        
        new_ability = current_ability + k_factor * (outcome - p_correct)
        
        # Clamp ability score between 0.1 and 1.0
        return max(0.1, min(1.0, new_ability))

    @staticmethod
    def get_next_question_difficulty(current_ability: float) -> float:
        """
        In 1D adaptive logic, we aim for questions near the estimated ability.
        """
        return current_ability
