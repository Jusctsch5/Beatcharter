from enum import Enum
from beatchart.beatchart import Beatchart  # Assuming this is the correct import path

class StepDifficulty(Enum):
    BEGINNER = 1
    EASY = 2
    MEDIUM = 3
    HARD = 4
    CHALLENGE = 5

class ControllerType(Enum):
    ARCADE = 1    # Can employ the back bar for more stability
    PAD = 2       # Soft pad has
    KEYBOARD = 3  # Not limited to two directions

class BuilderProfile:
    def __init__(self, difficulty: StepDifficulty, controller_type: ControllerType,
                 mines: bool, holds: bool, rolls: bool):
        self.difficulty = difficulty
        self.controller_type = controller_type
        self.mines = mines  # Refers to explody bois that reduce your score when hit.
        self.holds = holds  # Refers to a held note that can't be moved off.
        self.rolls = rolls  # Refers to a held note that must be tapped repeatedly.

class StepBuilder:
    @staticmethod
    def build(beatchart_object: Beatchart, difficulty: StepDifficulty, 
              controller_type: ControllerType, mines: bool, holds: bool, rolls: bool) -> str:
        """
        Generate steps from the audio file
        
        Args:
            beatchart_object: Object to generate steps from
            difficulty: Difficulty level of the steps
            controller_type: Type of controller to be used
            mines: Whether to include mines
            holds: Whether to include hold notes
            rolls: Whether to include roll notes
            
        Returns:
            str: String containing the steps
        """
        profile = BuilderProfile(difficulty, controller_type, mines, holds, rolls)
        
        print(f"Generating SM with difficulty: {profile.difficulty}")
        return "" 