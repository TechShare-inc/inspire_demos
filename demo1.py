import time
from api.inspire_api import InspireHandAPI


motion = [
    [1000, 1000, 1000, 1000, 1000, 1000],
    [1000, 1000, 1000, 1000, 1000, 0],
    [1000, 1000, 1000, 1000, 1000, 1000],
    [1000, 1000, 1000, 1000, 200, 1000],
    [1000, 1000, 1000, 0, 200, 1000],
    [1000, 1000, 0, 0, 200, 1000],
    [1000, 0, 0, 0, 200, 1000],
    [0, 0, 0, 0, 200, 1000],
]


def main(port: str, baudrate: int):
    api = InspireHandAPI(port, baudrate)

    api.connect()

    api.reset_error()
    time.sleep(0.1)
    api.perform_open()
    time.sleep(0.8)

    try:
        while True:
            for i in range(len(motion)):
                api.set_angle(motion[i], 1)
                time.sleep(0.8)
    except KeyboardInterrupt:
        api.perform_open()
        time.sleep(0.8)
        print("Keyboard interrupt. Exiting...")
    finally:
        api.disconnect()
        print("Disconnected from the hand.")


if __name__ == "__main__":
    main(port="COM8", baudrate=115200)
