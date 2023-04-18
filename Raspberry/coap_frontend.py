import asyncio
import aiocoap
from decouple import config
import sys
from datetime import datetime
import serial


"""
CoAP FrontEnd Client for Raspberry PI.
"""


COAP_SERVER_ADDRESS = config('coap_server_address', None)
COAP_PORT = config('coap_port', None)


def the_great_infinity():
    """
    Get data from the Arduino. Use the Post function to send the data to coap_server
    Server is hosted in the cloud
    """
    try:
        ser = serial.Serial('/dev/ttyACM0', 38400)
    except serial.serialutil.SerialException:
        sys.exit("Err: couldn't open port!")

    while True:
        data = ser.readline().decode().strip().split(',')
        data = list(map(float, data[:6])) + [int(data[6])]

        # made a single payload line, encoded it
        data = " ".join(str(item) for item in data).encode()

        # send the data
        post(data)


async def post(payload: bytes):
    """
    CoAP Client.
    This end sends a post request to CoAP Server.

    Args:
        payload (bytes): byte payload that includes accelorometer, gyro and heartbeat all in 1 line
    """
    # Create a context and a request
    context = await aiocoap.Context.create_client_context()
    request = aiocoap.Message(code=aiocoap.POST)

    # Set the request URI to the hello resource we created
    request.set_request_uri(
        'coap://{}:{}/hello'.format(COAP_SERVER_ADDRESS, COAP_PORT))

    # Set the request payload
    request.payload = payload

    # Send the request and wait for the response
    response = await context.request(request).response

    # Print the response payload
    now = datetime.utcnow()
    print('{}: {}: {}'.format(now, response.code, response.payload))


if __name__ == "__main__":
    if COAP_SERVER_ADDRESS is None or COAP_PORT is None:
        sys.exit("COAP Server Address or Port Not Found. Terminated!")
    asyncio.run(the_great_infinity())
