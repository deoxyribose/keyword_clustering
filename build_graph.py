import pandas as pd

data = pd.read_csv('./search_results.csv', header=0)
data = data.drop(['Title', '_id'], axis= 1)

data['keyword_id'] = data.groupby('Keyword').ngroup()
data['url_id'] = data.groupby('Url').ngroup()
data = data.drop_duplicates()

keywords = data[['keyword_id', 'Keyword']]
keywords = keywords.drop_duplicates()

urls = data[['url_id', 'Url']]
urls = urls.drop_duplicates()

url2keyword = data[['url_id', 'keyword_id']]
url2keyword = url2keyword.drop_duplicates()

keywords.to_csv('keywords.csv', sep=',', index=False, header=['id', 'keyword'])
urls.to_csv('urls.csv', sep=',', index=False, header=['id', 'url'])
url2keyword.to_csv('url2keyword.csv', sep=',', index=False, header=['urlId', 'keywordId'])