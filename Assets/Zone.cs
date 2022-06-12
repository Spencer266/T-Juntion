using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Zone : MonoBehaviour
{
    public int counter = 0;
    // Start is called before the first frame update
    void Start()
    {
        
    }

    private void CheckStop()
    {
        RaycastHit[] hits;
        hits = Physics.RaycastAll(transform.position, transform.forward, 20f);
        Debug.DrawRay(transform.position, transform.forward * 20f, Color.blue);
        counter = 0;

        foreach (RaycastHit hit in hits)
        {
            if (hit.collider.GetComponent<Rigidbody>().velocity == Vector3.zero)
            {
                counter++;
            }
        }
    }

    void FixedUpdate()
    {
        CheckStop();
        Debug.Log(counter);
    }
}
