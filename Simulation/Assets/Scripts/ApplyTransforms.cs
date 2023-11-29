
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class ApplyTransforms : MonoBehaviour
{
    // Declare general Movment variables
    [SerializeField] Vector3 poswheel1;
    [SerializeField] Vector3 poswheel2;
    [SerializeField] Vector3 poswheel3;
    [SerializeField] Vector3 poswheel4;
    [SerializeField] Vector3 displacement;
    [SerializeField] float angle;
    [SerializeField] AXIS rotationAxis;
    [SerializeField] GameObject wheel12;
    // Wheel Axis
    AXIS wheelAxis = AXIS.X;
    float wheelAngle = -30;
    float scaleFactor = 0.3f; // Scaling factor
    GameObject wheel1;
    GameObject wheel2;
    GameObject wheel3;
    GameObject wheel4;
    
    Vector3 stopP;
    Vector3 startP;
    
    

    // First car variables
    Mesh mesh;
    Mesh mesh1;
    Mesh mesh2;
    Mesh mesh3;
    Mesh mesh4;
    Vector3[] baseVertices;
    Vector3[] baseVertices1;
    Vector3[] baseVertices2;
    Vector3[] baseVertices3;
    Vector3[] baseVertices4;
    Vector3[] newVertices;
    Vector3[] newVertices1;
    Vector3[] newVertices2;
    Vector3[] newVertices3;
    Vector3[] newVertices4;

    // Declare 
    Mesh wheels;
    Vector3[] baseVerticesWheels;
    Vector3[] newVerticesWheels;

    void Start()
    {

        wheel1 = Instantiate(wheel12, new Vector3(0f,0f,0f), Quaternion.identity);
        wheel2 = Instantiate(wheel12, new Vector3(0f,0f,0f), Quaternion.identity);
        wheel3 = Instantiate(wheel12, new Vector3(0f,0f,0f), Quaternion.identity);
        wheel4 = Instantiate(wheel12, new Vector3(0f,0f,0f), Quaternion.identity);
        
        mesh = GetComponentInChildren<MeshFilter>().mesh;
        baseVertices = mesh.vertices;

        newVertices = new Vector3[baseVertices.Length];
        for (int i = 0; i < baseVertices.Length; i++)
        {
            newVertices[i] = baseVertices[i];
        }
        mesh1 = wheel1.GetComponentInChildren<MeshFilter>().mesh;
        baseVertices1 = mesh1.vertices;
        newVertices1 = new Vector3[baseVertices1.Length];
        for (int i = 0; i < baseVertices1.Length; i++)
        {
            newVertices1[i] = baseVertices1[i];
        }
        mesh2 = wheel2.GetComponentInChildren<MeshFilter>().mesh;
        baseVertices2 = mesh2.vertices;
        newVertices2 = new Vector3[baseVertices2.Length];
        for (int i = 0; i < baseVertices2.Length; i++)
        {
            newVertices2[i] = baseVertices2[i];
        }
        mesh3 = wheel3.GetComponentInChildren<MeshFilter>().mesh;
        baseVertices3 = mesh3.vertices;
        newVertices3 = new Vector3[baseVertices3.Length];
        for (int i = 0; i < baseVertices3.Length; i++)
        {
            newVertices3[i] = baseVertices3[i];
        }
        mesh4 = wheel4.GetComponentInChildren<MeshFilter>().mesh;
        baseVertices4 = mesh4.vertices;
        newVertices4 = new Vector3[baseVertices4.Length];
        for (int i = 0; i < baseVertices4.Length; i++)
        {
            newVertices4[i] = baseVertices4[i];
        }

    }

    // Update is called once per frame
    void Update()
    {

        displacement = stopP - startP;
        displacement = Vector3.Lerp(startP, stopP, dt);
        DoTransform();
    }

    void DoTransform(){
        Matrix4x4 scale = HW_Transforms.ScaleMat(0.4f,0.4f,0.4f);
        Matrix4x4 translation = HW_Transforms.TranslationMat(0,-0.5f,0);
        Matrix4x4 rueda1 = HW_Transforms.TranslationMat(poswheel1.x , poswheel1.y, poswheel1.z);
        Matrix4x4 rueda2 = HW_Transforms.TranslationMat(poswheel2.x , poswheel2.y , poswheel2.z);
        Matrix4x4 rueda3 = HW_Transforms.TranslationMat(poswheel3.x , poswheel3.y , poswheel3.z);
        Matrix4x4 rueda4 = HW_Transforms.TranslationMat(poswheel4.x , poswheel4.y, poswheel4.z);


        Matrix4x4 move= HW_Transforms.TranslationMat(displacement.x *Time.time , displacement.y *Time.time, displacement.z *Time.time);
        Matrix4x4 moveOrigin= HW_Transforms.TranslationMat(-displacement.x, -displacement.y, -displacement.z);
        Matrix4x4 moveObject= HW_Transforms.TranslationMat(displacement.x, displacement.y, displacement.z);
        Matrix4x4 rotate = HW_Transforms.RotateMat(angle * Time.time, rotationAxis );
        Matrix4x4 composite =  move  * rotate ;
        Matrix4x4 composite1 = composite * rueda1;
        Matrix4x4 composite2 = composite * rueda2;
        Matrix4x4 composite3 = composite * rueda3;
        Matrix4x4 composite4 = composite * rueda4;

        for (int i=0; i<newVertices.Length; i++)
        {
            Vector4 temp = new Vector4(baseVertices[i].x, baseVertices[i].y, baseVertices[i].z, 1);

            newVertices[i] = composite * temp;
        }
        for (int i=0; i<newVertices1.Length; i++)
        {
            Vector4 temp1 = new Vector4(baseVertices1[i].x, baseVertices1[i].y, baseVertices1[i].z, 1);

            newVertices1[i] = composite1 * temp1;
        }
        for (int i=0; i<newVertices2.Length; i++)
        {
            Vector4 temp2 = new Vector4(baseVertices2[i].x, baseVertices2[i].y, baseVertices2[i].z, 1);

            newVertices2[i] = composite2 * temp2;
        }
        for (int i=0; i<newVertices3.Length; i++)
        {
            Vector4 temp3 = new Vector4(baseVertices3[i].x, baseVertices3[i].y, baseVertices3[i].z, 1);

            newVertices3[i] = composite3 * temp3;
        }
        for (int i=0; i<newVertices4.Length; i++)
        {
            Vector4 temp4 = new Vector4(baseVertices4[i].x, baseVertices4[i].y, baseVertices4[i].z, 1);

            newVertices4[i] = composite4 * temp4;
        }


        mesh.vertices = newVertices;
        mesh.RecalculateNormals();
        mesh1.vertices = newVertices1;
        mesh1.RecalculateNormals();
        mesh2.vertices = newVertices2;
        mesh2.RecalculateNormals();
        mesh3.vertices = newVertices3;
        mesh3.RecalculateNormals();
        mesh4.vertices = newVertices4;
        mesh4.RecalculateNormals();

    }
    public void setDestination(Vector3 destination)
    {
        startP = stopP;
        stopP = destination;

    }
}