import argparse
from py2neo import Graph

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

def construct_greedy_query(phrase, min_n_keywords = 3, n_common_urls = 4):
    """
    Iteratively build cliques of min_n_keywords where all edges have more than n_common_urls
    """
    # Find keyword
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
                             'WITH *,reduce(intersect = r1.urls, r IN [{relationships_up_to_n}] | apoc.coll.intersection(intersect, r.urls)) AS commonUrls\n'\
                             'WHERE size(commonUrls) > 4\n'\
                             .format(n=n,nplus1=n+1,keywords_up_to_n=keywords_up_to(n),relationships_up_to_n=relationships_up_to(n),n_common_urls=n_common_urls)
        # Find the biggest group of clusters that share the same urls and select the top cluster
        select_best_clique = 'WITH commonUrls, collect([{all_vars}]) as groups ORDER BY size(groups) DESC LIMIT 1\n'\
                             'UNWIND groups as group\n'\
                             'WITH {uncollect} LIMIT 1\n'\
                             .format(all_vars=all_vars(n), uncollect=uncollect(n))
        find_next_keyword += select_best_clique
    return_keywords = ', '.join(['k'+str(i) for i in range(1,min_n_keywords+1)])
    # return the keywords
    return_query = 'RETURN [k in [{return_keywords}] | k.keyword] AS group\n'\
                    .format(return_keywords=return_keywords)
    return match_phrase + find_next_keyword + return_query

def find_largest_keyword_cluster(phrase, min_n_keywords = 3, n_common_urls = 4, range_min = 15, range_max = 30):
    # run binary search
    # start with pivot = 15
    def run_query(n_keywords):
        return graph.run(construct_greedy_query(phrase, min_n_keywords = n_keywords, n_common_urls = n_common_urls)).to_table()
    
    while range_max - range_min > 2:
        query_lo = run_query(range_min)
        query_hi = run_query(range_max)
        if query_lo and query_hi:
            # set range to query_hi, query_hi*2
            range_min = range_max
            range_max = range_max*2
        elif not query_lo and not query_hi:
            # set range to query_lo//2, query_lo
            range_max = range_min
            range_min = range_min//2
        else:
            pivot = (range_min + range_max)//2
            query = run_query(pivot)
            if query:
                range_min = pivot
            else:
                range_max = pivot
    results = run_query((range_min + range_max)//2)    
    if results:
        return results
    else:
        return run_query(range_min)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Keyword clustering based on search results")
    parser.add_argument('keyword', action='store', type=str, help='The keyword to cluster.')
    parser.add_argument('-k', '--min_n_keywords', default=3)
    parser.add_argument('-u', '--n_common_urls', default=4)

    args = parser.parse_args()

    cluster = find_largest_keyword_cluster(args.keyword, min_n_keywords = args.min_n_keywords, n_common_urls = args.n_common_urls, range_min = 15, range_max = 30)

    for keyword in cluster[0][0]:
        print(keyword)