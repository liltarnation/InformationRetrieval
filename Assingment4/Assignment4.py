from serpapi import GoogleSearch
import numpy as np
from urllib.parse import urlsplit, parse_qsl
from matplotlib import pyplot as plt


def get_search_results(algo, query, top_n):
    # retrieve results and rank
    ranking = []
    
    if algo == 'yahoo':
        param = {
        "engine": algo,
        "p": query,
        "api_key": "c1b57a5186ae96e31b5966c89200e8fbe3491fb9854ad5089f56feed874dcf57"
        }
    else:
        param = {
        "engine": algo,
        "q": query,
        "api_key": "c1b57a5186ae96e31b5966c89200e8fbe3491fb9854ad5089f56feed874dcf57"
        }

    search = GoogleSearch(param)
    while True:
        results = search.get_dict()
        for organic in results.get("organic_results", []):
            ranking.append(organic["link"])
            if len(ranking) == top_n:
                print(len(ranking))
                return ranking
        if "next" in results.get("serpapi_pagination", []):
            search.params_dict.update(dict(parse_qsl(urlsplit(results.get("serpapi_pagination").get("next")).query)))
        else:
            break
    return ranking


def precision_recall(retrieved_docs, relevant_docs):
    # here the relevant_docs are the baseline url's that we determined
    # The retrieved_docs refers to all url's found by a different search engines results
    RDIAS = 0
    for item in retrieved_docs:
        # if the url in the retrieved docs is in the relevant docs, increment count RDIAS
        if item in relevant_docs:
            RDIAS += 1
    precision = RDIAS/len(retrieved_docs)
    recall = RDIAS/len(relevant_docs)
    return precision, recall


def precision_at_11_standard_recall_levels(retrieved_docs, relevant_docs):
    RDIAS = 0
    index = 1
    standard_r_values = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    standard_p_values= []
    p_values = []
    r_values = []
    # here we append only the precision points when we have found a document in both the answer and relevant set
    # we also append the index, which tells us how far in the ranking the matching document is.
    # This is useful for the precision recall plot as it shows whether the top results or the bottom results in the set are most relevant
    for item in retrieved_docs:
        if item in relevant_docs:
            RDIAS += 1
            p_values.append(float(RDIAS/index))
            r_values.append(index)
        index += 1
    
    # below we calculate the precision scores for the 11 standard recall values. We stored the index in which a document
    # was found to match one in the relevant set. Using this index we can set values between say index 2 and 5 (index 3 4 5)
    # to the precision score calculated at recall index 5 (similar process as in the slides).
    # This method allows us to graphically show how the precision of the retrieved set changes as recall increases.
    for i in range(len(r_values)):
        for j in range(1, len(standard_r_values)):
            if r_values[i]/10 == standard_r_values[j]:
                if i == 0:
                    standard_p_values.append(p_values[i])
                else:
                    for z in range(r_values[i]-r_values[i-1]):
                        standard_p_values.append(p_values[i])
    
    # fill the remaining spots in the list with zero's, as there are no more relevant sites in the retrieved set (precision is 0)
    while len(standard_p_values) < len(standard_r_values)-1:
        standard_p_values.append(0)
    
    # add the precision at recall 0.0 (which is the precision at recall 0.1)
    standard_p_values.insert(0, standard_p_values[0])
    return standard_p_values, standard_r_values

def single_valued_summaries(retrieved_docs, relevant_docs):
    RDIAS = 0
    index = 1
    p_values = []
    r_values = []
    # append precision points for each iteration
    for item in retrieved_docs:
        if item in relevant_docs:
            RDIAS += 1
        p_values.append(RDIAS/index)
        r_values.append(RDIAS/len(relevant_docs))
        index += 1
    # return the precision at 5th spot and precision at 10th spot
    # the args contains values 5 and 10 so we must get the precision scores at index 5+1 and 10+1
    print("precision at position 5: ", p_values[4])
    print("precision at position 10: ", p_values[9])
    return p_values, r_values

def fmeasure(precision, recall):
    fmeasures = []
    # compute f measure at each position i in the lists of recall and precision values
    for i in range(len(recall)):
        if recall[i] == 0 and precision[i] == 0:
            fmeasures.append(0)
        elif precision[i] == 0:
            fmeasures.append(2/(1/recall[i]))
        elif recall[i] == 0:
            fmeasures.append(2/(1/precision[i]))
        else:
            fmeasures.append(2/((1/recall[i])+(1/precision[i])))
    return fmeasures

def plot(precision, recall, name1, name2):
    plt.plot(recall, precision, marker = 'o', markerfacecolor = 'green', markersize = 4)
    plt.title(name1 + " compared to " + name2)
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.ylim(0, 1.2)
    plt.xlim(0, 1.2)
    plt.show()

if __name__ == '__main__':
    query = "Hans Niemann"
    search_results = {
        'google': get_search_results('google', query, top_n=10),
        'bing': get_search_results('bing', query, top_n=10),
        'yahoo': get_search_results('yahoo', query, top_n=10),
        'duckduckgo': get_search_results('duckduckgo', query, top_n=10)
    }
    algo_names = ["google", "bing", "yahoo", "duckduckgo"]
    retrieved_docs = [search_results["google"], search_results["bing"], search_results["yahoo"], search_results["duckduckgo"]]
    relevant_docs = retrieved_docs
    for i in range(len(retrieved_docs)):
        for y in range(len(relevant_docs)):
            if i != y:
                precision, recall = precision_recall(retrieved_docs[i], relevant_docs[y])
                print(algo_names[i]+ " compared to", algo_names[y], " as the set of relevant document " + "Precision: ", precision, " Recall: ", recall)

                # compute precision at 11 standard recall levels
                precision_list, recall_list = precision_at_11_standard_recall_levels(retrieved_docs[i], relevant_docs[y])
                plot(precision_list, recall_list, algo_names[i], algo_names[y])
                precision_list, recall_list = single_valued_summaries(retrieved_docs[i], relevant_docs[y])
                f_measure = fmeasure(precision_list, recall_list)
                print(sum(f_measure)/len(f_measure))
                print("***********************************")
    
    
    
    


    