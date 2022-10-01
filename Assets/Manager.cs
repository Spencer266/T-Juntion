using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Unity.MLAgents;

public class Manager : MonoBehaviour
{
    public static Manager Instance;
    public bool resetRequest;

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
    }

    public void UpdateResetRequest(bool state)
    {
        if (!resetRequest == state)
        {
            if (state == false)
            {
                Crashed?.Invoke();
            }
            // !!! NOTE TO FIX: Potential bug might happend if ResetEnvironment() is called before
            // functions triggered by Crashed are done.
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
