import PySimpleGUI as sg
from scholarly import scholarly
from serpapi import GoogleSearch
from urllib.parse import urlsplit, parse_qsl

def retrieveAllPublications(authorId, sort):
    parameters = {
        "engine": "google_scholar_author",
        "author_id": authorId,
        "api_key": "5e166b8c4d016db55cfc5102c16195abffc661f0c2cfc34755c6a93d119cae5a",
        "hl" : "en",
        "num" : 100,
        "sort" : sort
    }

    search = GoogleSearch(parameters)
    results = search.get_dict()

    author_results_data = {
        "author_data" : {},
        "author_articles" : []
    }

    author_results_data["author_data"]["name"] = results.get("author").get("name")

    while True:
        results = search.get_dict()

        for article in results.get("articles", []):

            author_results_data["author_articles"].append({
                "article_title": article.get("title"),
                "article_year": article.get("year"),
                "article_authors": article.get("authors"),
                "article_cited_by_value": article.get("cited_by", {}).get("value")
            })
        if "next" in results.get("serpapi_pagination", []):
            search.params_dict.update(dict(parse_qsl(urlsplit(results.get("serpapi_pagination").get("next")).query)))
        else:
            break

    return author_results_data["author_articles"]

headings = ['Title', 'Authors', 'Publication date', '# citations']

layout = [
    [sg.Text("Search author:"), sg.Input(key="-IN-"), sg.FileBrowse()],
    [sg.Text("Sort in terms of:"), sg.Input(key="-OUT-")],
    [sg.Submit()],
    [sg.Exit()],
]

window = sg.Window("GUI for Google Scholar Queries", layout)

while True:
    event, value = window.read()
    if event.__contains__('Exit'):
        break
    if event.__contains__('Submit'):
        authorName = value["-IN-"]
        search_query = scholarly.search_author(authorName)
        authorId = next(search_query)["scholar_id"]
        query = value["-OUT-"]
        data = retrieveAllPublications(authorId, query)
        table_data = []
        for i in range(len(data)):
            table_data.append([data[i]["article_title"],
            data[i]["article_authors"], 
            data[i]["article_year"],
            data[i]["article_cited_by_value"]])
        print(table_data)
        layout = [
            [sg.Text("Search author:"), sg.Input(key="-IN-"), sg.FileBrowse()],
            [sg.Text("Sort in terms of:"), sg.Input(key="-OUT-")],
            [sg.Submit()],
            [sg.Button("Show table")],
            [sg.Table(values=table_data, headings=headings)],
            [sg.Exit()],
        ]
        window1 = sg.Window("GUI for Google Scholar Queries", layout)
        window.close()
        window = window1
window.close()