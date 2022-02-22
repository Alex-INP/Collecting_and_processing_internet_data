import requests

name = "Alex-INP"
result = requests.get(f"https://api.github.com/users/{name}/repos").content

with open("results.json", "wb") as file:
	file.write(result)

