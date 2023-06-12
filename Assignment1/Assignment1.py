import PySimpleGUI as sg
from scholarly import scholarly
from serpapi import GoogleSearch
from urllib.parse import urlsplit, parse_qsl

# retrieveAllPublications: str -> str -> [dict]
# retrieveAllPublications does a google search using parameters retrieve through the user's input. The number of results is set to 100 for maximum efficiency.
# since we can only retrieve 100 publications at a time, we have to use "serpapi_pagination" in order to emulate going to the next page and recieving the next
# 100 results until we have retrieved all publications for that specific author. Everything is saved in a list of dictionaries called author_results_data and returned
# after all publications have been retrieved.
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

# Headings list is used for the table that is created with the necessary information later.
headings = ['Title', 'Authors', 'Publication date', '# citations']

# The layout is responsible for showing how the GUI window should look like and what keys to update when necessary.
layout = [
    [sg.Text("Search author:"), sg.Input(key="-IN-")],
    [sg.Text("Sort in terms of:"), sg.Button("Number of citations"), sg.Button("Date of publication")],
    [sg.Frame('Results tables', [[]] ,key="-Tables-", visible=False)],
    [sg.Text("", key = "-Citation-", visible=False)],
    [sg.Submit()],
    [sg.Exit()],
]

# Creating an instance of the GUI window
window = sg.Window("GUI for Google Scholar Queries", layout)

# Initializing 2 variables sort_required and total_citation that are used in the main code
sort_required = None
total_citation = 0

# We use a while True such that whenever the user presses exit we can simply break the loop which will close the window.
while True:
    # The window will wait for the user to input the fields and press a button.
    event, value = window.read()
    # If user presses on the exit button, the loop will break and the window will close.
    if event == ('Exit'):
        break
    # If user presses on the "Date of publication" button, the sort_required variable will be assigned the corresponding string such that when retrieveAllPublications
    # is called, it will be sorted by the date of publication
    if event == "Date of publication":
        sort_required = "pubdate"
        sg.popup("We will sort your query results by publication date!")
    # And the same for no of citations.
    if event == "Number of citations":
        sort_required = None
        sg.popup("We will sort your query results by the number of citations!")
    if event == "Submit":
        # Save the input field for the author into a variable
        authorName = value["-IN-"]
        # Use scholarly.search.author in order to retrieve the scholar_id which will be used in retrieveAllPublications
        search_query = scholarly.search_author(authorName)
        authorId = next(search_query)["scholar_id"]
        data = retrieveAllPublications(authorId, sort_required)
        table_data = []
        # Once retrieveAllPublications has been called and the data has been saved, we can proceed to loop through each article in the data and append the data that we want
        # into a new list of dictionaries such that we can use that for the GUI window.
        for i in data:
            table_data.append([i["title"],
            i["authors"], 
            i["year"],
            i["cited_by"]["value"]])
            # Since we also want the total no. of citations, we sum all the cited_by values for each article into one variable.
            if (i["cited_by"]["value"] is not None):
                total_citation = total_citation + i["cited_by"]["value"]
        # Here we finally extend the window and input the corresponding information.
        window.extend_layout(window["-Tables-"], [[sg.Table(values=table_data, headings=headings, max_col_width=35, display_row_numbers=True, row_height=35, num_rows=5)]])
        # The skeleton for the total citation text is also updated
        window["-Citation-"].update("Total citations: " + str(total_citation), visible=True)
        window["-Tables-"].update(visible=True)
        #We notify the window that the visibility has changed such that it can refresh the window.
        window.visibility_changed()
#Finally, the window closes when the user has pressed exit.
window.close()