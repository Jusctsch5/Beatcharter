package builders;

import beatchart.Beatchart;

public class StepBuilder {

    public enum StepDifficulty
    {
        BEGINNER, EASY, MEDIUM, HARD, CHALLENGE;
    }

    public enum ControllerType
    {
        ARCADE,   // Can employ the back bar for more stability
        PAD,      // Soft pad has
        KEYBOARD; // Not limited to two directions
    }

    static class BuilderProfile {
        public BuilderProfile(StepDifficulty iDifficulty, ControllerType iControllerType,
                              boolean iMines, boolean iHolds, boolean iRolls) {
            difficulty = iDifficulty;
            controllerType = iControllerType;
            mines = iMines; // Refers to explody bois that reduce your score when hit.
            holds = iHolds; // Refers to a held note that can't be moved off.
            rolls = iRolls; // Refers to a held note that must be tapped repeatedly.
        }

        StepDifficulty difficulty;
        ControllerType controllerType;
        boolean mines;
        boolean holds;
        boolean rolls;
    }

    /**
     * @param audioFile - File to generate steps from
     * @return String containing the steps
     */
    public static String Build(Beatchart object, StepDifficulty iDifficulty, ControllerType iControllerType,
                               boolean iMines, boolean iHolds, boolean iRolls) {

        BuilderProfile profile = new BuilderProfile(iDifficulty, iControllerType, iMines, iHolds, iRolls);


        System.out.println("Generating SM with difficulty: " + profile.difficulty);
        return "";
    }
}
