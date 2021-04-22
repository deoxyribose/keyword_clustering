CREATE CONSTRAINT urlIdConstraint ON (url:Url) ASSERT url.id IS UNIQUE;

CREATE CONSTRAINT keywordIdConstraint ON (keyword:Keyword) ASSERT keyword.id IS UNIQUE;

LOAD CSV WITH HEADERS FROM "file:///urls.csv" AS csvLine
CREATE (u:Url {id: toInteger(csvLine.id), url: csvLine.url});

LOAD CSV WITH HEADERS FROM "file:///keywords.csv" AS csvLine
CREATE (keyword:Keyword {id: toInteger(csvLine.id), keyword: csvLine.keyword});

LOAD CSV WITH HEADERS FROM "file:///url2keyword.csv" AS csvLine
MATCH (keyword:Keyword {id: toInteger(csvLine.keywordId)}), (url:Url {id: toInteger(csvLine.urlId)})
CREATE (url)-[:SEARCH_RESULT_FOR]->(keyword);

CREATE INDEX kws IF NOT EXISTS FOR (k:Keyword) ON (k.keyword);

CALL apoc.periodic.iterate(
"MATCH (k1:Keyword) RETURN k1",
"MATCH (k1)<--(r:Url)-->(k2:Keyword)
WHERE k1 <> k2
WITH k1, k2, COLLECT(DISTINCT r.id) AS commonURLs
WHERE size(commonURLs) >= 3
MERGE (k1)-[r:ASSOCIATED_WITH]-(k2)
SET r.urls = commonURLs", 
{batchSize: 250, parallel: false});
