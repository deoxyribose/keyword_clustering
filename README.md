# keyword_clustering
"Hard" keyword clustering

From https://en.wikipedia.org/wiki/Keyword_clustering#Hard:
A keyword clustering tool scans the list of keywords and then picks a keyword with the highest search volume. Then a tool compares the TOP 10 search result listings that showed up for the taken keyword to the TOP10 search results that showed up for another keyword to detect the number of matching URLs. At the same time, a tool compares all keywords to each other and all matching URLs in the detected pairs. If the detected number of identical search listings matches the selected grouping level, the keywords are grouped together.

As the result, all keywords within a group will be related to each other by having the same matching URLs.

# Input data format

A csv file containing
keyword1, url1
keyword1, url2
keyword2, url3
keyword2, url2
...

# How to run

run "sh install_neo4j.sh"
run "sh create_database.sh"

To cluster an input search query run
"python keyword_cluster.py "search query" -k 3 -u 4"
where 3 is the grouping level, and 4 is the minimum number of matching URLs.

To cluster all keywords, run
"python find_all_groups.py -k 3 -u 4"
This creates a csv file output.csv, formatted as
keyword1 supporting_keyword1,supporting_keyword2,...
keyword2 supporting_keyword3,supporting_keyword4,...
