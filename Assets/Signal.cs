using System.Collections;
using System;
using System.Collections.Generic;
using UnityEngine;

public struct SignalInfo
{
    public float signalTimer;
    public bool signalState;
    public int signalCounter;
    public float firstSpeed;

    public void GetInfo(float t, bool s, int c, float f)
    {
        signalTimer = t;
        signalState = s;
        signalCounter = c;
        firstSpeed = f;
    }
}

public class Signal : MonoBehaviour
{
    public List<int> direction;
    public bool available;
    public KeyCode switcher;
    public SignalInfo signalInfo;
    public bool allowDecision;

    private float currentTimer;
    private string state;
    private int counter = 0;
    private float firstSpeed;

    private void Start()
    {
        firstSpeed = 0;
        available = false;
        GetComponent<Renderer>().material.SetColor("_Color", Color.red);
        currentTimer = 0;
        state = "OFF";
        allowDecision = false;
    }
    private void CheckStop() 
    {
        RaycastHit[] hits;
        hits = Physics.RaycastAll(transform.position, transform.forward, 20f);
        Debug.DrawRay(transform.position, transform.forward * 20f, Color.blue);
        counter = 0;

        if (hits.Length != 0)
        {
            var minDist = 100000f;
            foreach (RaycastHit hit in hits)
            {
                var currentBody = hit.collider.GetComponent<Rigidbody>();
                // Get the number of cars on 1 lane that are stopping
                if (Vector3.Magnitude(currentBody.velocity) <= 0.01f)
                {
                    counter++;
                }
                float x = Vector3.Distance(currentBody.transform.position, transform.position);
                if (x < minDist)
                {
                    minDist = x;
                    firstSpeed = Vector3.Magnitude(currentBody.velocity);
                }
            }
            if (currentTimer > 3) allowDecision = false;
            if (minDist <= 3 && !allowDecision)
            {
                allowDecision = true;
                gameObject.GetComponentInParent<SignalAgent>().RequestDecision();
            }
            if (minDist > 3)
                allowDecision = false;
        }
    }

    private void OnTriggerExit(Collider collider)
    {
        allowDecision = true;
    }

    public void GetSignalInfo()
    {
        signalInfo.GetInfo(currentTimer, available, counter, firstSpeed);
    }

    public SignalInfo SendSignalInfo()
    {
        return signalInfo;
    }

    public void OnAvailableChange()
    {
        state = available ? "ON" : "OFF";
        currentTimer = 0;
    }
    void FixedUpdate()
    {
        GetSignalInfo();
        if (Input.GetKeyDown(switcher))
        {
            available = !available;
            OnAvailableChange();
        }

        GetComponent<Renderer>().material.SetColor("_Color", available ? Color.green : Color.red);
        // update timer
        currentTimer += Time.deltaTime;
        CheckStop();
    }
}
