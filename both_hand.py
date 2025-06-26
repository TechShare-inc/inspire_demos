import time
from api.inspire_api import InspireHandAPI
from concurrent.futures import ThreadPoolExecutor, as_completed

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
        print(f"Keyboard interrupt on port {port}. Exiting...")
    finally:
        api.disconnect()
        print(f"Disconnected from the hand on port {port}.")


if __name__ == "__main__":
    ports = ["COM8", "COM11"]  # 使用するポートをリストで指定
    baudrate = 115200

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(main, port, baudrate) for port in ports]

        try:
            # as_completedを使用して各スレッドの進行を監視
            for future in as_completed(futures):
                future.result()  # 各スレッドの実行結果を待機
        except KeyboardInterrupt:
            print("Keyboard interrupt received. Exiting...")
        finally:
            # スレッドプールを安全にシャットダウン
            executor.shutdown(wait=False)
            print("All threads have been terminated.")

