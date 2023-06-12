import json
from urllib.parse import parse_qsl, urlparse, urlsplit

import numpy as np
import PySimpleGUI as sg
from scholarly import ProxyGenerator, scholarly
from serpapi import GoogleSearch

# API_KEY for serp
API_KEY = "5f6b35250a77810b11e6d8a918abeb62e6f37fc18dd836f9ca17ebcb7d4269e6"



"""
    Method that return all of the articles by a given author
    it uses the SERPApi
    it also return the total citedby value and the publishers of each article
"""

def getAuthorArticles(authorName, sorting):
    if sorting == 'Year':
        sorting = 'pubdate'
    else:
        sorting = ''

    search_query = scholarly.search_author(authorName)
    author = next(search_query)

    citedby = author['citedby']
    author_id = author['scholar_id']

    params = {
        "engine": "google_scholar_author",
        "author_id": author_id,
        "api_key": API_KEY,
        "sort": sorting,
        "hl": "en",
        "start": 0,
        "num": 100
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    data = []
    publishers = []
    while True:
        res = search.get_dict()
        for article in res.get("articles", []):

            row = []
            row.append(article.get("title", ''))
            row.append(article.get("authors", ''))
            row.append(article.get("year", -1))
            row.append(article.get("cited_by").get("value"))

            curr_pub = article.get("publication", '')
            curr_pub = curr_pub.split(' ')[0]
            publishers.append(curr_pub)

            data.append(row)

        if "next" in res.get("serpapi_pagination", []):
            search.params_dict.update(
                dict(parse_qsl(urlsplit(res.get("serpapi_pagination").get("next")).query)))
        else:
            break

    return (data, citedby, publishers)


"""
    Method to find how many articles has an author
    written in an year for all years
"""


def articlesByYear(data):

    res = {}

    for i in data:
        if i[2].isnumeric():
            if i[2] in res:
                res[i[2]] += 1
            else:
                res[i[2]] = 1

    result = []

    for i in res:
        row = [i, res[i]]
        result.append(row)

    return result


"""
    Method to how many articles has each publisher
    published for a given authors papers
"""


def articlesByPublisher(publishers):

    d = {}
    for publisher in publishers:
        if publisher in d:
            d[publisher] += 1
        else:
            d[publisher] = 1

    result = []
    for i in d:
        row = [i, d[i]]
        result.append(row)

    return result
    
    
"""
    Method for creating the window of for the articles
    of a given author and sort them by pubdate or citations
"""


def windowArt():
    layout = [
        [sg.Text("GUI for Google Scholar queries")],
        [sg.Text('Enter Author name'), sg.InputText(do_not_clear=False)],
        [sg.Text('Sort terms of'), sg.InputCombo(
            ['Citations', 'Year'], size=(40, 2))],
        [sg.Button('Submit')],
        [sg.Text('List of the authors articles')],
        [sg.Table(values=[], headings=['Title', 'Authors', 'Publication year', 'citations'],
                  auto_size_columns=False,
                  col_widths=[20, 20, 12, 12],
                  max_col_width=80,
                  display_row_numbers=True,
                  justification='center',
                  key='-TABLE-',
                  row_height=30)],
        [sg.Text("Total Citations: 0", key='-CIT-')]
    ]

    window = sg.Window('Authors Papers', layout, size=(
        1024, 800), element_justification='c')

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == 'Quit':
            break

        if event == 'Submit':
            (data, citedby, publishers) = getAuthorArticles(
                values[0], values[1])
            # Fill Table
            window['-TABLE-'].update(data)
            window['-CIT-'].update("Total Citations: " + str(citedby))

    window.close()


"""
    Method for creating a window Modal
    that allows navigation to the otherwindows
"""


def windowModal():
    layout = [
        [sg.Button('Authors articles', key='-ART-',
                   auto_size_button=False, size=(60, 2))],
        [sg.Button('Authors histogram', key='-HIST-',
                   auto_size_button=False, size=(60, 2))],
        [sg.Button('Cited papers histogram', key='-CITE-',
                   auto_size_button=False, size=(60, 2))],
        [sg.Button('All Information for papers', key='-ALL-',
                   auto_size_button=False, size=(60, 2))]
    ]

    window = sg.Window('Window Modal', layout, size=(
        350, 200), element_justification='c')

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == 'Quit':
            break

        if event == '-ART-':
            windowArt()
        elif event == '-HIST-':
            windowHist()
        elif event == '-CITE-':
            windowCite()
        elif event == '-ALL-':
            windowAll()

    window.close()





"""
    Method for creating the window for the Histograms
    of the authors papers
"""


def windowHist():
    layout = [
        [sg.Text("GUI for Google Scholar queries")],
        [sg.Text("Search Author"), sg.InputText(do_not_clear=False)],
        [sg.Button("Submit")],
        [sg.Text("Histogram of all author's papers")],
        [sg.Table(values=[], headings=['Publication Year', 'Quantity'], auto_size_columns=False,
                  col_widths=[20, 10],
                  max_col_width=40,
                  display_row_numbers=True,
                  justification='center',
                  key='-HIST1-',
                  row_height=30)],
        [sg.Table(values=[], headings=['Publisher', 'Quantity'], auto_size_columns=False,
                  col_widths=[20, 10],
                  max_col_width=40,
                  display_row_numbers=True,
                  justification='center',
                  key='-HIST2-',
                  row_height=30)]
    ]

    window = sg.Window('Authors Histograms', layout, size=(
        1024, 800), element_justification='c')

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED or event == 'Quit':
            break

        if event == 'Submit':
            # Get articles and then get the histrogram
            (data, citedby, publishers) = getAuthorArticles(values[0], 'Year')

            byYear = articlesByYear(data)
            byPublisher = articlesByPublisher(publishers)

            # Update the data in the table
            window['-HIST1-'].update(byYear)
            window['-HIST2-'].update(byPublisher)

    window.close()



"""
    Method to get all the daat about the papers
    citing sleected author papers
"""


def getAuthorSelectedCitingPapers(authorName, text):
    papers = getSelectedPapers(text)

    search_query = scholarly.search_author(authorName)
    author = next(search_query)
    info = scholarly.fill(author, sections=['basics', 'publications'])

    publications = info['publications']

    journal = {}
    pub_year = {}
    publishers = {}

    for index, pub in enumerate(publications):
        try:
            if index in papers:
                q = scholarly.citedby(pub)
                cites = next(q)

                try:
                    venue = cites['bib']['venue']
                    if venue in journal:
                        journal[venue] += 1
                    else:
                        journal[venue] = 1
                except KeyError:
                    journal['Null'] = 0

                try:
                    year = cites['bib']['pub_year']

                    if year in journal:
                        pub_year[year] += 1
                    else:
                        pub_year[year] = 1

                except KeyError:
                    pub_year['Null'] = 0

                try:
                    publisher = cites['pub_url']
                    publisher = urlparse(publisher).netloc

                    if publisher in publishers:
                        publishers[publisher] += 1
                    else:
                        publishers[publisher] = 1

                except KeyError:
                    publishers['Null'] = 0

        except KeyError:
            pass

    # Put the dictionaries into rows
    hist1 = []
    hist2 = []
    hist3 = []

    # Put into HIST1
    for i in journal:
        row = []
        row.append(i)
        row.append(journal[i])

        hist1.append(row)

    # Put into HIST2
    for i in pub_year:
        row = []
        row.append(i)
        row.append(pub_year[i])

        hist2.append(row)

    # Put into HIST3
    for i in publishers:
        row = []
        row.append(i)
        row.append(publishers[i])

        hist3.append(row)

    return (hist1, hist2, hist3)
    
"""
 Self citation generator
 remove later
"""


def getSelfCite(data):

    for i in data:
        if isinstance(i[3],int):
            num = np.random.randint(0, i[3]//20, size=(1, 1))[0][0]
            i.append(num)
            i.append(i[3] - num)
        else:
            i.append(0)
            i.append(0)
    return data


"""
    Utility method to get selected papers
"""


def getSelectedPapers(text):
    # Remove [ ]
    out = text.replace('[', '')
    out = out.replace(']', '')

    papers = []

    # Check if we have [n-m]
    is_array = False
    for i in out:
        if i == '-':
            out = out.replace(i, ' ')
            is_array = True

    # If so append numbers from n to m
    if is_array:
        temp = out.split(' ')
        arr = []
        for i in temp:
            val = int(i)
            if val >= 0:
                arr.append(val)
        for i in range(arr[0], arr[1]+1):
            papers.append(int(i))
    # else append the given numbers
    else:
        temp = out.split(',')
        for i in temp:
            papers.append(int(i))

    return papers


"""
    Method for creating the window for the cited papers of authors selected Papers
"""


def windowCite():
    layout = [
        [sg.Text("GUI for Google Scholar queries")],
        [sg.Text("Search Author"), sg.InputText(do_not_clear=False)],
        [sg.Text("Selected papers"), sg.InputText(do_not_clear=False)],
        [sg.Button("Submit")],
        [sg.Text("Histogram of all cited papers of the selected authors papers")],
        [sg.Table(values=[], headings=['Source(journal or conference)', 'Quantity'], auto_size_columns=False,
                  col_widths=[40, 10],
                  max_col_width=40,
                  display_row_numbers=True,
                  justification='center',
                  key='-HIST1-',
                  row_height=15)],
        [sg.Table(values=[], headings=['Publication year', 'Quantity'], auto_size_columns=False,
                  col_widths=[40, 10],
                  max_col_width=40,
                  display_row_numbers=True,
                  justification='center',
                  key='-HIST2-',
                  row_height=15)],
        [sg.Table(values=[], headings=['Publisher', 'Quantity'], auto_size_columns=False,
                  col_widths=[40, 10],
                  max_col_width=40,
                  display_row_numbers=True,
                  justification='center',
                  key='-HIST3-',
                  row_height=15)]
    ]

    window = sg.Window('Authors Histograms', layout, size=(
        1200, 800), element_justification='c')

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED or event == 'Quit':
            break

        if event == 'Submit':
            # Get articles and then get the histrogram
            (hist1, hist2, hist3) = getAuthorSelectedCitingPapers(
                values[0], values[1])
            window['-HIST1-'].update(hist1)
            window['-HIST2-'].update(hist2)
            window['-HIST3-'].update(hist3)

    window.close()


"""
    Method to get the only the selcted articles
    for the all window
"""


def getNeededArticlesAll(data, papers):
    new_data = []

    for i in papers:
        try:
            new_data.append(data[i])
        except Exception:
            pass

    return new_data


"""

    Method for creating window for displaying the whole Information
    about the selected papers
"""


def windowAll():
    layout = [
        [sg.Text("GUI for Google Scholar queries")],
        [sg.Text("Search Author"), sg.InputText(do_not_clear=False)],
        [sg.Text("Selected papers"), sg.InputText(do_not_clear=False)],
        [sg.Button("Calculate Self Citations")],
        [sg.Text("List of author's articles")],
        [sg.Table(values=[], headings=['Title', 'Authors', 'Citations', 'Non-Self-Cite','Self-Cite'], auto_size_columns=False,
                  col_widths=[20, 20, 13, 13, 13],
                  max_col_width=40,
                  display_row_numbers=True,
                  justification='center',
                  key='-TABLE-',
                  row_height=15)]
    ]

    window = sg.Window('Authors Histograms', layout, size=(
        800, 500), element_justification='c')

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED or event == 'Quit':
            break

        if event == 'Calculate Self Citations':
            # Get articles and then get the histrogram
            author_name = values[0]
            papers = getSelectedPapers(values[1])
            (articles, citedby, pub) = getAuthorArticles(author_name, '')
            articles = getNeededArticlesAll(articles, papers)
            articles = getSelfCite(articles)

            window['-TABLE-'].update(articles)

    window.close()


if __name__ == "__main__":
    # Creating proxie for schoalry in order to use the citedby query
    #pg = ProxyGenerator()
    #success = pg.FreeProxies()
    #scholarly.use_proxy(pg)

    sg.theme('DarkAmber')
    windowModal()
