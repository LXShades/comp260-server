from Game import Game

import random

def main():
    Game()  # Create the game


# Call the main function!
if __name__ == "__main__":
    main()

# Probability experiment
'''succeeded = 0
    total = 10000
    totalWhereOneRollsIn = 0

    for i in range(total):
        # Roll two dice
        diceA = random.randint(1, 6)
        diceB = random.randint(1, 6)

        # Random chance of one or both of the dice rolling into the player's view
        whichOnes = random.randint(0, 1) | (random.randint(0, 1) << 1)

        # ignore cases where no or both dice roll into view

        if whichOnes == 1:
            # Dice A rolls into view
            if diceA == 1:
                if diceB == 1:
                    succeeded += 1
                totalWhereOneRollsIn += 1
        elif whichOnes == 2:
            # Dice B rolls into view
            if diceB == 1:
                if diceA == 1:
                    succeeded += 1
                totalWhereOneRollsIn += 1

    print("Succeeded/total where one dice rolls in " + str(succeeded/totalWhereOneRollsIn * 100))

    input("continue")'''