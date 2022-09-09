using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Unity.MLAgents;

public class Manager : MonoBehaviour
{
    public static Manager Instance;
    public bool resetRequest;
    public int passedCounter;

    public static event Action Crashed;
    public static event Action ResetRequestChanged;
    public static event Action PassedCounterChanged;

    [SerializeField] Spawner spawner1;
    [SerializeField] Spawner spawner2;
    [SerializeField] Spawner spawner3;

    void Awake() 
    {
        Instance = this;
        resetRequest = false;
        passedCounter = 0;
    }

    public void UpdateResetRequest(bool state)
    {
        if (!resetRequest == state)
        {
            if (state == false)
            {
                Crashed?.Invoke();
            }

            ResetEnvironment();
            resetRequest = false;
            ResetRequestChanged?.Invoke();
        }
        else
        {
            resetRequest = true;
        }
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

        passedCounter = 0;
    }
    private void Update()
    {
        
    }
}
