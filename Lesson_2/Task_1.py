import threading
from pprint import pprint
from queue import Queue

from bs4 import BeautifulSoup
import requests
import re


def print_global_result(global_result):
    for page_dict in global_result:
        print("-" * 160)
        print(f"Страница: {page_dict['страница']}")
        for i in page_dict["данные"]:
            print("-" * 80)
            for key, val in i.items():
                print(f"{key}: {val}")


def get_page_deltas(total_pages, threads_count):
    thread_pagecount = total_pages // threads_count
    final_list = [[0, thread_pagecount]]
    last_thread_pagecount = total_pages % threads_count
    page_count = thread_pagecount
    while page_count + thread_pagecount <= total_pages:
        final_list.append([page_count + 1, page_count + thread_pagecount])
        page_count = page_count + thread_pagecount
    final_list[-1][-1] += last_thread_pagecount
    return final_list


class MultipageProcessor(threading.Thread):
    def __init__(
        self,
        pages_delta,
        target_site,
        search_url_part,
        headers,
        params,
        global_result,
        bad_link=False
    ):
        super().__init__()
        self.pages_delta = pages_delta
        self.target_site = target_site
        self.search_url_part = search_url_part
        self.headers = headers
        self.params = params
        self.global_result = global_result
        self.bad_link = bad_link

    def run(self):
        for i in range(self.pages_delta[0], self.pages_delta[1]):
            self.params["page"] = i
            if self.bad_link:
                result = requests.get(
                    f"https://hh.ru/search/vacancy?clusters=true&area=1&ored_clusters=true&enable_snippets=true&salary=&text=python&page={i}&hhtmFrom=vacancy_search_list",
                    headers=self.headers).text
            else:
                result = requests.get(
                    f"{self.target_site}{self.search_url_part}",
                    headers=self.headers,
                    params=self.params).text

            page = BeautifulSoup(result, "html.parser")
            with list_lock:
                self.global_result.append(self.process_page(page, i))

        print(
            f"Thread: {threading.currentThread().getName()} finished. Page delta: {self.pages_delta[0]}-{self.pages_delta[1]}")

    def process_page(self, page, page_number):

        final_dict = {"страница": page_number + 1, "данные": []}
        elements = page.find_all(
            "div", {"class": "vacancy-serp-item vacancy-serp-item_redesigned"})
        for element in elements:
            final_dict["данные"].append(
                self.process_vacancy_element(
                    element, self.target_site))
        return final_dict

    def process_vacancy_element(self, element, site):
        final_dict = {
            "наименование": None,
            "зарплата": None,
            "ссылка_на_вакансию": None,
            "сайт_вакансии": site}
        name_el = element.find("a", {"data-qa": "vacancy-serp__vacancy-title"})
        reward_el = element.find(
            "span", {
                "data-qa": "vacancy-serp__vacancy-compensation"})

        final_dict["наименование"] = name_el.getText()
        final_dict["ссылка_на_вакансию"] = name_el.attrs["href"]
        final_dict["зарплата"] = self.process_reward(reward_el)
        return final_dict

    def process_reward(self, reward):
        final_dict = {"от": None, "до": None, "валюта": None}
        if reward:
            reward = reward.get_text().replace("\u202f", " ")

            numbers = re.findall(r"(?:\d+\s)+\d+", reward)
            currency = re.search(r"\b\w+(?=[.]?$)", reward)

            if currency:
                final_dict["валюта"] = currency.group(0)
            if numbers:
                if re.search(r"от", reward):
                    final_dict["от"] = numbers[0]
                if re.search(r"до", reward):
                    final_dict["до"] = numbers[-1]
                if re.search(r"–", reward):
                    final_dict["от"] = numbers[0]
                    final_dict["до"] = numbers[-1]
        return final_dict


def main():
    target_site = "https://hh.ru"
    search_url_part = "/search/vacancy"
    search_text = "python"
    page = "0"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"}

    # params = {
    # 	"area": "1",
    # 	"fromSearchLine": "True",
    # 	"text": search_text,
    # 	"page": page,
    # 	"hhtmFrom": "vacancy_search_list"}

    params = {
        "clusters": True,
        "area": 1,
        "ored_clusters": True,
        "enable_snippets": True,
        "salary": "",
        "text": search_text,
		"fromSearchLine": True,
        "page": page,
        "hhtmFrom": "vacancy_search_list"}

    result = requests.get(
        f"{target_site}{search_url_part}",
        headers=headers,
        params=params).content

    site = BeautifulSoup(result, "html.parser")
    total_pages = int(site.select(
        "a.bloko-button[rel=nofollow][data-qa=pager-page]")[-1].find("span").text)

    one_thread = False
    number_of_threads = 8

    global_result = []
    threads = []

    global list_lock
    list_lock = threading.Lock()

    if one_thread:
        thread_1 = MultipageProcessor(
            [0, total_pages], target_site, search_url_part, headers, params, global_result, bad_link=False)
        thread_1.start()
        thread_1.join()
    else:
        thread_page_deltas = get_page_deltas(total_pages, number_of_threads)
        print(thread_page_deltas)
        for delta in thread_page_deltas:
            threads.append(
                MultipageProcessor(
                    delta,
                    target_site,
                    search_url_part,
                    headers,
                    params,
                    global_result,
					bad_link=True))

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

    global_result = sorted(global_result, key=lambda a: a["страница"])

    print_global_result(global_result)


if __name__ == "__main__":
    main()
