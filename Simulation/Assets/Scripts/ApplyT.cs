// Domingo Mora Perez
//Cristina Gonzalez

using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class ApplyT : MonoBehaviour
{
    [SerializeField] float carscale;
    [SerializeField] float wheelScale;
    [SerializeField] GameObject wheelPreFab;
    [SerializeField] List<Vector3> wheels;
    [SerializeField] Vector3 startPos;
    [SerializeField] Vector3 stopPos;
    Mesh mesh;
    Vector3[] baseVertices;
    Vector3[] newVertices;
    List<Mesh> wheelMesh;
    List<Vector3[]> baseVerticesWheels;
    List<Vector3[]> newVerticesWheels;
    List<GameObject> wheelObjects;
    Matrix4x4 composite; //
    Matrix4x4 wheelcomposite; //
    void Start()
    {
        mesh = GetComponentInChildren<MeshFilter>().mesh;
        baseVertices = mesh.vertices;
        newVertices = new Vector3[baseVertices.Length];
        wheelMesh = new List<Mesh>();
        baseVerticesWheels = new List<Vector3[]>();
        newVerticesWheels = new List<Vector3[]>();
        wheelObjects = new List<GameObject>();
        

        foreach(Vector3 wheel in wheels)
        {
            GameObject wheelObject = Instantiate(wheelPreFab, new Vector3(0,0,0), Quaternion.identity);
            wheelObjects.Add(wheelObject);
            
        }
        for(int i = 0; i < wheelObjects.Count; i++)
        {
            wheelMesh.Add(wheelObjects[i].GetComponentInChildren<MeshFilter>().mesh);
            baseVerticesWheels.Add(wheelMesh[i].vertices);
            newVerticesWheels.Add(new Vector3[baseVerticesWheels[i].Length]);
        }

    }
    Vector3 Target(Vector3 actualPosition, Vector3 newPosition)
    {
        if(this.stopPos != newPosition)
        {
            startPos = actualPosition;
            stopPos = newPosition;
            Vector3 interpolation = Vector3.Lerp(startPos, stopPos, 1);
            return interpolation;
        }
        else
        {
            return newPosition;
        }
    }
    public void StartMovement(Vector3 actualPosition, Vector3 newPosition)
    {
        Vector3 interpolation = Target(actualPosition, newPosition);
        DoTransform(interpolation);
    }
    void DoTransform(Vector3 interpolation)
    {
        Matrix4x4 move = HW_Transforms.TranslationMat(interpolation.x, interpolation.y, interpolation.z);
        Matrix4x4 scale = HW_Transforms.ScaleMat(carscale, carscale, carscale);
        if(interpolation.x != 0)
        {
            float angle = Mathf.Atan2(stopPos.z - startPos.z, stopPos.x - startPos.x)* Mathf.Rad2Deg;
            Matrix4x4 rotation = HW_Transforms.RotateMat(angle, AXIS.Y);
            composite = move * rotation * scale;

        }
        else
        {
            composite = move * scale;
        }
        for (int i = 0; i < newVertices.Length; i++)
        {
            Vector4 temp = new Vector4(baseVertices[i].x,baseVertices[i].y, baseVertices[i].z, 1 );
            newVertices[i] = composite * temp;

        }
        mesh.vertices = newVertices;
        mesh.RecalculateNormals();
        mesh.RecalculateBounds();
        for(int i = 0; i < wheelObjects.Count; i++)
        {
            Matrix4x4 wheelscale = HW_Transforms.ScaleMat(wheelScale, wheelScale, wheelScale);
            Matrix4x4 wheelrotation = HW_Transforms.RotateMat(90 * Time.time, AXIS.X);
            Matrix4x4 wheelmove = HW_Transforms.TranslationMat(wheels[i].x, wheels[i].y,wheels[i].z);
            wheelcomposite = composite * wheelmove * wheelrotation * wheelscale;
            for(int j = 0; j < newVerticesWheels[i].Length; j++)
            {
                Vector4 temp = new Vector4(baseVerticesWheels[i][j].x, baseVerticesWheels[i][j].y, baseVerticesWheels[i][j].z, 1);
                newVerticesWheels[i][j] = wheelcomposite * temp;
            }
            wheelMesh[i].vertices = newVerticesWheels[i];
            wheelMesh[i].RecalculateNormals();
            wheelMesh[i].RecalculateBounds();
        }
    }
}