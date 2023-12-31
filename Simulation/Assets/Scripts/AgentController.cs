﻿// TC2008B. Sistemas Multiagentes y Gráficas Computacionales
// Domingo Mora Perez
//Cristina Gonzalez

using System;
using System.Collections;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using UnityEngine.Networking;


[Serializable]
public class AgentsData
{
    /*
    The AgentData class is used to store the data of each agent.
    
    Attributes:
        id (string): The id of the agent.
        x (float): The x coordinate of the agent.
        y (float): The y coordinate of the agent.
        z (float): The z coordinate of the agent.
    */
    public List<AgentData> positions;

    public AgentsData() => this.positions = new List<AgentData>();
}
[Serializable]
public class AgentData
{
    /*
    The AgentData class is used to store the data of each agent.
    
    Attributes:
        id (string): The id of the agent.
        x (float): The x coordinate of the agent.
        y (float): The y coordinate of the agent.
        z (float): The z coordinate of the agent.
    */
    public string id;
    public float x, y, z;
    public string state;

    public AgentData(string id, float x, float y, float z)
    {
        this.id = id;
        this.x = x;
        this.y = y;
        this.z = z;
        this.state = state;

    }
}
[Serializable]
public class TrafficLightData
{
    /*
    The AgentData class is used to store the data of each agent.
    
    Attributes:
        id (string): The id of the agent.
        x (float): The x coordinate of the agent.
        y (float): The y coordinate of the agent.
        z (float): The z coordinate of the agent.
    */
    public string id;
    public float x, y, z;
    public string state;

    public TrafficLightData(string id, float x, float y, float z, string state)
    {
        this.id = id;
        this.x = x;
        this.y = y;
        this.z = z;
        this.state = state;
    }
}
[Serializable]
public class TrafficLightsData
{
    /*
    The AgentData class is used to store the data of each agent.
    
    Attributes:
        id (string): The id of the agent.
        x (float): The x coordinate of the agent.
        y (float): The y coordinate of the agent.
        z (float): The z coordinate of the agent.
    */
    public List<TrafficLightData> positions;

    public TrafficLightsData() => this.positions = new List<TrafficLightData>();
}





[Serializable]
public class AgentController : MonoBehaviour
{
    /*
    The AgentController class is used to control the agents in the simulation.

    Attributes:
        serverUrl (string): The url of the server.
        getAgentsEndpoint (string): The endpoint to get the agents data.
        getObstaclesEndpoint (string): The endpoint to get the obstacles data.
        sendConfigEndpoint (string): The endpoint to send the configuration.
        updateEndpoint (string): The endpoint to update the simulation.
        agentsData (AgentsData): The data of the agents.
        obstacleData (AgentsData): The data of the obstacles.
        agents (Dictionary<string, GameObject>): A dictionary of the agents.
        prevPositions (Dictionary<string, Vector3>): A dictionary of the previous positions of the agents.
        currPositions (Dictionary<string, Vector3>): A dictionary of the current positions of the agents.
        updated (bool): A boolean to know if the simulation has been updated.
        started (bool): A boolean to know if the simulation has started.
        agentPrefab (GameObject): The prefab of the agents.
        obstaclePrefab (GameObject): The prefab of the obstacles.
        floor (GameObject): The floor of the simulation.
        NAgents (int): The number of agents.
        width (int): The width of the simulation.
        height (int): The height of the simulation.
        timeToUpdate (float): The time to update the simulation.
        timer (float): The timer to update the simulation.
        dt (float): The delta time.
    */
    string serverUrl = "http://localhost:8585";
    string getAgentsEndpoint = "/getAgents";
    string getTrafficLightsEndpoint = "/getTrafficLights";
    string sendConfigEndpoint = "/init";
    string updateEndpoint = "/update";
    AgentsData agentsData, TrafficLData;
    Dictionary<string, GameObject> agents;
    Dictionary<string, GameObject> trafficData;
    Dictionary<string, Vector3> prevPositions, currPositions;

    bool updated = false, started = false;

    public GameObject agentPrefab, trafficLightPrefab, floor;
    public int NAgents, width, height;
    public float timeToUpdate = 5.0f;
    private float timer, dt;

    void Start()
    {
        agentsData = new AgentsData();
        TrafficLData = new AgentsData();

        prevPositions = new Dictionary<string, Vector3>();
        currPositions = new Dictionary<string, Vector3>();

        agents = new Dictionary<string, GameObject>();
        trafficData = new Dictionary<string, GameObject>();

        floor.transform.localScale = new Vector3((float)width/10, 1, (float)height/10);
        floor.transform.localPosition = new Vector3((float)width/2-0.5f, 0, (float)height/2-0.5f);
        
        timer = timeToUpdate;

        // Launches a couroutine to send the configuration to the server.
        StartCoroutine(SendConfiguration());
    }

    private void Update() 
    {
        if(timer < 0)
        {
            timer = timeToUpdate;
            updated = false;
            StartCoroutine(UpdateSimulation());
        }

        if (updated)
        {
            timer -= Time.deltaTime;
            dt = 1.0f - (timer / timeToUpdate);

            // Iterates over the agents to update their positions.
            // The positions are interpolated between the previous and current positions.
            foreach(var agent in currPositions)
            {
                Vector3 currentPosition = agent.Value;
                Vector3 previousPosition = prevPositions[agent.Key];
                agents[agent.Key].GetComponent<ApplyT>().StartMovement(previousPosition,currentPosition);
            }

            // float t = (timer / timeToUpdate);
            // dt = t * t * ( 3f - 2f*t);
        }
    }
 
    IEnumerator UpdateSimulation()
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + updateEndpoint);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else 
        {
            StartCoroutine(GetAgentsData());
        }
    }

    IEnumerator SendConfiguration()
    {
        /*
        The SendConfiguration method is used to send the configuration to the server.

        It uses a WWWForm to send the data to the server, and then it uses a UnityWebRequest to send the form.
        */
        WWWForm form = new WWWForm();

        form.AddField("NAgents", NAgents.ToString());
        form.AddField("width", width.ToString());
        form.AddField("height", height.ToString());

        UnityWebRequest www = UnityWebRequest.Post(serverUrl + sendConfigEndpoint, form);
        www.SetRequestHeader("Content-Type", "application/x-www-form-urlencoded");

        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(www.error);
        }
        else
        {
            Debug.Log("Configuration upload complete!");
            Debug.Log("Getting Agents positions");

            // Once the configuration has been sent, it launches a coroutine to get the agents data.
            StartCoroutine(GetAgentsData());
            StartCoroutine(GetTrafficLightsData());
        }
    }

    IEnumerator GetAgentsData() 
    {
        // The GetAgentsData method is used to get the agents data from the server.

        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getAgentsEndpoint);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else 
        {
            // Once the data has been received, it is stored in the agentsData variable.
            // Then, it iterates over the agentsData.positions list to update the agents positions.
            agentsData = JsonUtility.FromJson<AgentsData>(www.downloadHandler.text);

            foreach(AgentData agent in agentsData.positions)
            {
                Vector3 orginPos = new Vector3 (0,0,0);
                Vector3 newAgentPosition = new Vector3(agent.x, agent.y, agent.z);
                

                    if(!agents.ContainsKey(agent.id))
                    {
                        prevPositions[agent.id] = newAgentPosition;
                        agents[agent.id] = Instantiate(agentPrefab, orginPos,Quaternion.identity);
                        

                    }
                    else
                    {
                        Vector3 currentPosition = new Vector3();                     
                        if(currPositions.TryGetValue(agent.id, out currentPosition)){
                            prevPositions[agent.id] = currentPosition;
                        }
                        currPositions[agent.id] = newAgentPosition;
                        
                    }
            }

            updated = true;
            if(!started) started = true;
        }
    }

    IEnumerator GetTrafficLightsData()
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getTrafficLightsEndpoint);
        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
        {
            Debug.Log("[GetTrafficLightsData] Error: " + www.error);
        }
        else
        {
            TrafficLightsData newData = JsonUtility.FromJson<TrafficLightsData>(www.downloadHandler.text);
            HashSet<string> receivedTrafficLightIds = new HashSet<string>();

            foreach (TrafficLightData trafficLightData in newData.positions)
            {

                receivedTrafficLightIds.Add(trafficLightData.id);

                if (!trafficData.ContainsKey(trafficLightData.id))
                {
                    GameObject newTrafficLight = Instantiate(trafficLightPrefab, new Vector3(trafficLightData.x, trafficLightData.y, trafficLightData.z), Quaternion.identity);
                    trafficData.Add(trafficLightData.id, newTrafficLight);

                }
                else
                {
                    // get the traffic light and set the state
                    trafficData[trafficLightData.id].GetComponent<LightsColor>().isGreen = trafficLightData.state.ToLower() == "true" ? true : false;
                }
            }
        }
    }
}


