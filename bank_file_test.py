# Writing data inside our new project folder
with open("bank_data.txt", "w") as file:
    file.write("Account #101 | Owner: Anna | Balance: 550.0€\n")
    file.write("Account #102 | Owner: Bob | Balance: 350.0€\n")

print("Data successfully saved!")