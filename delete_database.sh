DROP CONSTRAINT urlIdConstraint;
DROP CONSTRAINT keywordIdConstraint;
MATCH (n) DETACH DELETE n;
