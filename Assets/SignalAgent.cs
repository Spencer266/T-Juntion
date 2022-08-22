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
        Academy.Instance.AutomaticSteppingEnabled = false;
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
        bool controlSignal;
        if (signalObj1.allowDecision)
        {
            controlSignal = actionBuffers.DiscreteActions[0] == 1 ? true : false;
            if (controlSignal != signalObj1.available)
            {
                signalObj1.available = controlSignal;
                signalObj1.OnAvailableChange();
            }
        }
        
        if (signalObj2.allowDecision)
        {
            controlSignal = actionBuffers.DiscreteActions[1] == 1 ? true : false;
            if (controlSignal != signalObj2.available)
            {
                signalObj2.available = controlSignal;
                signalObj2.OnAvailableChange();
            }
        }
        
        if (signalObj3.allowDecision)
        {
            controlSignal = actionBuffers.DiscreteActions[2] == 1 ? true : false;
            if (controlSignal != signalObj3.available)
            {
                signalObj3.available = controlSignal;
                signalObj3.OnAvailableChange();
            }
        }       

        SetReward(-1 * (signalObj1.signalInfo.signalCounter + signalObj2.signalInfo.signalCounter + signalObj3.signalInfo.signalCounter));
        // Reset Request and Car Crossed will be called automatically by events
    }

    void ResetRequested()
    {
        // Debug.Log("Reseting Environment");
        Manager.Instance.resetRequest = false;
        SetReward(-20);
        EndEpisode();
    }

    void CarCrossed()
    {
        // Debug.Log("Car passed");
        Manager.Instance.passedCounter--;
        SetReward(10);
    }
}
