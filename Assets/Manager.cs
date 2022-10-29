using System;
using System.Threading;
using UnityEngine;

public class Manager : MonoBehaviour
{
    public static Manager Instance;
    public bool resetRequest;
    public int StopCount { get { return stopCount; } }
    public float StopTime { get { return accummulatedStopTime; } }

    private readonly Mutex crash = new Mutex();
    private readonly Mutex stopMutex = new Mutex();
    private readonly Mutex stopTimeMutex = new Mutex();
    private bool carCrash = false;
    private int stopCount;
    private float accummulatedStopTime;

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
        stopCount = 0;
        accummulatedStopTime = 0;
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

    public void ACarStopped()
    {
        stopMutex.WaitOne();

        stopCount++;

        stopMutex.ReleaseMutex();
    }

    public void AddStopTime(float amount)
    {
        stopTimeMutex.WaitOne();

        accummulatedStopTime += amount;

        stopTimeMutex.ReleaseMutex();
    }

    public void UpdateCarPassed()
    {
        PassedCounterChanged?.Invoke();
    }

    public void ClearScene()
    {
        var carObjects = GameObject.FindGameObjectsWithTag("car");
        foreach (var carObject in carObjects)
        {
            Destroy(carObject);
        }
    }


    public void ResetEnvironment()
    {
        stopCount = 0;
        accummulatedStopTime = 0;
        spawner1.RandomSpawn();
        spawner2.RandomSpawn();
        spawner3.RandomSpawn();
    }
}
