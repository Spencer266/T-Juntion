using UnityEngine;

[CreateAssetMenu(fileName = "Configuration", menuName = "ScriptableObjects/ControllerConfig", order = 1)]
public class ControllerConfig : ScriptableObject
{
    public float SumTime;
    public float MaxTimeOn;
    // MaxTimeOff = SumTime - MaxTimeOn

    public int MaxStep;
    public int MaxEpisode;

    public float CrashReward;
    public float CarPassedReward;
    public float WaitTimeReward;
}
