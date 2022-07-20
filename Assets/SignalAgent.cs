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

    // Start is called before the first frame update
    void Start()
    {
        Manager.ResetRequestChanged += ResetRequested;
        Manager.PassedCounterChanged += CarCrossed;
    }

    public override void OnEpisodeBegin()
    {
        Manager.Instance.ResetEnvironment();
        Debug.Log("Episode begin");
    }

    public override void CollectObservations(VectorSensor sensor)
    {
        SignalInfo signalInfo1 = signalObj1.signalInfo;
        SignalInfo signalInfo2 = signalObj2.signalInfo;
        SignalInfo signalInfo3 = signalObj3.signalInfo;

        sensor.AddObservation(signalInfo1.signalTimer);
        sensor.AddObservation(signalInfo1.signalCounter);
        sensor.AddObservation(signalInfo1.signalState);

        sensor.AddObservation(signalInfo2.signalTimer);
        sensor.AddObservation(signalInfo2.signalCounter);
        sensor.AddObservation(signalInfo2.signalState);

        sensor.AddObservation(signalInfo3.signalTimer);
        sensor.AddObservation(signalInfo3.signalCounter);
        sensor.AddObservation(signalInfo3.signalState);
    }

    public override void OnActionReceived(ActionBuffers actionBuffers)
    {
        float controlSignal1 = actionBuffers.DiscreteActions[0];
        float controlSignal2 = actionBuffers.DiscreteActions[1];
        float controlSignal3 = actionBuffers.DiscreteActions[2];

        signalObj1.available = controlSignal1 == 1? true : false;
        signalObj1.OnAvailableChange();

        signalObj2.available = controlSignal2 == 1 ? true : false;
        signalObj2.OnAvailableChange();

        signalObj3.available = controlSignal3 == 1 ? true : false;
        signalObj3.OnAvailableChange();
        // Reset Request and Car Crossed will be called automatically by events


    }

    public override void Heuristic(in ActionBuffers actionsOut)
    {

    }

    void ResetRequested()
    {
        // Debug.Log("Reseting Environment");
        Manager.Instance.resetRequest = false;
        SetReward(-0.5f);
        EndEpisode();
    }

    
    void CarCrossed()
    {
        // Debug.Log("Car passed");
        Manager.Instance.passedCounter--;
        SetReward(1);
    }
}
