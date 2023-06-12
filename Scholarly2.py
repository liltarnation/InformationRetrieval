import PySimpleGUI as sg
from scholarly import scholarly
from serpapi import GoogleSearch
from urllib.parse import urlsplit, parse_qsl
from collections import Counter
import re

def retrieveAllPublications(authorId):
    parameters = {
        "engine": "google_scholar_author",
        "author_id": authorId,
        "api_key": "c1b57a5186ae96e31b5966c89200e8fbe3491fb9854ad5089f56feed874dcf57",
        "hl" : "en",
        "num" : 100,
    }

    author_results_data = []

    search = GoogleSearch(parameters)
    while True:
        results = search.get_dict()
        for article in results.get("articles", []):
            author_results_data.append(article)
        if "next" in results.get("serpapi_pagination", []):
            search.params_dict.update(dict(parse_qsl(urlsplit(results.get("serpapi_pagination").get("next")).query)))
        else:
            break
    return author_results_data

def retrieveAllPublishers(authorName):
    parameters = {
        "engine": "google_scholar",
        "q": "author:"+authorName,
        "api_key": "c1b57a5186ae96e31b5966c89200e8fbe3491fb9854ad5089f56feed874dcf57",
        "h1" : "en",
        "num" : 100
    }

    organic_results_data = []

    search = GoogleSearch(parameters)
    while True:
        results = search.get_dict()
        for organic in results.get("organic_results", []):
            organic_results_data.append(organic)
        if "next" in results.get("serpapi_pagination", []):
            search.params_dict.update(dict(parse_qsl(urlsplit(results.get("serpapi_pagination").get("next")).query)))
        else:
            break
    return organic_results_data

headings = ['Publication Year', 'Quantity']
headings2 = ['Publisher', 'Quantity']

layout = [
    [sg.Text("Search author:"), sg.Input(key="-IN-"), sg.FileBrowse()],
    [sg.Frame('Results tables', [[]] ,key="-Tables-", visible=False)],
    [sg.Submit()],
    [sg.Exit()],
]

window = sg.Window("GUI for Google Scholar Queries", layout)

year_count = []
temp = []
table_data = []
publisher_count = []

while True:
    event, value = window.read()
    if event == 'Exit':
        break

    if event == "Submit":
        authorName = value["-IN-"]
        search_query = scholarly.search_author(authorName)
        #
        #
        authorId = next(search_query)
        dataArticles = retrieveAllPublications(authorId["scholar_id"])
        dataPublishers = retrieveAllPublishers(authorName)
        pubUrl = []
        for i in range(len(dataPublishers)):
            x = re.split(" - ", dataPublishers[i]["publication_info"]["summary"])
            pubUrl.append(x[len(x)-1])
        temp = Counter(pubUrl) 
        
        for key, value in temp.items():
            publisher_count.append([key, value])
        for i in range(len(dataArticles)):
            table_data.append(dataArticles[i]["year"])
        temp = Counter(table_data)
        for key, value in temp.items():
            year_count.append([key, value])
        window.extend_layout(window["-Tables-"], [[sg.Table(values=year_count, headings=headings, max_col_width=35, display_row_numbers=True, row_height=35, num_rows=5)]])
        window.extend_layout(window["-Tables-"], [[sg.Table(values=publisher_count, headings=headings2, max_col_width=35, display_row_numbers=True, row_height=35, num_rows=5)]])
        window["-Tables-"].update(visible=True)
        window.visibility_changed()

window.close()