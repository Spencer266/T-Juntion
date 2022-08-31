using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class SignalController : MonoBehaviour
{
    [SerializeField] Signal signalObj1;
    [SerializeField] Signal signalObj2;
    [SerializeField] Signal signalObj3;

    private float timer;
    private float counter;

    // Start is called before the first frame update
    void Start()
    {
        timer = 0;
        counter = 0;
        OnReset();
        Manager.ResetRequestChanged += OnReset;
    }

    void OnReset()
    {
        Manager.Instance.resetRequest = false;
        Manager.Instance.ResetEnvironment();
        signalObj1.available = true;
        signalObj2.available = false;
        signalObj3.available = false;
    }
    // Update is called once per frame
    void FixedUpdate()
    {
        if (timer >= 10)
        {
            signalObj1.NewSignal(!signalObj1.available);
            signalObj2.NewSignal(!signalObj2.available);
            signalObj3.NewSignal(!signalObj3.available);

            timer = 0;
            counter++;
        }

        if (counter == 10)
        {
            OnReset();
            counter = 0;
        }

        timer += Time.deltaTime;
    }
}
