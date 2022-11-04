using System;
using UnityEngine;
using System.Threading;
using System.IO;

public class Manager : MonoBehaviour
{
    public static Manager Instance;
    public bool resetRequest;
    public bool crashHandled;

    private readonly Mutex stopMutex = new Mutex();
    private readonly Mutex passedMutex = new Mutex();
    private readonly Mutex stopTimeMutex = new Mutex();
    private readonly Mutex crashHandleMutex = new Mutex();

    public static event Action ResetRequestChanged;

    private int stopCount;
    private float accummulatedStopTime;
    private int passedCounter;
    public float ep_time;

    private StreamWriter writer;
    private string filePath;

    [SerializeField] Spawner spawner1;
    [SerializeField] Spawner spawner2;
    [SerializeField] Spawner spawner3;

    void Awake() 
    {
        Instance = this;
        stopCount = 0;
        ep_time = 0;
        passedCounter = 0;
        accummulatedStopTime = 0;
        crashHandled = false;

        filePath = "data/rewards.csv";
        writer = new StreamWriter(filePath, false);
    }

    public void UpdateResetRequest(bool state)
    {
        if (state == false)
        {
            crashHandleMutex.WaitOne();
            if (crashHandled)
            {
                crashHandled = false;
                return;
            }
            else
            {
                crashHandled = true;
            }
            crashHandleMutex.ReleaseMutex();
        }
        resetRequest = state;
        ClearScene();
        WriteDataToFile();
        ResetRequestChanged?.Invoke();
        ResetEnvironment();
    }

    public void ACarStopped()
    {
        stopMutex.WaitOne();

        stopCount++;

        stopMutex.ReleaseMutex();
    }

    public void UpdateCarPassed()
    {
        passedMutex.WaitOne();

        passedCounter++;

        passedMutex.ReleaseMutex();
    }

    public void AddStopTime(float stopTime)
    {
        stopTimeMutex.WaitOne();

        accummulatedStopTime += stopTime;

        stopTimeMutex.ReleaseMutex();
    }

    public void ClearScene()
    {
        spawner1.StopSpawning();
        spawner2.StopSpawning();
        spawner3.StopSpawning();

        var carObjects = GameObject.FindGameObjectsWithTag("car");
        foreach (var carObject in carObjects)
        {
            accummulatedStopTime += carObject.GetComponent<Car>().StopTime;
            Destroy(carObject);
        }
    }

    public void ResetEnvironment()
    {
        accummulatedStopTime = 0;
        stopCount = 0;
        passedCounter = 0;
        ep_time = 0;

        spawner1.StartSpawning();
        spawner2.StartSpawning();
        spawner3.StartSpawning();
    }

    void WriteDataToFile()
    {
        string content = $"{ep_time} , {passedCounter} , {stopCount} , {accummulatedStopTime}";
        writer.WriteLine(content);
        Debug.Log(content);
        writer.Flush();
    }
}
