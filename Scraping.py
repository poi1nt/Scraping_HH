import requests
import fake_headers
import bs4
import re
import json


def get_html_HH():
    url = "https://spb.hh.ru/search/vacancy?text=python&area=1&area=2"
    headers = fake_headers.Headers(browser="chrome", os="lin")
    headers_dict = headers.generate()

    response = requests.get(url, headers=headers_dict).text
    soup = bs4.BeautifulSoup(response, "lxml")
    jobs = soup.find_all("a", class_="serp-item__title")
    return jobs, headers_dict


def get_href_job_vacancy(jobs, headers_dict):
    href_list_all = []
    href_list = []
    for job in jobs:
        job_href = job.get("href")
        href_list_all.append(job_href)

    for href in href_list_all:
        count = 0
        response_job = requests.get(url=href, headers=headers_dict).text
        soup = bs4.BeautifulSoup(response_job, "lxml")
        skills = soup.find_all("div", class_="bloko-tag bloko-tag_inline")
        for skill in skills:
            if re.search(r"Django|Flask", skill.text) is not None:
                count += 1
        if count > 0:
            href_list.append(href)
    return href_list


def get_data(href_list, headers_dict):
    job_list = []
    for href in href_list:
        res_job = requests.get(url=href, headers=headers_dict).text
        soup = bs4.BeautifulSoup(res_job, "lxml")
        name = (
            soup.find("div", class_="vacancy-title")
            .find("h1", class_="bloko-header-section-1")
            .text
        )
        company = soup.find("div", class_="vacancy-company-details").text
        city = (
            soup.find(
                "a",
                class_="bloko-link bloko-link_kind-tertiary bloko-link_disable-visited",
            )
            .find("span")
            .text.split(",")
        )
        salary = soup.find(
            "span", class_="bloko-header-section-2 bloko-header-section-2_lite"
        ).text
        job_dict = {
            name: {
                "Название компании": company,
                "Город": city[0],
                "Зарплата": salary,
                "Ссылка": href,
            }
        }
        job_list.append(job_dict)
    return job_list


def get_json(job_list):
    with open("job_HH.json", "w+", encoding="utf-8") as file:
        json.dump(job_list, file, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    jobs, headers_dict = get_html_HH()
    href_list = get_href_job_vacancy(jobs, headers_dict)
    job_list = get_data(href_list, headers_dict)
    get_json(job_list)
