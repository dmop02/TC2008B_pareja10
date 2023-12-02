using UnityEngine;

public class LightsColor : MonoBehaviour
{
    public Material greenLightMaterial; 
    public Material redLightMaterial;   
    public Color greenLightColor = Color.green; 
    public Color redLightColor = Color.red;   
    public float changeInterval = 15.0f;

    private MeshRenderer meshRenderer;
    private Light trafficLight;
    private float timer;
    public bool isGreen = true;

    void Start()
    {
        meshRenderer = GetComponent<MeshRenderer>();
        trafficLight = GetComponent<Light>();

        //Start with Green
        meshRenderer.material = greenLightMaterial;
        trafficLight.color = greenLightColor;
        timer = changeInterval;
    }

    void Update()
    {
        ChangeInterval();
        if (isGreen == false)
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
    
    void ChangeInterval()
    {
        if (timer > 0)
        {
            timer -= Time.deltaTime;
        }
        else
        {
            timer = 6;
            isGreen = !isGreen;
        }
    }
}
