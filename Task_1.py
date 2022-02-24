import requests
import json

name = "Alex-INP"
result = requests.get(f"https://api.github.com/users/{name}/repos").content

for i in json.loads(result):
	print(i["name"])

with open("results.json", "wb") as file:
	file.write(result)

