using System;
using System.Threading;
using UnityEngine;

public class Manager : MonoBehaviour
{
    public static Manager Instance;
    public bool resetRequest;

    private Mutex crash = new Mutex();
    private bool carCrash = false;

    public static event Action ResetRequestChanged;
    public static event Action PassedCounterChanged;

    [SerializeField] Spawner spawner1;
    [SerializeField] Spawner spawner2;
    [SerializeField] Spawner spawner3;

    void Awake() 
    {
        Instance = this;
        resetRequest = false;
        carCrash = false;
    }

    public void UpdateResetRequest(bool state)
    {
        crash.WaitOne();
        
        if (carCrash == false)
        {
            ResetRequestChanged?.Invoke();
            carCrash = true;
        }
        else
        {
            carCrash = false;
        }
        crash.ReleaseMutex();
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
}
