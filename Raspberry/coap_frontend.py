import os
import asyncio
import aiocoap
from decouple import config
import sys
from datetime import datetime
import serial

from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_ssh_public_key


"""
CoAP FrontEnd Client for Raspberry PI.
"""


COAP_SERVER_ADDRESS = config('coap_server_address', None)
COAP_PORT = config('coap_port', None)


async def the_great_infinity():
    """
    Get data from the Arduino. Use the Post function to send the data to coap_server
    Server is hosted in the cloud
    """
    try:
        ser = serial.Serial('/dev/ttyACM0', 38400)
    except serial.serialutil.SerialException:
        sys.exit("Err: couldn't open port!")

    while True:
        print(ser.readline().decode())
        data = ser.readline().decode().strip().split(',')
        try:
            data = list(map(float, data[:6])) + [int(data[6])]

            # made a single payload line, encoded it
            data = " ".join(str(item) for item in data).encode()

            # send the data
            try:
                await post(data)
            except aiocoap.error.NetworkError:
                print("Err: server is unavailable!")
        except IndexError:
            # There could be a possible index error, if any of the sensor misses
            # it will pass for now.
            pass


async def encrypt(data: bytes):
    """encrypt the data using public key encryption system.
    if there's no public key available, it will send the data as it is.

    Args:
        data (bytes): _description_
    """
    filename = "awesome_secret.pub"
    directory = "ssh_keys"
    path = os.path.join(directory, filename)
    if not os.path.isfile(path):
        return data
    else:
        with open(os.path.join(directory, filename), "rb") as key_file:
            ssh_key_data = key_file.read()
            loaded_public_key = load_ssh_public_key(ssh_key_data)

        encrypted_data = loaded_public_key.encrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return encrypted_data


async def post(payload: bytes):
    """
    CoAP Client.
    This end sends a post request to CoAP Server.

    Args:
        payload (bytes): byte payload that includes accelorometer, gyro and heartbeat all in 1 line
    """
    # Create a context and a request
    payload = await encrypt(payload)  # this encrypt the data, probably
    context = await aiocoap.Context.create_client_context()
    request = aiocoap.Message(code=aiocoap.POST)

    # Set the request URI to the hello resource we created
    request.set_request_uri(
        'coap://{}:{}/hello'.format(COAP_SERVER_ADDRESS, COAP_PORT))

    # Set the request payload
    request.payload = payload

    # # Send the request and wait for the response
    response = await context.request(request).response

    # Print the response payload
    now = datetime.utcnow()
    print('{}: {}: {}'.format(now, response.code, response.payload))

if __name__ == "__main__":
    if COAP_SERVER_ADDRESS is None or COAP_PORT is None:
        sys.exit("COAP Server Address or Port Not Found. Terminated!")
    asyncio.run(the_great_infinity())
