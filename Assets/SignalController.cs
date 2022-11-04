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

    private float timer; // signal timer
    private int step;
    private int episode;


    // Start is called before the first frame update
    void Start()
    {
        MaxTime = config.SumTime - config.MaxTimeOn;
        MaxStep = config.MaxStep;

        Manager.ResetRequestChanged += OnReset;

        episode = 0;
        OnReset();
    }

    void OnReset()
    {
        signalObj1.OnEnvironmentReset();
        signalObj2.OnEnvironmentReset();
        signalObj3.OnEnvironmentReset();

        signalObj1.available = true;
        signalObj2.available = false;
        signalObj3.available = false;

        step = 0;
        timer = 0;
        episode++;
    }
    

    void FixedUpdate()
    {
        // Time scaling to change simulation speed
        if (Input.GetKeyDown(KeyCode.RightArrow))
        {
            Time.timeScale *= 2f;
            Debug.Log("Simulation speed: " + Time.timeScale);
        }
        if (Input.GetKeyDown(KeyCode.LeftArrow))
        {
            Time.timeScale *= 0.5f;
            Debug.Log("Simulation speed: " + Time.timeScale);
        }

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
            //Debug.Log($"{episode}, maxed episode");
            Manager.Instance.UpdateResetRequest(true);
        }

        if (episode > config.MaxEpisode)
            UnityEditor.EditorApplication.isPlaying = false;

        step++;

        timer += Time.deltaTime;
        Manager.Instance.ep_time += Time.deltaTime;
    }
}
