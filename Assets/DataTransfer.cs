using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using Newtonsoft.Json;
using UnityEngine;
using System.Threading;

public class DataTransfer : MonoBehaviour
{
    public Signal signalObj;

    private Thread SocketThread;
    void Start()
    {
        Application.runInBackground = true;
        StartServer();
    }

    void StartServer()
    {
        SocketThread = new Thread(NetworkCode)
        {
            IsBackground = true
        };
        SocketThread.Start();
    }

    void NetworkCode()
    {
        // Setup server addresses
        var localIp = IPAddress.Any;
        var localPort = 1308;
        var localEndPoint = new IPEndPoint(localIp, localPort);
        
        // Setup socket
        var socket = new Socket(AddressFamily.InterNetwork, SocketType.Dgram, ProtocolType.Udp);
        socket.Bind(localEndPoint);
        Debug.Log($"Local socket bind to {localEndPoint}. Waiting for request ...");

        var size = 1024;
        var receiveBuffer = new byte[size];

        // Define sending data
        SignalInfo sendData;
        string jsonData;
        byte[] sendBuffer;

        while (true)
        {
            // Endpoint address of remote client
            EndPoint remoteEndpoint = new IPEndPoint(IPAddress.Any, 0);

            // Receiving data
            var length = socket.ReceiveFrom(receiveBuffer, ref remoteEndpoint);
            var text = Encoding.ASCII.GetString(receiveBuffer, 0, length);
            Debug.Log($"Received from {remoteEndpoint}: {text}");

            // Prepare sending data
            sendData = signalObj.SendSignalInfo();
            jsonData = JsonConvert.SerializeObject(sendData);
            sendBuffer = Encoding.Default.GetBytes(jsonData);

            socket.SendTo(sendBuffer, remoteEndpoint);
            Array.Clear(receiveBuffer, 0, size);

            //System.Threading.Thread.Sleep(1);
        }
    }

    void StopServer()
    {
        //stop thread
        if (SocketThread != null)
        {
            SocketThread.Abort();
        }
    }

    void OnDisable()
    {
        StopServer();
    }
}