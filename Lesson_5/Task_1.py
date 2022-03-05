import datetime

from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains


def add_to_db(data):
	mongo_client = MongoClient("localhost", 27017)
	database = mongo_client["email_database"]

	email_cursor = database.emails
	email_cursor.delete_many({})

	for i in data:
		email_cursor.insert_one(i)


def add_data(all_news, href):
	driver.get(href)
	letter_data = {"from": None, "date": None, "subject": None, "text": None}

	send_info_el = driver.find_element(By.CLASS_NAME, "letter__author")

	letter_data["from"] = send_info_el.find_element(By.CSS_SELECTOR, "span").get_attribute("title")

	date = send_info_el.find_element(By.CSS_SELECTOR, "div.letter__date").text
	if "Вчера" in date:
		date = date.split(",")
		date[0] = (datetime.datetime.today() - datetime.timedelta(1)).strftime("%d-%m-%Y")
		letter_data["date"] = ",".join(date)
	else:
		letter_data["date"] = date


	letter_data["subject"] = driver.find_element(By.CSS_SELECTOR, "h2.thread-subject").text
	letter_data["text"] = driver.find_element(By.CSS_SELECTOR, "div.letter-body").text

	print(letter_data)
	all_news.append(letter_data)


options = Options()
options.add_argument("start-maximized")

driver = webdriver.Chrome(service=Service("./chromedriver.exe"), options=options)
driver.get("https://mail.ru/")
driver.implicitly_wait(5)

login_btn = driver.find_element(By.CSS_SELECTOR, "button.ph-login")
login_btn.click()

login_url = driver.find_element(By.XPATH, "//iframe[contains(@src, 'login')]").get_attribute("src")
driver.get(login_url)

username_input = driver.find_element(By.CSS_SELECTOR, "input[name='username']")
username_input.send_keys("study.ai_172@mail.ru")

driver.find_element(By.CSS_SELECTOR, "button[data-test-id='next-button']").click()

password_input = driver.find_element(By.CSS_SELECTOR, "input[name='password']")
password_input.send_keys(("NextPassword172#"))

driver.find_element(By.CSS_SELECTOR, "button[data-test-id='submit-button']").click()

all_news = []
letter_hrefs = set()
scroll_action = ActionChains(driver)
break_condition = 0
while True:
	letters = driver.find_elements(By.CSS_SELECTOR, "a.llc")

	for letter in letters:
		letter_hrefs.add(letter.get_attribute("href"))

	if break_condition == len(letter_hrefs):
		break
	else:
		break_condition = len(letter_hrefs)
	scroll_action.move_to_element(letters[-1]).perform()

for href in letter_hrefs:
	add_data(all_news, href)

add_to_db(all_news)


