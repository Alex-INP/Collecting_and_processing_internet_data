from pymongo import MongoClient


def print_filtered_data(cursor, num):
	for i in cursor.find({"$or": [{"зарплата.от": {"$gt": num}}, {"зарплата.до": {"$gt": num}}]}):
		print(i)


def main():
	mongo_client = MongoClient("localhost", 27017)
	database = mongo_client["vacancy_database"]

	vacancy_cursor = database.vacancy
	number = 100000

	print_filtered_data(vacancy_cursor, number)


if __name__ == "__main__":
	main()
