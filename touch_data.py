import time
from pymodbus.client import ModbusTcpClient
from pymodbus.pdu import ExceptionResponse
import json
import datetime
from pathlib import Path
import numpy as np
from dataclasses import dataclass
import numpy.typing as npt

# 定义 Modbus TCP 相关参数
MODBUS_IP = "192.168.11.210"
MODBUS_PORT = 6000

# 定义各部分数据地址范围
TOUCH_SENSOR_BASE_ADDR_PINKY = 3000  # 小拇指
TOUCH_SENSOR_END_ADDR_PINKY = 3369

TOUCH_SENSOR_BASE_ADDR_RING = 3370  # 无名指
TOUCH_SENSOR_END_ADDR_RING = 3739

TOUCH_SENSOR_BASE_ADDR_MIDDLE = 3740  # 中指
TOUCH_SENSOR_END_ADDR_MIDDLE = 4109

TOUCH_SENSOR_BASE_ADDR_INDEX = 4110  # 食指
TOUCH_SENSOR_END_ADDR_INDEX = 4479

TOUCH_SENSOR_BASE_ADDR_THUMB = 4480  # 大拇指
TOUCH_SENSOR_END_ADDR_THUMB = 4899

TOUCH_SENSOR_BASE_ADDR_PALM = 4900  # 掌心
TOUCH_SENSOR_END_ADDR_PALM = 5123

# Modbus 每次最多读取寄存器的数量
MAX_REGISTERS_PER_READ = 125


@dataclass
class FingerSensorData:
    """Data class for individual finger sensor data."""

    top: npt.NDArray[np.int32]
    tip: npt.NDArray[np.int32]
    base: npt.NDArray[np.int32]


@dataclass
class ThumbSensorData:
    """Data class for thumb sensor data (includes mid sensor)."""

    top: npt.NDArray[np.int32]
    tip: npt.NDArray[np.int32]
    mid: npt.NDArray[np.int32]
    base: npt.NDArray[np.int32]


@dataclass
class TactileData:
    """Data class for all tactile sensor data with timestamp."""

    timestamp: float
    pinky: FingerSensorData
    ring: FingerSensorData
    middle: FingerSensorData
    index: FingerSensorData
    thumb: ThumbSensorData
    palm: npt.NDArray[np.int32]


def read_register_range(client, start_addr, end_addr):
    """
    批量读取指定地址范围内的寄存器数据。
    """
    register_values = []
    # 分段读取寄存器
    for addr in range(start_addr, end_addr + 1, MAX_REGISTERS_PER_READ * 2):
        current_count = min(MAX_REGISTERS_PER_READ, (end_addr - addr) // 2 + 1)
        response = client.read_holding_registers(address=addr, count=current_count)

        if isinstance(response, ExceptionResponse) or response.isError():
            print(f"读取寄存器 {addr} 失败: {response}")
            register_values.extend([0] * current_count)
        else:
            register_values.extend(response.registers)

    return register_values


def format_finger_data(finger_name, data) -> FingerSensorData:
    """
    Format regular finger tactile data into FingerSensorData structure.
    """
    if len(data) < 185:
        print(f"{finger_name} 数据长度不足，至少185个数据，实际：{len(data)}")
        return FingerSensorData(
            top=np.array([], dtype=np.int32),
            tip=np.array([], dtype=np.int32),
            base=np.array([], dtype=np.int32),
        )

    idx = 0
    # Top sensor data (3x3)
    top_data = np.array(data[idx : idx + 9], dtype=np.int32).reshape(3, 3)
    idx += 9

    # Tip sensor data (12x8)
    tip_data = np.array(data[idx : idx + 96], dtype=np.int32).reshape(12, 8)
    idx += 96

    # Base sensor data (10x8)
    base_data = np.array(data[idx : idx + 80], dtype=np.int32).reshape(10, 8)

    return FingerSensorData(top=top_data, tip=tip_data, base=base_data)


def format_thumb_data(data) -> ThumbSensorData:
    """
    Format thumb tactile data into ThumbSensorData structure.
    """
    if len(data) < 210:
        print(f"大拇指数据长度不足，至少210个数据，实际：{len(data)}")
        return ThumbSensorData(
            top=np.array([], dtype=np.int32),
            tip=np.array([], dtype=np.int32),
            mid=np.array([], dtype=np.int32),
            base=np.array([], dtype=np.int32),
        )

    idx = 0
    # Top sensor data (3x3)
    top_data = np.array(data[idx : idx + 9], dtype=np.int32).reshape(3, 3)
    idx += 9

    # Tip sensor data (12x8)
    tip_data = np.array(data[idx : idx + 96], dtype=np.int32).reshape(12, 8)
    idx += 96

    # Mid sensor data (3x3)
    mid_data = np.array(data[idx : idx + 9], dtype=np.int32).reshape(3, 3)
    idx += 9

    # Base sensor data (12x8)
    base_raw = np.array(data[idx : idx + 96], dtype=np.int32).reshape(12, 8)
    # Apply transformations for thumb base data
    base_data = np.flip(np.fliplr(base_raw), axis=0)

    return ThumbSensorData(top=top_data, tip=tip_data, mid=mid_data, base=base_data)


def format_palm_data(data):
    """
    Format palm data as 8x14 numpy array (transposed from original 14x8).
    """
    expected_len = 14 * 8
    if len(data) < expected_len:
        print(f"掌心数据长度不足，至少{expected_len}个数据，实际：{len(data)}")
        return None

    # Generate original matrix (14 rows, 8 columns)
    palm_matrix = np.array(data[:expected_len], dtype=np.int32).reshape(14, 8)

    # Transpose to get 8x14 matrix
    transposed = palm_matrix.T

    return transposed


def print_tactile_data(tactile_data: TactileData):
    """Print formatted tactile data from TactileData object."""
    if tactile_data is None:
        print("触觉数据为空")
        return

    print(f"时间戳: {tactile_data.timestamp}")

    # Print finger data
    fingers = [
        ("小拇指", tactile_data.pinky),
        ("无名指", tactile_data.ring),
        ("中指", tactile_data.middle),
        ("食指", tactile_data.index),
    ]

    for name, finger_data in fingers:
        if finger_data is not None:
            print(f"--- {name} ---")
            print(f"  Top (指端): {finger_data.top.shape}")
            print(f"  Tip (指尖): {finger_data.tip.shape}")
            print(f"  Base (指腹): {finger_data.base.shape}")

    # Print thumb data
    if tactile_data.thumb is not None:
        print(f"--- 大拇指 ---")
        print(f"  Top (指端): {tactile_data.thumb.top.shape}")
        print(f"  Tip (指尖): {tactile_data.thumb.tip.shape}")
        print(f"  Mid (指中): {tactile_data.thumb.mid.shape}")
        print(f"  Base (指腹): {tactile_data.thumb.base.shape}")

    # Print palm data
    if tactile_data.palm is not None and tactile_data.palm.size > 0:
        print(f"--- 掌心 ---")
        print(f"  Palm: {tactile_data.palm.shape}")


def save_tactile_data_to_jsonl(tactile_data: TactileData, file_path):
    """Save TactileData to JSONL format."""

    def convert_arrays_to_lists(data):
        if isinstance(data, np.ndarray):
            return data.tolist()
        elif hasattr(data, "__dict__"):
            return {
                key: convert_arrays_to_lists(value)
                for key, value in data.__dict__.items()
            }
        else:
            return data

    # Convert the tactile data to a JSON-serializable format
    json_data = convert_arrays_to_lists(tactile_data)

    # Append to JSONL file
    with open(file_path, "a", encoding="utf-8") as f:
        json.dump(json_data, f)
        f.write("\n")


def create_recording_directory():
    """Create a directory for recording data."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    recordings_dir = Path("recordings")
    recordings_dir.mkdir(exist_ok=True)
    session_dir = recordings_dir / f"session_{timestamp}"
    session_dir.mkdir(exist_ok=True)
    return session_dir


def save_data_to_jsonl(file_path, tactile_data: TactileData):
    """Save TactileData to a JSONL file with timestamp."""
    save_tactile_data_to_jsonl(tactile_data, file_path)


def read_multiple_registers(record=False, duration=5):
    client = ModbusTcpClient(MODBUS_IP, port=MODBUS_PORT)
    client.connect()

    # Setup recording if needed
    recording_dir = None
    data_file = None
    if record:
        recording_dir = create_recording_directory()
        data_file = recording_dir / "touch_data.jsonl"
        print(f"Recording data to {data_file}")

    print(f"Starting data collection for {duration} seconds...")
    collection_start_time = time.time()
    collection_count = 0

    try:
        while time.time() - collection_start_time < duration:
            start_time = time.time()

            # 读取各部分数据
            pinky_register_values = read_register_range(
                client, TOUCH_SENSOR_BASE_ADDR_PINKY, TOUCH_SENSOR_END_ADDR_PINKY
            )
            ring_register_values = read_register_range(
                client, TOUCH_SENSOR_BASE_ADDR_RING, TOUCH_SENSOR_END_ADDR_RING
            )
            middle_register_values = read_register_range(
                client, TOUCH_SENSOR_BASE_ADDR_MIDDLE, TOUCH_SENSOR_END_ADDR_MIDDLE
            )
            index_register_values = read_register_range(
                client, TOUCH_SENSOR_BASE_ADDR_INDEX, TOUCH_SENSOR_END_ADDR_INDEX
            )
            thumb_register_values = read_register_range(
                client, TOUCH_SENSOR_BASE_ADDR_THUMB, TOUCH_SENSOR_END_ADDR_THUMB
            )
            palm_register_values = read_register_range(
                client, TOUCH_SENSOR_BASE_ADDR_PALM, TOUCH_SENSOR_END_ADDR_PALM
            )

            end_time = time.time()
            frequency = (
                1 / (end_time - start_time) if end_time > start_time else float("inf")
            )

            # Format data into TactileData structure
            pinky_formatted = format_finger_data("小拇指", pinky_register_values)
            ring_formatted = format_finger_data("无名指", ring_register_values)
            middle_formatted = format_finger_data("中指", middle_register_values)
            index_formatted = format_finger_data("食指", index_register_values)
            thumb_formatted = format_thumb_data(thumb_register_values)
            palm_formatted = format_palm_data(palm_register_values)

            # Create TactileData object
            tactile_data = TactileData(
                timestamp=time.time(),
                pinky=pinky_formatted,
                ring=ring_formatted,
                middle=middle_formatted,
                index=index_formatted,
                thumb=thumb_formatted,
                palm=(
                    palm_formatted
                    if palm_formatted is not None
                    else np.array([], dtype=np.int32)
                ),
            )

            # Save data if recording
            if record and data_file:
                save_data_to_jsonl(data_file, tactile_data)

            # Print formatted data
            print_tactile_data(tactile_data)

            collection_count += 1
            print(f"读取频率：{frequency:.2f} Hz")
            print(f"Collection #{collection_count}")
            if record:
                print(f"Recording to {data_file}")
            print("\n" + "=" * 40 + "\n")

        end_time = time.time()
        total_time = end_time - collection_start_time
        print(f"Data collection completed!")
        print(f"Total collections: {collection_count}")
        print(f"Total time: {total_time:.2f} seconds")
        print(f"Average frequency: {collection_count/total_time:.2f} Hz")

    finally:
        client.close()


if __name__ == "__main__":
    read_multiple_registers(record=True)
