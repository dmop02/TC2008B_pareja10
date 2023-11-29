# TC2008B. Sistemas Multiagentes y Gráficas Computacionales
# Python flask server to interact with Unity. Based on the code provided by Sergio Ruiz.
# Octavio Navarro. October 2023git

from flask import Flask, request, jsonify
from randomAgents.model import CityModel
from randomAgents.agent import Car, Obstacle

# Size of the board:
number_agents = 10
width = 28
height = 28
cityModel = None
currentStep = 0

app = Flask("Traffic example")


@app.route("/init", methods=["GET", "POST"])
def initModel():
    global currentStep, cityModel, number_agents, width, height

    if request.method == "POST":
        number_agents = int(request.form.get("NAgents"))
        width = int(request.form.get("width"))
        height = int(request.form.get("height"))
        currentStep = 0

        
        cityModel = CityModel(number_agents)

        return jsonify({"message": "Parameters recieved, model initiated."})
    elif request.method == "GET":
        number_agents = 10
        width = 30
        height = 30
        currentStep = 0
        cityModel = CityModel(number_agents)

        return jsonify({"message": "Default parameters recieved, model initiated."})


@app.route("/getAgents", methods=["GET"])
def getAgents():
    global cityModel

    if request.method == "GET":
        # Print agent positions
        for a, (x, z) in cityModel.grid.coord_iter():
            print(a, x, z)
        agentPositions = [
            {"id": str(agent.unique_id), "x": x, "y": 1, "z": z}
            for agents, (x, z) in cityModel.grid.coord_iter()
            for agent in agents
            if isinstance(agent, Car)
        ]

        return jsonify({"positions": agentPositions})


@app.route("/getObstacles", methods=["GET"])
def getObstacles():
    global cityModel

    if request.method == "GET":
        carPositions = [
            {"id": str(agent.unique_id), "x": x, "y": 1, "z": z}
            for agents, (x, z) in cityModel.grid.coord_iter()
            for agent in agents
            if isinstance(agent, Obstacle)
        ]

        return jsonify({"positions": carPositions})


@app.route("/update", methods=["GET"])
def updateModel():
    global currentStep, cityModel
    if request.method == "GET":
        cityModel.step()
        currentStep += 1
        return jsonify(
            {
                "message": f"Model updated to step {currentStep}.",
                "currentStep": currentStep,
            }
        )


if __name__ == "__main__":
    app.run(host="localhost", port=8585, debug=True)