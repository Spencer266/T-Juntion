using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using TMPro;
using System;

public class Displayer : MonoBehaviour
{
    public Signal signalObj;
    public TextMeshProUGUI textDisplayer;

    private SignalInfo displayInfo;
    // Start is called before the first frame update
    void Start()
    {
        textDisplayer.text = "Testing";
    }

    // Update is called once per frame
    void Update()
    {
        displayInfo = signalObj.SendSignalInfo();
        TimeSpan time = TimeSpan.FromSeconds(displayInfo.signalTimer);
        textDisplayer.text = String.Format("\nStopping: {0}\n{1} - {2}",
                                            displayInfo.signalCounter,
                                            displayInfo.signalState,
                                            time.ToString(@"mm\:ss\:fff"));
    }
}
