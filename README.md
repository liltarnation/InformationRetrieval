The code works by taking the authors name as the input, using scholarly to get the scholar_id and using that to run a request through serpapi using retrieveAllPublications*. Next, I save all the articles into a list of dictionaries and I append the sufficient information that I need for the GUI in a new list of lists. Finally, I can use this new list of lists in order to extend the table with the information that we need, and finally update the window to show the table.

*retrieveAllPublications does a google search using parameters retrieve through the user's input. The number of results is set to 100 for maximum efficiency.
since we can only retrieve 100 publications at a time, we have to use "serpapi_pagination" in order to emulate going to the next page and recieving the next
100 results until we have retrieved all publications for that specific author. Everything is saved in a list of dictionaries called author_results_data and returned
after all publications have been retrieved.


 
