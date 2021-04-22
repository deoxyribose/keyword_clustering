import argparse
from collections import OrderedDict
from py2neo import Graph
import csv
import pandas as pd

graph = Graph(auth=('neo4j', 'shekhor'))

def keywords_up_to(n):
    return ', '.join(['k'+str(i) for i in range(1,n+1)])

def relationships_up_to(n):
    return ', '.join(['r'+str(i) for i in range(1,n+1)])

def all_vars(n):
    return ', '.join([keywords_up_to(n+1), relationships_up_to(n)])

def uncollect(n):
    vars = all_vars(n)
    return ', '.join([f'group[{i}] as {var}' for i,var in enumerate(vars.split(', '))])

def commonUrls(n):
    if n == 2:
        return 'r1.urls'
    else:
        return 'commonUrls'

def return_results(result):
    n_k = len(result[0][1:])//2
    return [keyword['keyword'] for keyword in result[0][1:n_k+1]]

def construct_greedy_query(phrase, min_n_keywords = 3, n_common_urls = 4, prev_result = None):
    """
    Iteratively build cliques of min_n_keywords where all edges have more than n_common_urls
    """

    match_phrase = 'MATCH (k1:Keyword {{keyword: "{phrase}"}})-[r1:ASSOCIATED_WITH]-(k2:Keyword)\n'\
                       'WHERE size(r1.urls) > {n_common_urls}\n'\
                       'WITH *\n'\
                        .format(phrase=phrase, n_common_urls=n_common_urls)
    if min_n_keywords < 3:
        print("Couldn't find any keywords to cluster with")

    find_next_keyword = ''
    for n in range(2,min_n_keywords):
        # Find k_n+1: k_n's neighbors that share at least n_common_urls urls with k_1, k_2, ..., k_n
        find_next_keyword += '\n'
        find_next_keyword += 'MATCH (k{n})-[r{n}:ASSOCIATED_WITH]-(k{nplus1})\n'\
                             'WHERE NOT k{nplus1} in [{keywords_up_to_n}]\n'\
                             'WITH *, apoc.coll.intersection({commonUrls}, r{n}.urls) AS commonUrls\n'\
                             'WHERE size(commonUrls) >= {n_common_urls}\n'\
                             .format(n=n,nplus1=n+1,keywords_up_to_n=keywords_up_to(n),commonUrls=commonUrls(n),relationships_up_to_n=relationships_up_to(n),n_common_urls=n_common_urls)
        # Find the biggest group of clusters that share the same urls and select the top cluster
        select_best_clique = 'WITH commonUrls, collect([{all_vars}]) as groups ORDER BY size(groups) DESC LIMIT 1\n'\
                             'UNWIND groups as group\n'\
                             'WITH {uncollect}, commonUrls LIMIT 1\n'\
                             .format(all_vars=all_vars(n), uncollect=uncollect(n))
        find_next_keyword += select_best_clique
    return_keywords = ', '.join(['k'+str(i) for i in range(1,min_n_keywords+1)])
    # return the keywords
    return_query = 'RETURN *\n'\
                    .format(return_keywords=return_keywords)
    return match_phrase + find_next_keyword + return_query

def construct_search_query(phrase, min_n_keywords = 3, n_common_urls = 4, prev_result = None):
    """
    Return number of groups with min_n_keywords.
    If there is only one such group, that is the largest possible group.
    If there is zero, min_n_keywords is set too high.
    If there is more than one, min_n_keywords is set too low.
    """
    match_phrase = 'MATCH (k1:Keyword {{keyword: "{phrase}"}})-[r1:ASSOCIATED_WITH]-(k2:Keyword)\n'\
                       'WHERE size(r1.urls) > {n_common_urls}\n'\
                       'WITH *\n'\
                        .format(phrase=phrase, n_common_urls=n_common_urls)
    find_next_keyword = ''
    for n in range(2,min_n_keywords):
        # Find k_n+1: k_n's neighbors that share at least n_common_urls urls with k_1, k_2, ..., k_n
        find_next_keyword += '\n'
        find_next_keyword += 'MATCH (k{n})-[r{n}:ASSOCIATED_WITH]-(k{nplus1})\n'\
                             'WHERE NOT k{nplus1} in [{keywords_up_to_n}]\n'\
                             'WITH *, apoc.coll.intersection({commonUrls}, r{n}.urls) AS commonUrls\n'\
                             'WHERE size(commonUrls) >= {n_common_urls}\n'\
                             .format(n=n,nplus1=n+1,keywords_up_to_n=keywords_up_to(n),commonUrls=commonUrls(n),relationships_up_to_n=relationships_up_to(n),n_common_urls=n_common_urls)
        # Find the biggest group of clusters that share the same urls and select the top cluster
        if n < min_n_keywords-1:
            select_best_clique = 'WITH commonUrls, collect([{all_vars}]) as groups ORDER BY size(groups) DESC LIMIT 1\n'\
                                 'UNWIND groups as group\n'\
                                 'WITH {uncollect},commonUrls LIMIT 1\n'\
                                 .format(all_vars=all_vars(n), uncollect=uncollect(n))
        else:
            select_best_clique = 'WITH commonUrls, collect([{all_vars}]) as groups ORDER BY size(groups) DESC LIMIT 1\n'\
                                 'UNWIND groups as group\n'\
                                 'WITH {uncollect},commonUrls\n'\
                                 .format(all_vars=all_vars(n), uncollect=uncollect(n))
        find_next_keyword += select_best_clique
    return_keywords = ', '.join(['k'+str(i) for i in range(1,min_n_keywords+1)])
    # return the keywords
    #return_query = 'RETURN [k in [{return_keywords}] | k.keyword] AS group\n'\
    #                .format(return_keywords=return_keywords)
    return_query = 'RETURN COUNT(*)\n'\
                    .format(return_keywords=return_keywords)
    return match_phrase + find_next_keyword + return_query

def run_min_query(phrase, min_n_keywords):
    return graph.run(construct_greedy_query(phrase, min_n_keywords=min_n_keywords)).to_table()

def find_largest_keyword_cluster(phrase, min_n_keywords = 3, n_common_urls = 4, init_guess = 15):
    """
    Find the largest group size by running search queries and imporving guessses iteratively
    """
    def run_query(n_keywords):
        return graph.run(construct_search_query(phrase, min_n_keywords = n_keywords, n_common_urls = n_common_urls)).to_table()[0][0]
    
    new_guess = init_guess
    result = run_query(new_guess)
    
    while result != 1:
        print(f"Guessing group size to be {new_guess}")
        print(f"Up to {result} keywords could be added, continuing search...")
        if result > 0:
            new_guess = new_guess + result - 1
            result = run_query(new_guess)
        else:
            new_guess = new_guess//2
            result = run_query(new_guess)

    print(f"Found largest group size to be {new_guess}")
    return return_results(graph.run(construct_greedy_query(phrase, min_n_keywords = new_guess, n_common_urls = n_common_urls)).to_table())


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Keyword clustering based on search results")
    parser.add_argument('-r', '--reuse_queries', default=True)
    parser.add_argument('-k', '--min_n_keywords', default=3)
    parser.add_argument('-u', '--n_common_urls', default=3)

    args = parser.parse_args()
    args.min_n_keywords = int(args.min_n_keywords)
    args.n_common_urls = int(args.n_common_urls)

    groups = {}

    with open('keywords.csv', newline='\n') as input_file:
        keywords = csv.reader(input_file, delimiter=',', quotechar='"')
        next(keywords, None) # skip header
        for row in keywords:
            try:
                print("\n")
                keyword = row[1]
                min_result = run_min_query(keyword, args.min_n_keywords)
                if not min_result:
                    print(f"{keyword} is single")
                    groups[keyword] = []
                else:
                    print(f"Searching for largest group for {keyword}...")
                    cluster = find_largest_keyword_cluster(keyword, min_n_keywords = args.min_n_keywords, n_common_urls = args.n_common_urls, init_guess = 15)
                    groups[keyword] = cluster[1:]
                    for supporting_keyword in cluster[1:]:
                        if supporting_keyword in groups.keys():
                            # compare the cluster of each supporting keyword to the newfound cluster, and replace it if the new one is bigger
                            if len(groups[supporting_keyword]) < len(cluster)-1:
                                groups[supporting_keyword] = cluster[1:]
                        else:
                            # if the supporting keyword hasn't been assigned a cluster yet, do so now
                            groups[supporting_keyword] = cluster[1:]
            except KeyboardInterrupt:
                df = pd.DataFrame.from_dict(groups, orient="index")
                df.to_csv("groups.csv")
    df = pd.DataFrame.from_dict(groups, orient="index")
    df.to_csv("groups.csv")
