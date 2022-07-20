using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Manager : MonoBehaviour
{
    public static Manager Instance;
    public bool resetRequest;
    public int passedCounter;

    public static event Action ResetRequestChanged;
    public static event Action PassedCounterChanged;

    [SerializeField] Spawner spawner1;
    [SerializeField] Spawner spawner2;
    [SerializeField] Spawner spawner3;

    void Awake() 
    {
        Instance = this;
        resetRequest = false;
    }

    public void UpdateResetRequest(bool state)
    {
        resetRequest = state;
        ResetRequestChanged?.Invoke();
    }

    public void UpdateCarPassed()
    {
        passedCounter++;
        PassedCounterChanged?.Invoke();
    }

    public void ResetEnvironment()
    {
        var carObjects = GameObject.FindGameObjectsWithTag("car");
        foreach (var carObject in carObjects)
        {
            Destroy(carObject);
        }

        spawner1.RandomSpawn();
        spawner2.RandomSpawn();
        spawner3.RandomSpawn();
    }
    private void Update()
    {
        
    }
}
