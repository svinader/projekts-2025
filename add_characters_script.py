import json
import os

FILENAME = 'characters_data.json'

#Ja fails neeksistē, izveido tukšu JSON failu
if not os.path.exists(FILENAME):
    with open(FILENAME, 'w') as f:
        json.dump({}, f, indent=2)

with open(FILENAME, 'r') as f:
    data = json.load(f)

name = input("Enter the name of the brawler: ")
rarity = input("Enter the rarity (e.g., legendary, epic, rare): ")
image = input("Paste the image URL: ")

gadget = input("Enter the gadget: ")
star_power = input("Enter the star power: ")
gear_1 = input("Enter the first gear: ")
gear_2 = input("Enter the second gear: ")

data[name] = {
    "rarity": rarity,
    "image": image,
    "builds": [
        f"Gadget: {gadget}",
        f"Star Power: {star_power}",
        f"Gears: {gear_1} and {gear_2}"
    ]
}

with open(FILENAME, 'w') as f:
    json.dump(data, f, indent=2)

print(f"Character '{name}' was successfully added!")
