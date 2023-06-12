import PySimpleGUI as sg
from scholarly import scholarly
from scholarly import ProxyGenerator
from serpapi import GoogleSearch
from urllib.parse import urlsplit, parse_qsl
from collections import Counter
import re

#same as previous documentation
def retrieveAllArticles(authorId):
    parameters = {
        "engine": "google_scholar_author",
        "author_id": authorId,
<<<<<<< HEAD
        "api_key": "7d86033b863e4fd5285d7a1565666381593a7df67ff9d83469375cf937015369",
=======
        "api_key": "5e166b8c4d016db55cfc5102c16195abffc661f0c2cfc34755c6a93d119cae5a",
>>>>>>> 053a85e6c973399884ab5f63485f77ac149ba864
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


def retrieveCitedArticles(citationId):
    parameters = {
        "engine": "google_scholar",
        "q": "source:",
        "cites": str(citationId),
<<<<<<< HEAD
        "api_key": "7d86033b863e4fd5285d7a1565666381593a7df67ff9d83469375cf937015369",
=======
        "api_key": "c1b57a5186ae96e31b5966c89200e8fbe3491fb9854ad5089f56feed874dcf57",
>>>>>>> 053a85e6c973399884ab5f63485f77ac149ba864
        "hl" : "en",
        "num" : 100,
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


def retrieveInfo(citations):
    articleSource = []
    publisher = []
    pubYear = []
    for i in citations:
        string = i["publication_info"]['summary']

        # find the publication year
        year = re.search(r"\d{4}", string)
        if year is not None:
            year = year.group()
            pubYear.append(year)
        
        # find publisher
        published = re.split(" - ", string)
        publisher.append(published[len(published)-1])

        # find journal
        journal = re.search(r"\-\s[A-Za-z]+\,", string)
        if journal is not None:
            print(journal)
            journal = journal.group()
            articleSource.append(journal)
        
    return articleSource, pubYear, publisher

def calculateSelfCitations(citationData, specifiedArticle):
    authorNames = specifiedArticle["authors"]
    authorNames = re.split(',', authorNames)
    selfCitation = 0
    nonSelfCitation = 0
    for i in citationData:
        counter = 0
        authors = i["publication_info"]['summary']
        authors = re.split(' - ', authors)
        authors = re.split(', ', authors[0])
        for names in authors:
            if names in authorNames:
                counter += 1
        if counter > 0:
            selfCitation += 1
        else:
            nonSelfCitation += 1
    
    return selfCitation, nonSelfCitation


headings = ['Journal', 'Quantity']
headings1 = ['Publication_year', 'Quantity']
headings2 = ['Publisher', 'Quantity']
headings3 = ['Title', 'Authors', 'Publication Year', 'citations', 'self-citations', 'non-self-citations']

layout = [
    [sg.Text("Search author:"), sg.Input(key="-IN-")],
    [sg.Text("Selected Papers:"), sg.Input(key="-Papers-")],
    [sg.Frame('Results tables', [[]] ,key="-Tables-", visible=False)],
    [sg.Submit()],
    [sg.Exit()],
]

window = sg.Window("GUI for Google Scholar Queries", layout)

year_count = []
venue_count = []
temp = []
publisher_count = []
citations = []

while True:
    event, value = window.read()
    if event == ('Exit'):
        break
    if event == "Submit":

        # takes the numbers of papers from the input, strips it of the special characters and splits based on the commas and dash.
        # Then it sets each string to an int.

        selectedPapers = value["-Papers-"]
        selectedPapers = selectedPapers.strip("[]")
        if '-' in selectedPapers:
            selectedPapers = re.split('-', selectedPapers)
            for i in range(len(selectedPapers)):
                selectedPapers[i] = int(selectedPapers[i])
            selectedPapers = list(range(min(selectedPapers), max(selectedPapers)+1))
        else:
            selectedPapers = re.split(',', selectedPapers)
            for i in range(len(selectedPapers)):
                selectedPapers[i] = int(selectedPapers[i])

        # retrieve author name from input

        authorName = value["-IN-"]
        search_query = scholarly.search_author(authorName)
        author = next(search_query)
        authorId = author["scholar_id"]
        data = retrieveAllArticles(authorId)

        # extract the specific articles selected with the input
        selfCitation = []
        citationDatas = []
        for i in selectedPapers:
            citationId = data[i]["cited_by"]["cites_id"]
            citationData = retrieveCitedArticles(citationId)
            articleVenue, pubyear, articlePublisher = retrieveInfo(citationData)
            selfCitation, nonSelfCitation = calculateSelfCitations(citationData, data[i])
            citationDatas.append([
                data[i]['title'],
                re.split(',', data[i]["authors"]),
                data[i]['year'],
                selfCitation+nonSelfCitation,
                selfCitation,
                nonSelfCitation,
            ])
<<<<<<< HEAD
=======
            articleVenue, pubyear, articlePublisher = retrieveInfo(citationData)
>>>>>>> 053a85e6c973399884ab5f63485f77ac149ba864
        temp = Counter(pubyear)
        for key, value in temp.items(): 
            year_count.append([key, value])
        temp = Counter(articleVenue)
        for key, value in temp.items():
            venue_count.append([key, value])
        temp = Counter(articlePublisher)
        for key, value in temp.items():
            publisher_count.append([key, value])
        window.extend_layout(window["-Tables-"], [[sg.Button("Calculate self citations")]])
        window.extend_layout(window["-Tables-"], [[sg.Table(values=venue_count, headings=headings, max_col_width=35, display_row_numbers=True, row_height=35, num_rows=5)]])
        window.extend_layout(window["-Tables-"], [[sg.Table(values=year_count, headings=headings1, max_col_width=35, display_row_numbers=True, row_height=35, num_rows=5)]])
        window.extend_layout(window["-Tables-"], [[sg.Table(values=publisher_count, headings=headings2, max_col_width=35, display_row_numbers=True, row_height=35, num_rows=5)]])
        window["-Tables-"].update(visible=True)
        window.visibility_changed()
    if event == "Calculate self citations":
        window.extend_layout(window["-Tables-"], [[sg.Table(values=citationDatas, headings=headings3, max_col_width=35, display_row_numbers=True, row_height=35, num_rows=5)]])
        window.visibility_changed()
window.close()