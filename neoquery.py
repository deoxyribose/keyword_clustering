from bottle import get, run, request, response, static_file
from py2neo import Graph

graph = Graph()

if __name__ == "__main__":
    run(port=8080)