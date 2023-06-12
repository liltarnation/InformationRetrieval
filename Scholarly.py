import PySimpleGUI as sg
from scholarly import scholarly
from serpapi import GoogleSearch
from urllib.parse import urlsplit, parse_qsl

def retrieveAllPublications(authorId, sort):
    parameters = {
        "engine": "google_scholar_author",
        "author_id": authorId,
        "api_key": "c1b57a5186ae96e31b5966c89200e8fbe3491fb9854ad5089f56feed874dcf57",
        "hl" : "en",
        "num" : 100,
        "sort" : sort
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

headings = ['Title', 'Authors', 'Publication date', '# citations']

layout = [
    [sg.Text("Search author:"), sg.Input(key="-IN-"), sg.FileBrowse()],
    [sg.Text("Sort in terms of:"), sg.Button("Number of citations"), sg.Button("Date of publication")],
    [sg.Frame('Results tables', [[]] ,key="-Tables-", visible=False)],
    [sg.Text("", key = "-Citation-", visible=False)],
    [sg.Submit()],
    [sg.Exit()],
]

window = sg.Window("GUI for Google Scholar Queries", layout)

sort_required = None
total_citation = 0

while True:
    event, value = window.read()
    if event.__contains__('Exit'):
        break
    if event == "Date of publication":
        sort_required = "pubdate"
        sg.popup("We will sort your query results by publication date!")
    if event == "Number of citations":
        sort_required = None
        sg.popup("We will sort your query results by the number of citations!")
    if event == "Submit":
        authorName = value["-IN-"]
        search_query = scholarly.search_author(authorName)
        authorId = next(search_query)["scholar_id"]
        data = retrieveAllPublications(authorId, sort_required)
        table_data = []
        for i in range(len(data)):
            table_data.append([data[i]["title"],
            data[i]["authors"], 
            data[i]["year"],
            data[i]["cited_by"]["value"]])
            if (data[i]["cited_by"]["value"] is not None):
                total_citation = total_citation + data[i]["cited_by"]["value"]
        window.extend_layout(window["-Tables-"], [[sg.Table(values=table_data, headings=headings, max_col_width=35, display_row_numbers=True, row_height=35, num_rows=5)]])
        window["-Citation-"].update("Total citations: " + str(total_citation), visible=True)
        window["-Tables-"].update(visible=True)
        window.visibility_changed()

window.close()