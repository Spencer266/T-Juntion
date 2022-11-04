using System;
using System.IO;
using System.Threading;
using UnityEngine;

public class Manager : MonoBehaviour
{
    public static Manager Instance;
    public int StopCount { get { return stopCount; } }
    public float ep_time;

    private readonly Mutex crashHandleMutex = new Mutex();
    private readonly Mutex stopMutex = new Mutex();
    private readonly Mutex stopTimeMutex = new Mutex();
    private readonly Mutex passCountMutex = new Mutex();

    private bool crashHandled;
    private int stopCount;
    private float accummulatedStopTime;
    private int passedCount;

    public static event Action CarCrashed;
    public static event Action PassedCounterChanged;

    private StreamWriter writer;

    [SerializeField] Spawner spawner1;
    [SerializeField] Spawner spawner2;
    [SerializeField] Spawner spawner3;

    void Awake()
    {
        Instance = this;
        crashHandled = false;
        stopCount = 0;
        accummulatedStopTime = 0;
        passedCount = 0;

        writer = new StreamWriter("data/data.csv", false);
    }

    public void CrashHandle()
    {
        crashHandleMutex.WaitOne();
        
        if (crashHandled == false)
        {
            CarCrashed?.Invoke();
            crashHandled = true;
        }
        else
        {
            crashHandled = false;
        }
        crashHandleMutex.ReleaseMutex();
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
        passCountMutex.WaitOne();

        passedCount++;
        PassedCounterChanged?.Invoke();

        passCountMutex.ReleaseMutex();
    }

    private void ClearScene()
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


    private void ResetEnvironment()
    {
        stopCount = 0;
        accummulatedStopTime = 0;
        passedCount = 0;
        crashHandled = false;
        ep_time = 0;

        spawner1.StartSpawning();
        spawner2.StartSpawning();
        spawner3.StartSpawning();
    }

    void WriteDataToFile()
    {
        string content = $"{ep_time}, {passedCount}, {stopCount}, {accummulatedStopTime}";
        writer.WriteLine(content);
        Debug.Log(content);
        writer.Flush();
    }

    public void OnNewEpisode()
    {
        ClearScene();
        WriteDataToFile();
        ResetEnvironment();
    }
}
