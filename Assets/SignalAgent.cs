using System.IO;
using System.Collections;
using UnityEngine;
using Unity.MLAgents;
using Unity.MLAgents.Actuators;
using Unity.MLAgents.Sensors;
using System.Threading;

public class SignalAgent : Agent
{
    [SerializeField] Signal signalObj1;
    [SerializeField] Signal signalObj2;
    [SerializeField] Signal signalObj3;

    // Start is called before the first frame update
    void Start()
    {
        Academy.Instance.AutomaticSteppingEnabled = false;

        Academy.Instance.OnEnvironmentReset += EpisodeBegin;
        Manager.CarCrashed += Crashed;
        Manager.PassedCounterChanged += CarCrossed;
    }

    public void HandleEnvReset()
    {
        signalObj1.OnEnvironmentReset();
        signalObj2.OnEnvironmentReset();
        signalObj3.OnEnvironmentReset();
    }

    public void EpisodeBegin()
    {
        Manager.Instance.OnNewEpisode();
        SetReward(0);
        HandleEnvReset();
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

        // sensor.AddObservation(Manager.Instance.StopCount);
    }

    public override void OnActionReceived(ActionBuffers actionBuffers)
    {
        // Action space 8: signal independent
        byte act = (byte)actionBuffers.DiscreteActions[0];
        BitArray comb = new BitArray(new byte[] { act });

        // Action space 3:
        /*int on = actionBuffers.DiscreteActions[0];
        BitArray comb = new BitArray(3, false);
        comb[on] = true;*/

        signalObj1.NewSignal(comb[0]);
        signalObj2.NewSignal(comb[1]);
        signalObj3.NewSignal(comb[2]);

        AddReward(-1 * ((signalObj1.signalInfo.signalCounter + signalObj2.signalInfo.signalCounter + signalObj3.signalInfo.signalCounter) / 3));
        
        
        // Reset Request and Car Crossed will be called automatically by events
    }

    void Crashed()
    {
        AddReward(-20);
        EndEpisode();
    }

    void CarCrossed()
    {
        AddReward(10);
    }

    private void FixedUpdate()
    {
        Manager.Instance.ep_time += Time.deltaTime;
    }
}
