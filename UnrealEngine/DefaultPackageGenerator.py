"""
This Python code is a script that performs various text processing operations on a file named "input_DefaultPackage.txt.txt",
with the ultimate goal of converting it to a JSON file.
"""
import json

# In the first operation, the script reads the contents of the file,
# removes all occurrences of the parentheses characters ("(" and ")"),
# writes the modified text back to the file,
# and truncates the file to its current position.
with open("input_DefaultPackage.txt", "r+") as file:
    input_text = file.read()
    input_text = input_text.replace("(", "").replace(")", "")
    file.seek(0)
    file.write(input_text)
    file.truncate()

# In the second operation, the script reads the contents of the file again,
# replaces all occurrences of commas (",") with new line characters ("\n"),
# writes the modified text back to the file,
# and truncates the file to its current position.
with open("input_DefaultPackage.txt", "r+") as file:
    input_text = file.read()
    input_text = input_text.replace(",", "\n")
    file.seek(0)
    file.write(input_text)
    file.truncate()

# In the third operation, the script reads the contents of the file again,
# removes all lines that start with a double quote (") character,
# writes the modified text back to the file,
# and truncates the file to its current position.
with open("input_DefaultPackage.txt", "r+") as file:
    lines = file.readlines()
    file.seek(0)
    file.truncate()
    for line in lines:
        if not line.startswith('"'):
            file.write(line)

# In the fourth operation, the script reads the contents of the file again,
# writes all lines that start with the string "Size" to the file,
# followed by a new line character ("\n"), and writes all other lines to the file,
# then truncates the file to its current position.
with open("input_DefaultPackage.txt", "r+") as file:
    lines = file.readlines()
    file.seek(0)
    file.truncate()
    for line in lines:
        if line.startswith("Size"):
            file.write(line)
            file.write("\n")
        else:
            file.write(line)

# In the fifth operation, the script reads the contents of the file again,
# removes all occurrences of single quotes ("'"), writes the modified text back to the file,
# and truncates the file to its current position.
with open("input_DefaultPackage.txt", "r+") as file:
    text = file.read()
    text = text.replace("'", "")
    file.seek(0)
    file.write(text)
    file.truncate()

# In the sixth operation, the script reads the contents of the file again,
# replaces all occurrences of the strings " Name=" with '{"name": ', "Mesh=StaticMesh" with ',"path": ',
# and "Size=" with ',"size": ',
# writes the modified text back to the file, and truncates the file to its current position.
with open("input_DefaultPackage.txt", "r+") as file:
    text = file.read()
    text = text.replace(" Name=", '},{"name": ')
    text = text.replace("Mesh=StaticMesh", ',"path": ')
    text = text.replace("Size=", ',"size": ')
    file.seek(0)
    file.write(text)
    file.truncate()

# In the seventh operation, the script reads the contents of the file again,
# replaces the words "Medium", "Small", "Big", "Tiny",
# and "Huge" with their corresponding values as strings in double quotes,
# writes the modified text back to the file, and truncates the file to its current position.
with open("input_DefaultPackage.txt", "r+") as file:
    text = file.read()
    text = text.replace("Medium", '"Medium"')
    text = text.replace("Small", '"Small"')
    text = text.replace("Big", '"Big"')
    text = text.replace("Tiny", '"Tiny"')
    text = text.replace("Huge", '"Huge"')
    file.seek(0)
    file.write(text)
    file.truncate()

# In the eighth operation, the script reads the contents of the file again,
# finds the first occurrence of the string "},"
# and replaces it with '{ "props": [ ', writes the modified text back to the file,
# and truncates the file to its current position.
with open("input_DefaultPackage.txt", "r+") as file:
    text = file.read()
    index = text.find("},")

    if index != -1:
        text = text.replace("},", '{ "props": [ ', 1)

    file.seek(0)
    file.write(text)
    file.truncate()

# In the ninth operation, the script reads the contents of the file again,
# adds a closing curly brace and square bracket to the end of the text (after removing any trailing whitespace),
# writes the modified text back to the file,
# and truncates the file to its current position.
with open("input_DefaultPackage.txt", "r+") as file:
    text = file.read()
    text_with_exclamation = text.strip() + "} ] }"
    file.seek(0)
    file.write(text_with_exclamation)
    file.truncate()

# In the tenth operation, the script reads the contents of the file again,
# writing those contents to a new json file
with open("input_DefaultPackage.txt", "r") as input_file:
    text = input_file.read()

with open("Default.Package.json", "w") as output_file:
    output_file.write(text)

# In the eleven operation, the scropt reads the contents of the file again
# and reformat the code.
with open("Default.Package.json", "r+") as file:
    data = json.load(file)
    file.seek(0)
    json.dump(data, file, indent=3, sort_keys=True)
    file.truncate()
