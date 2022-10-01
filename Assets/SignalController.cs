using System.IO;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class SignalController : MonoBehaviour
{
    [SerializeField] Signal signalObj1;
    [SerializeField] Signal signalObj2;
    [SerializeField] Signal signalObj3;
    [SerializeField] ControllerConfig config;

    private float MaxTime;
    private int MaxStep;

    private float m_timer;
    private float timer;
    private int step;
    private int episode;

    private int passedCounter = 0;
    private float step_rewards;
    private float ep_rewards;

    private StreamWriter writer;
    private string filePath;

    // Start is called before the first frame update
    void Start()
    {
        MaxTime = config.SumTime - config.MaxTimeOn;
        MaxStep = config.MaxStep;

        Manager.Crashed += Crashed;
        Manager.PassedCounterChanged += CarPassed;
        Manager.ResetRequestChanged += OnReset;

        episode = 0;
        OnReset();

        filePath = "data/rewards.csv";
        writer = new StreamWriter(filePath, false);
        writer.WriteLine("Episode, Reward");
    }

    void OnReset()
    {
        signalObj1.OnEnvironmentReset();
        signalObj2.OnEnvironmentReset();
        signalObj3.OnEnvironmentReset();

        signalObj1.available = true;
        signalObj2.available = false;
        signalObj3.available = false;

        passedCounter = 0;
        step = 0;
        timer = 0;
        m_timer = 0;
        episode++;
        ep_rewards = 0;
    }

    void Crashed()
    {
        AddReward(config.CrashReward);
        WriteDataToFile();
        Debug.Log($"{episode}, {ep_rewards} crashed");
    }

    void CarPassed()
    {
        passedCounter++;
        AddReward(config.CarPassedReward);
    }

    void AddReward(float value)
    {
        step_rewards += value;
        ep_rewards += value;
    }

    void SetReward(float value)
    {
        ep_rewards += (value - step_rewards);
        step_rewards = value;
    }

    void WriteDataToFile()
    {
        if (ep_rewards == config.CrashReward)
        {
            episode--;
            return;
        }
        string content = $"{episode}, {m_timer}, {passedCounter}, {ep_rewards}";
        writer.WriteLine(content);
        writer.Flush();
    }

    void FixedUpdate()
    {
        step_rewards = 0;

        // Time scaling to change simulation speed
        if (Input.GetKeyDown(KeyCode.RightArrow))
        {
            Time.timeScale *= 2f;
            Debug.Log("Simulation speed: " + Time.timeScale);
        }
        if (Input.GetKeyDown(KeyCode.LeftArrow))
        {
            Time.timeScale = 0.5f;
            Debug.Log("Simulation speed: " + Time.timeScale);
        }

        AddReward(config.WaitTimeReward * ((signalObj1.signalInfo.timerOn + signalObj2.signalInfo.timerOn + signalObj3.signalInfo.timerOn)/3));

        if (timer >= MaxTime)
        {
            signalObj1.NewSignal(!signalObj1.available);
            signalObj2.NewSignal(!signalObj2.available);
            signalObj3.NewSignal(!signalObj3.available);

            timer = 0;
            MaxTime = config.SumTime - MaxTime;
        }

        // End episode when reach max step
        if (step >= MaxStep)
        {
            WriteDataToFile();
            Debug.Log($"{episode}, {ep_rewards} maxed episode");
            Manager.Instance.UpdateResetRequest(true);
        }

        if (episode > config.MaxEpisode)
            UnityEditor.EditorApplication.isPlaying = false;

        step++;

        timer += Time.deltaTime;
        m_timer += Time.deltaTime;
    }
}
