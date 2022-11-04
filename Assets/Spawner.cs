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
        Instantiate(spawnObject, transform.position + transform.TransformDirection(Vector3.forward), transform.rotation);
        StartCoroutine(SpawnObject());
    }

    public void RandomSpawn()
    {
        /*if (Random.Range(0, 1) == 0)
            return;*/

        int randomDistance = Random.Range(10, 20);
        Instantiate(spawnObject, transform.position + transform.TransformDirection(Vector3.forward*randomDistance), transform.rotation);
    }

    public void StopSpawning()
    {
        StopAllCoroutines();
    }

    public void StartSpawning()
    {
        StartCoroutine(SpawnObject());
    }
}
