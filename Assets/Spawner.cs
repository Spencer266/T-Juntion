using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Spawner : MonoBehaviour
{
    public GameObject spawnObject;
    // Start is called before the first frame update
    void Start()
    {
        StartCoroutine(SpawnObject());
    }

    IEnumerator SpawnObject()
    {
        yield return new WaitForSeconds(Random.Range(10, 15));
        Instantiate(spawnObject, transform.position + transform.TransformDirection(Vector3.forward), transform.rotation);
        StartCoroutine(SpawnObject());
    }
}
