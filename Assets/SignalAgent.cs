using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Unity.MLAgents;
using Unity.MLAgents.Actuators;
using Unity.MLAgents.Sensors;
using UnityEngine.SceneManagement;

public class SignalAgent : Agent
{
    private Signal signalObj;
    // Start is called before the first frame update
    void Start()
    {
        signalObj = GetComponent<Signal>();
        Manager.ResetRequestChanged += ResetRequested;
        Manager.PassedCounterChanged += CarCrossed;
    }

    public override void OnEpisodeBegin()
    {
        Manager.Instance.ResetEnvironment();
    }

    public override void CollectObservations(VectorSensor sensor)
    {
        SignalInfo signalInfo = signalObj.signalInfo;
        sensor.AddObservation(signalInfo.firstSpeed);
        sensor.AddObservation(signalInfo.signalTimer);
        sensor.AddObservation(signalInfo.signalCounter);
        sensor.AddObservation(signalInfo.signalState);
    }

    public override void OnActionReceived(ActionBuffers actionBuffers)
    {
        float controlSignal = actionBuffers.DiscreteActions[0];
        signalObj.available = controlSignal == 1? true : false;
        Debug.Log(controlSignal);

        // Reset Request and Car Crossed will be called automatically by events


    }

    public override void Heuristic(in ActionBuffers actionsOut)
    {

    }

    void ResetRequested()
    {
        Debug.Log("Reseting Environment");
        Manager.Instance.resetRequest = false;
        SetReward(-0.5f);
        EndEpisode();
    }

    void CarCrossed()
    {
        Manager.Instance.passedCounter--;
        SetReward(1);
    }
}
