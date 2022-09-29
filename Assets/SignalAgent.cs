using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Unity.MLAgents;
using Unity.MLAgents.Actuators;
using Unity.MLAgents.Sensors;
using UnityEngine.SceneManagement;

public class SignalAgent : Agent
{
    [SerializeField] Signal signalObj1;
    [SerializeField] Signal signalObj2;
    [SerializeField] Signal signalObj3;

    public override void Initialize()
    {
        if (!Academy.Instance.IsCommunicatorOn)
        {
            this.MaxStep = 0;
        }
    }

    // Start is called before the first frame update
    void Start()
    {
        Academy.Instance.AutomaticSteppingEnabled = false;
        Academy.Instance.OnEnvironmentReset += EpisodeBegin;
        Manager.ResetRequestChanged += ResetRequested;
        Manager.PassedCounterChanged += CarCrossed;
    }

    public void EpisodeBegin()
    {
        SetReward(0);
        Manager.Instance.ResetEnvironment();
        signalObj1.OnEnvironmentReset();
        signalObj2.OnEnvironmentReset();
        signalObj3.OnEnvironmentReset();

        Debug.Log("Episode begin");
    }

    
    public override void CollectObservations(VectorSensor sensor)
    {
        SignalInfo signalInfo1 = signalObj1.signalInfo;
        SignalInfo signalInfo2 = signalObj2.signalInfo;
        SignalInfo signalInfo3 = signalObj3.signalInfo;

        sensor.AddObservation(signalInfo1.timerOn);
        sensor.AddObservation(signalInfo1.signalCounter);
        sensor.AddObservation(signalInfo1.signalState);
        sensor.AddObservation(signalInfo1.firstSpeed);

        sensor.AddObservation(signalInfo2.timerOn);
        sensor.AddObservation(signalInfo2.signalCounter);
        sensor.AddObservation(signalInfo2.signalState);
        sensor.AddObservation(signalInfo2.firstSpeed);

        sensor.AddObservation(signalInfo3.timerOn);
        sensor.AddObservation(signalInfo3.signalCounter);
        sensor.AddObservation(signalInfo3.signalState);
        sensor.AddObservation(signalInfo3.firstSpeed);
    }

    public override void OnActionReceived(ActionBuffers actionBuffers)
    {

        byte act = (byte)actionBuffers.DiscreteActions[0];
        BitArray comb = new BitArray(new byte[] { act });

        signalObj1.NewSignal(comb[0]);
        signalObj2.NewSignal(comb[1]);
        signalObj3.NewSignal(comb[2]);

        AddReward(-1 * ((signalObj1.signalInfo.signalCounter + signalObj2.signalInfo.signalCounter + signalObj3.signalInfo.signalCounter) / 3));
        // Reset Request and Car Crossed will be called automatically by events
    }

    void ResetRequested()
    {
        Manager.Instance.resetRequest = false;
        AddReward(-20);
        EndEpisode();
    }

    void CarCrossed()
    {
        AddReward(10);
    }
}
