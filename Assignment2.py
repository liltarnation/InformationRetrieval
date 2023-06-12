import PySimpleGUI as sg
from scholarly import scholarly
from serpapi import GoogleSearch
from urllib.parse import urlsplit, parse_qsl
from collections import Counter
import re

# retrieveAllPublications: str -> str -> [dict]
# retrieveAllPublications does a google search using parameters retrieve through the user's input. The number of results is set to 100 for maximum efficiency.
# since we can only retrieve 100 publications at a time, we have to use "serpapi_pagination" in order to emulate going to the next page and recieving the next
# 100 results until we have retrieved all publications for that specific author. Everything is saved in a list of dictionaries called author_results_data and returned
# after all publications have been retrieved.
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

# retrieveAllPublishers: str -> [dict]
# retrieveAllPublishers is a function that uses the "organic_results" endpoint in order to retrieve information about the author's article publishers. The function takes
# an author name as the input and uses that as a search query with the special "author:" tag. This will give us the information we need for each article.
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

#Headings used for the table
headings = ['Publication Year', 'Quantity']
headings2 = ['Publisher', 'Quantity']

#Layout of the GUI window
layout = [
    [sg.Text("Search author:"), sg.Input(key="-IN-")],
    [sg.Frame('Results tables', [[]] ,key="-Tables-", visible=False)],
    [sg.Submit()],
    [sg.Exit()],
]

#Creating instance of the GUI window
window = sg.Window("GUI for Google Scholar Queries", layout)

#Initializing variables used in code
year_count = []
temp = []
table_data = []
publisher_count = []

while True:
    event, value = window.read()
    if event == 'Exit':
        break
    if event == "Submit":
        #Takes authorname has input
        authorName = value["-IN-"]
        # Use scholarly.search.author in order to retrieve the scholar_id which will be used in retrieveAllPublications
        search_query = scholarly.search_author(authorName)
        authorId = next(search_query)
        dataArticles = retrieveAllPublications(authorId["scholar_id"])
        dataPublishers = retrieveAllPublishers(authorName)
        pubUrl = []
        #Retrieve the correct information about one of the fields which will give us the publisher
        for i in range(len(dataPublishers)):
            x = re.split(" - ", dataPublishers[i]["publication_info"]["summary"])
            pubUrl.append(x[len(x)-1])
        #Use Counter function in order to count all occurences in the list
        temp = Counter(pubUrl) 
        #Create list of lists that will work for the table
        for key, value in temp.items():
            publisher_count.append([key, value])
        #Append only year to list in order to use counter function to find occurences of the years the articles have been published
        for i in range(len(dataArticles)):
            table_data.append(dataArticles[i]["year"])
        #Counter function again
        temp = Counter(table_data)
        for key, value in temp.items():
            year_count.append([key, value])
        # Here we finally extend the window and input the corresponding information.
        window.extend_layout(window["-Tables-"], [[sg.Table(values=year_count, headings=headings, max_col_width=35, display_row_numbers=True, row_height=35, num_rows=5)]])
        window.extend_layout(window["-Tables-"], [[sg.Table(values=publisher_count, headings=headings2, max_col_width=35, display_row_numbers=True, row_height=35, num_rows=5)]])
        window["-Tables-"].update(visible=True)
        #We notify the window that the visibility has changed such that it can refresh the window.
        window.visibility_changed()
#Finally, the window closes when the user has pressed exit.
window.close()