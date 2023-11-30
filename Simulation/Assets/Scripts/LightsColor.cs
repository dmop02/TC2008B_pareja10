using UnityEngine;

public class LightsColor : MonoBehaviour
{
    public Material greenLightMaterial; 
    public Material redLightMaterial;   
    public Color greenLightColor = Color.green; 
    public Color redLightColor = Color.red;   
    public float changeInterval = 5.0f;
    public int state = 0;

    private MeshRenderer meshRenderer;
    private Light trafficLight;
    private float timer;
    public bool isGreen = true;

    void Start()
    {
        meshRenderer = GetComponent<MeshRenderer>();
        trafficLight = GetComponent<Light>();

        if (meshRenderer == null)
        {
            Debug.LogError("No MeshRenderer component found on the traffic light object.");
            return;
        }

        if (trafficLight == null)
        {
            Debug.LogError("No Light component found on the traffic light object.");
            return;
        }

        // Comenzar con la luz verde
        meshRenderer.material = greenLightMaterial;
        trafficLight.color = greenLightColor;
        timer = changeInterval;
    }

    void Update()
    {
        if (state == 0)
            {
                meshRenderer.material = redLightMaterial;
                trafficLight.color = redLightColor;
            }
            else
            {
                meshRenderer.material = greenLightMaterial;
                trafficLight.color = greenLightColor;
            }
        }
    }