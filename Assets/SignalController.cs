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

    private float timer;
    private int step;
    private int episode;

    private float step_rewards;
    private float ep_rewards;

    // Start is called before the first frame update
    void Start()
    {
        MaxTime = config.MaxTimeSwitch;
        MaxStep = config.MaxStep;

        Manager.Crashed += Crashed;
        Manager.PassedCounterChanged += CarPassed;
        Manager.ResetRequestChanged += OnReset;
        timer = 0;
        episode = 0;
        step_rewards = 0;
        ep_rewards = 0;
        OnReset();
    }

    void OnReset()
    {
        signalObj1.available = true;
        signalObj2.available = false;
        signalObj3.available = false;
        step = 0;
        timer = 0;
        episode++;
        // Debug.Log("Episode: " + episode + " " + gameObject.name);
    }

    void Crashed()
    {
        AddReward(config.CrashReward);
        Debug.Log($"Episode {episode}: {ep_rewards}");
        ep_rewards = 0;
    }

    void CarPassed()
    {
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

        AddReward(config.WaitTimeReward * (signalObj1.signalInfo.timerOn + signalObj2.signalInfo.timerOn + signalObj3.signalInfo.timerOn));

        if (timer >= MaxTime)
        {
            signalObj1.NewSignal(!signalObj1.available);
            signalObj2.NewSignal(!signalObj2.available);
            signalObj3.NewSignal(!signalObj3.available);

            timer = 0;
        }

        // End episode when reach max step
        if (step >= MaxStep)
        {
            Debug.Log($"Episode {episode}: {ep_rewards}");
            ep_rewards = 0;
            Manager.Instance.UpdateResetRequest(true);
        }

        if (episode > config.MaxEpisode)
            UnityEditor.EditorApplication.isPlaying = false;

        step++;

        timer += Time.deltaTime;

        // Debug.Log(Time.timeScale);
    }
}
