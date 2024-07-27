from fastapi import FastAPI, Query
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import csv
import sys
from util import Node, StackFrontier, QueueFrontier

class SerializerNoneReturn(BaseModel):
    message: str

class SerializerDataReturn(BaseModel):
    degrees: str
    layers: list


# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass

def main(load, name1, name2):
    
    directory = load if load else 'small'

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(name1)
    output = []
    if source is None:
        output.append(None)
        output.append("Person 1 not found.")
        return output
    target = person_id_for_name(name2)
    if target is None:
        output.append(None)
        output.append("Person 2 not found.")
        return output

    path = shortest_path(source, target)

    result = {
        "degrees":"",
        "layers": [],
    }
    if path:
        degrees = len(path)
        result['degrees'] = f"{degrees} degrees of separation."
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            result['layers'].append(f"{i + 1}: {person1} and {person2} starred in {movie}")
    else:
        return None
    return result

def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """

    # making initial state
    start = Node(state=source, parent=None, action=None)
    #using BFS search algorithm 
    frontier = QueueFrontier()
    # adding first state to frontier set 
    frontier.add(start)
    # making explored set that will contain all states that explored to make sure we will not go to them again
    explored = set()
    
    while True:
        # if frontier is empty that meaning no states to explored so no solution for this search
        if frontier.empty():
            return None
        # removing one state from frontier
        node = frontier.remove()
        # gool test - if the state is the target state then return the path to it 
        if node.state == target:
            path = []
            while node.parent is not None:
                path.append((node.action, node.state))
                node = node.parent
            path.reverse()
            return path
        # adding explored state to explored set
        explored.add(node.state)
        # searching for all neighbors possible states related to this state
        for action , state in neighbors_for_person(node.state):
            if not frontier.contains_state(state) and state not in explored:
                child = Node(state=state, parent=node, action=action)
                frontier.add(child)

def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]

def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors



@app.get('/')
def search(
    directory:str = Query( description="small or large"),
    name1:str = Query(..., description="Name of Actor 1"),
    name2:str = Query(..., description="Name of Actor 2")
    ):
    output = main(load=directory, name1=name1, name2=name2)
    if output is None:
        return SerializerNoneReturn(message="No connected.")
    elif output[0] is None:
        return SerializerNoneReturn(message=output[1])
    else:
        return SerializerDataReturn(degrees = output['degrees'], layers=output['layers'])