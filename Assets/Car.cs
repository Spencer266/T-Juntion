using UnityEngine;

struct CarInfo
{
    public Vector3 objVelocity;
    public Vector3 objPosition;
    public float objDistance;

    public void GetInfo(Vector3 v, Vector3 p, float d)
    {
        objDistance = d;
        objVelocity = v;
        objPosition = p;
    }
}

public class Car : MonoBehaviour
{
    [SerializeField] WheelCollider rearLeft;
    [SerializeField] WheelCollider rearRight;
    [SerializeField] WheelCollider backLeft;
    [SerializeField] WheelCollider backRight;

    public float accelerationForce;
    public float decelarationFactor;
    public float brakeForce;
    public float steerAngleLeft;
    public float steerAngleRight;

    public float currentAcceleration = 0f;
    private float currentBrake = 0f;
    private float currentSteerAngle = 0f;

    private Quaternion oldRotation;
    private int steering = 0;
    private int moveOption = 1;
    private bool passed = false;
    private bool entered = false;
    private bool obstacleInfront = false;
    private float running = 0;
    private float stopTime = 0;
    public float StopTime { get { return stopTime; } }

    void GoForward()
    {
        if (obstacleInfront)
        {
            currentAcceleration -= decelarationFactor;
            if (currentAcceleration < 0f)
            {
                currentAcceleration = 0f;
            }
        }
        else
        {
            currentAcceleration = accelerationForce;
        }
        currentBrake = 0f;
    }

    void Brake()
    {
        currentBrake = brakeForce;
    }

    int Turn(int direction)
    {
        currentBrake = 0f;
        float dotProduct = Quaternion.Dot(transform.localRotation, oldRotation);
        if (dotProduct <= 0.712f)
        {
            currentSteerAngle = 0f;
            moveOption = 1;
            return 0;
        }
        else
        {
            currentAcceleration = accelerationForce - 10f;
            currentSteerAngle = ((direction == -1) ? steerAngleLeft : steerAngleRight) * direction;
            return direction;
        }
    }


    private void OnTriggerEnter(Collider other)
    {
        if (other.CompareTag("signal"))
        {
            Signal collidedSignal = other.gameObject.GetComponent<Signal>();

            if (!entered)
            {
                // Randomly pick a moving options
                var rand = new System.Random();
                int pick = rand.Next(collidedSignal.direction.Count);
                moveOption = collidedSignal.direction[pick];

                // Save the old rotation for validating new rotation when turning
                oldRotation = transform.localRotation;

                entered = true;

                obstacleInfront = false;
            }
           
        }
    }

    private void OnTriggerExit(Collider other)
    {
        if (other.CompareTag("checker"))
        {
            Manager.Instance.UpdateCarPassed();
            passed = true;
        }

    }

    private void OnCollisionEnter(Collision collision)
    {
        if (collision.gameObject.CompareTag("car") && !passed)
        {
            Manager.Instance.AddStopTime(stopTime);
            Manager.Instance.CrashHandle();
        }

        if (collision.gameObject.CompareTag("destroyer"))
            Destroy(gameObject);
    }

    private bool LookFront()
    {
        RaycastHit hit;
        Vector3 direction = transform.TransformDirection(Vector3.forward);
        Vector3 origin = transform.position + new Vector3(0, 0.15f, 0) + direction * 0.6f;
        Ray detector = new Ray(origin, direction);

        float detectDistance = 2.4f;
        Debug.DrawRay(origin, direction * detectDistance, Color.red);
        if (Physics.Raycast(detector, out hit, detectDistance))
        {
            if (hit.collider.CompareTag("signal"))
                return !hit.collider.gameObject.GetComponent<Signal>().available;
            else if (hit.collider.CompareTag("destroyer"))
                return false;
            else
                return true;
        }
        return false;
    }


    void FixedUpdate()
    {
        // Decide how the car will move
        if (!entered)
            obstacleInfront = LookFront();

        switch (moveOption)
        {
            case 1:
                GoForward();
                break;
            case 2:
                steering = 1;
                steering = Turn(steering);
                break;
            case 3:
                steering = -1;
                steering = Turn(steering);
                break;
            /*case 0:
                Brake();
                break;*/
        }

        // Apply forces
        rearLeft.motorTorque = currentAcceleration;
        rearRight.motorTorque = currentAcceleration;

        rearLeft.brakeTorque = currentBrake;
        rearRight.brakeTorque = currentBrake;
        backLeft.brakeTorque = currentBrake;
        backRight.brakeTorque = currentBrake;

        rearLeft.steerAngle = currentSteerAngle;
        rearRight.steerAngle = currentSteerAngle;

        if (Vector3.Magnitude(GetComponent<Rigidbody>().velocity) <= 0.5f && currentAcceleration == 0)
        {
            if (running > 2f)
            {
                Manager.Instance.ACarStopped();
            }
            running = 0;
            stopTime += Time.deltaTime;
        }
        running += Time.deltaTime;

        // Logging
    }
}
