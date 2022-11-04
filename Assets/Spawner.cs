using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Spawner : MonoBehaviour
{
    public GameObject spawnObject;
    // Start is called before the first frame update
    void Start()
    {
        RandomSpawn();
    }

    IEnumerator SpawnObject()
    {
        yield return new WaitForSeconds(Random.Range(5, 10));
        float randomDistance = Random.Range(7, 9);
        Instantiate(spawnObject, transform.position + transform.TransformDirection(Vector3.forward * randomDistance), transform.rotation);
        StartCoroutine(SpawnObject());
    }

    public void RandomSpawn()
    {
        float randomDistance = 11;
        Instantiate(spawnObject, transform.position + transform.TransformDirection(Vector3.forward * randomDistance), transform.rotation);
        StartCoroutine(SpawnObject());
    }

    public void StopSpawning()
    {
        StopAllCoroutines();
    }

    public void StartSpawning()
    {
        RandomSpawn();
    }
}
