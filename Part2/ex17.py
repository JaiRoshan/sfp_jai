import random

# Step 1: Ask user their name
name = input("Agent, what is your name? ")

# Step 2 & 3: Create two lists
adjectives = ['Sneaky', 'Silent', 'Brave', 'Clever', 'Fierce', 'Shadowy']
animals = ['Otter', 'Panther', 'Fox', 'Raven', 'Tiger', 'Wolf']

# Step 5: Randomly choose adjective and animal
adjective = random.choice(adjectives)
animal = random.choice(animals)
codename = f"{adjective} {animal}"

# Step 6: Randomly choose a lucky number from 1 to 99
lucky_number = random.randint(1, 99)

# Step 7: Final message
print(f"\nWelcome, Agent {name}.")
print(f"Your codename is: {codename}")
print(f"Your lucky number is: {lucky_number}")
