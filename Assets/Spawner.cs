using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Spawner : MonoBehaviour
{
    public GameObject spawnObject;
    // Start is called before the first frame update
    void Start()
    {
        StartSpawning();
    }

    IEnumerator SpawnObject()
    {
        yield return new WaitForSeconds(Random.Range(5, 10));
        int randomDistance = 8;
        Instantiate(spawnObject, transform.position + transform.TransformDirection(Vector3.forward * randomDistance), transform.rotation);
        StartCoroutine(SpawnObject());
    }

    IEnumerator SpawnObject(int x)
    {
        yield return new WaitForSeconds(x);
        int randomDistance = 11;
        Instantiate(spawnObject, transform.position + transform.TransformDirection(Vector3.forward * randomDistance), transform.rotation);
        StartCoroutine(SpawnObject());
    }

    public void StopSpawning()
    {
        StopAllCoroutines();
    }

    public void StartSpawning()
    {
        StartCoroutine(SpawnObject(1));
    }
}
