# from graph import Graph
# Graphs
# https://en.wikipedia.org/wiki/Adjacency_matrix

def fileread(file):
    x, connect = 1 , 1
    # Splits file into lines by new line characters
    file = file.read().split('\n')
    # Gets the amount of vectors 
    # ex. n = 5
    size = int(file[0].split()[2])
    # Starts file after
    # ex. n = 5
    # [space]
    file = file[2:]

    # Creates dictionary
    graph = {}

    for line in file:
        # Splits line into a single characters list
        line = line.split()
        # Sets Y to zero, because Y is the columns
        y = 1
        # Loops through values in list
        for i in line:
            if i == '1':
                # Build Graph using X and Y values
                if x in graph:
                    # If the node is already added to the graph, function
                    # Appends the connecting node to the nodes "hash"
                    graph[x].append(y)
                else:
                    # If nodes doesn't exits, creates node with a list of
                    # nodes that it connects to
                    graph[x] = [y]
            # Regardless of built list, breaks the list based on 
            # specified size
            if y == size:
                break
            # Increments Y for each loop iteration
            y += 1
        # Increments X for each row in i (lines read)
        x += 1

    # Returns a dictionary of nodes and their connected nodes

    # Using the graph
    # https://www.python.org/doc/essays/graphs/
    return graph

        
# Files used to build graph
files = [
        open("Testcase1.txt", "r"),
        open("Testcase2.txt", "r"),
        open("Testcase3.txt", "r"),
        open("Testcase4.txt", "r")
        ]

# fileread(files[0])
fileNum = 0
for i in files:
    fileNum += 1
    graph = fileread(i)
    # Using this data type as a graph
    # https://docs.python.org/3.6/tutorial/datastructures.html
    print(graph)