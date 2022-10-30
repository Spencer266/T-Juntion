using System;
using UnityEngine;
using System.Threading;

public class Manager : MonoBehaviour
{
    public static Manager Instance;
    public bool resetRequest;
    public int StopCount { get { return stopCount; } }
    public float StopTime { get { return accummulatedStopTime; } }

    private readonly Mutex stopMutex = new Mutex();
    private readonly Mutex stopTimeMutex = new Mutex();

    public static event Action Crashed;
    public static event Action ResetRequestChanged;
    public static event Action PassedCounterChanged;
    private int stopCount;
    private float accummulatedStopTime;

    [SerializeField] Spawner spawner1;
    [SerializeField] Spawner spawner2;
    [SerializeField] Spawner spawner3;

    void Awake() 
    {
        Instance = this;
        resetRequest = false;
        stopCount = 0;
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

    public void ACarStopped()
    {
        stopMutex.WaitOne();

        stopCount++;

        stopMutex.ReleaseMutex();
    }

    public void UpdateCarPassed()
    {
        PassedCounterChanged?.Invoke();
    }

    public void AddStopTime(float amount)
    {
        stopTimeMutex.WaitOne();

        accummulatedStopTime += amount;

        stopTimeMutex.ReleaseMutex();
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
        accummulatedStopTime = 0;
        stopCount = 0;
        spawner1.RandomSpawn();
        spawner2.RandomSpawn();
        spawner3.RandomSpawn();
    }
}
