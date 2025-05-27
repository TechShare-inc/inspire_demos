from abc import ABC, abstractmethod
import os
from typing import Any
import serial
import time
import asyncio

import logging

import serial.tools

if os.name == "posix":
    import serial.tools.list_ports_posix
elif os.name == "nt":
    import serial.tools.list_ports_windows
elif os.name == "linux":
    import serial.tools.list_ports_linux

regdict = {
    "ID": 1000,
    "baudrate": 1001,
    "clearErr": 1004,
    "forceClb": 1009,
    "angleSet": 1486,
    "forceSet": 1498,
    "speedSet": 1522,
    "angleAct": 1546,
    "forceAct": 1582,
    "errCode": 1606,
    "statusCode": 1612,
    "temp": 1618,
    "actionSeq": 2320,
    "actionRun": 2322,
}

DEFAULT_PORT = "COM3" if os.name == "nt" else "/dev/ttyUSB0"
DEFAULT_BAUDRATE = 115200

class InspireHandAPI:
    _logger = logging.getLogger(__name__)
    _ser: serial.Serial
    _port: str
    _baudrate: int

    def __init__(self, port: str = DEFAULT_PORT, baudrate: int = DEFAULT_BAUDRATE):
        self._port = port
        self._baudrate = baudrate

    def _validate_com_port(self):
        if os.name == "nt":
            self._logger.debug(f"Checking COM port {self._port} on Windows")
            ports = list(serial.tools.list_ports_windows.comports())
            if self._port not in [p.device for p in ports]:
                self._logger.error(f"Port {self._port} not found")
                return False
            else:
                return True
        elif os.name == "posix":
            self._logger.debug(f"Checking Linux port {self._port}")
            ports = list(serial.tools.list_ports_posix.comports())
            if self._port not in [p.device for p in ports]:
                self._logger.error(f"Port {self._port} not found")
                return False
            else:
                return True
        else:
            self._logger.error(f"Unsupported OS: {os.name}")
            return False

    def connect(self) -> bool:
        try:
            self._ser = serial.Serial(self._port, self._baudrate)
            self._ser.open()

        except Exception as e:
            self._logger.error(
                f"Failed to connect to {self._port} with baudrate {self._baudrate}: {e}"
            )
            return False
        return True

    def disconnect(self) -> bool:
        if self._ser:
            try:
                self._ser.close()
                return True
            except Exception as e:
                self._logger.error(f"Failed to disconnect from {self._ser.port}: {e}")
                return False
        return True

    def reset_error(self) -> bool:
        return self._write_register(1, regdict["clearErr"], 1, [0x01])

    def return_to_zero(self) -> bool:
        return self.set_angle([0, 0, 0, 0, 0, 0])

    def perform_open(self) -> bool:
        return self.set_angle([1000, 1000, 1000, 1000, 1000, 1000])

    def perform_close(self) -> bool:
        return self.set_angle([0, 0, 0, 0, 0, 0])

    def set_angle(self, angles: list[int], hand_id: int = 1) -> bool:
        val_reg = []
        for angle in angles:
            val_reg.append(angle & 0xFF)
            val_reg.append((angle >> 8) & 0xFF)

        self._write_register(hand_id, regdict["angleSet"], 12, val_reg)

        return True

    def set_pos(self, hand_id: int, positions: list[int]) -> bool:
        val_reg = []
        for pos in positions:
            val_reg.append(pos & 0xFF)
            val_reg.append((pos >> 8) & 0xFF)

        self._write_register(hand_id, regdict["angleSet"], 12, val_reg)

        return True

    def set_speed(self, hand_id: int, speeds: list[int]) -> bool:
        val_reg = []
        for speed in speeds:
            val_reg.append(speed & 0xFF)
            val_reg.append((speed >> 8) & 0xFF)

        self._write_register(hand_id, regdict["speedSet"], 12, val_reg)

        return True

    def set_force(self, hand_id: int, forces: list[int]) -> bool:
        val_reg = []
        for force in forces:
            val_reg.append(force & 0xFF)
            val_reg.append((force >> 8) & 0xFF)

        self._write_register(hand_id, regdict["forceSet"], 12, val_reg)

        return True

    def _write_register(self, id, addr, num, val) -> bool:
        bytes = [0xEB, 0x90]
        bytes.append(id)  # id
        bytes.append(num + 3)  # len
        bytes.append(0x12)  # cmd
        bytes.append(addr & 0xFF)
        bytes.append((addr >> 8) & 0xFF)  # add
        for i in range(num):
            bytes.append(val[i])
        checksum = 0x00
        for i in range(2, len(bytes)):
            checksum += bytes[i]
        checksum &= 0xFF
        bytes.append(checksum)
        self._ser.write(bytearray(bytes))

        while self._ser.in_waiting > 0:
            self._ser.read_all()  # 把返回帧读掉，不处理
            time.sleep(0.01)

        return True

    def _read_register(self, id, addr, num, verbose=False) -> list[int]:
        bytes = [0xEB, 0x90]
        bytes.append(id)  # id
        bytes.append(0x04)  # len
        bytes.append(0x11)  # cmd
        bytes.append(addr & 0xFF)
        bytes.append((addr >> 8) & 0xFF)  # add
        bytes.append(num)
        checksum = 0x00
        for i in range(2, len(bytes)):
            checksum += bytes[i]
        checksum &= 0xFF
        bytes.append(checksum)
        self._ser.write(bytearray(bytes))

        time.sleep(0.01)

        recv = self._ser.read_all()

        if recv is None or len(recv) == 0:
            return []
        num = (recv[3] & 0xFF) - 3
        val = []
        for i in range(num):
            val.append(recv[7 + i])

        if verbose:
            self._logger.debug(f"Read {num} values from {addr} for hand {id}")
            for i in range(num):
                self._logger.debug(f"Value {i}: {val[i]}")

        return val

    def _read6(self, id, str) -> list[int]:
        if str not in regdict:
            self._logger.warning(f"Incorrect command: {str}")
            return []
        length = 6
        # str == 'errCode' or str == 'statusCode' or str == 'temp':
        val_act = self._read_register(id, regdict[str], length, True)
        if val_act is None or len(val_act) < length:
            self._logger.warning(f"No data read from {str} for hand {id}")
            return []
        self._logger.debug(f"Read {length} values from {str} for hand {id}")
        for i in range(length):
            self._logger.debug(f"Value {i}: {val_act[i]}")

        return val_act

    def _read12(self, id, str) -> list[int]:
        if str not in regdict:
            self._logger.warning(f"Incorrect command: {str}")
            return []

        length = 12
        # if str == 'angleSet' or str == 'forceSet' or str == 'speedSet' or str == 'angleAct' or str == 'forceAct':
        val = self._read_register(id, regdict[str], length, True)
        if len(val) < length:
            self._logger.warning(f"No data read from {str} for hand {id}")
            return []
        val_act = []
        for i in range(length // 2):
            val_act.append((val[2 * i] & 0xFF) + (val[1 + 2 * i] << 8))
        self._logger.debug(f"Read {length} values from {str} for hand {id}")

        for i in range(length // 2):
            self._logger.debug(f"Value {i}: {val_act[i]}")

        return val_act

    # def set_wristangle(self, hand_id, yaw, pitch):
    #     val_reg = [
    #         (yaw - 2550) & 0xFF, ((yaw - 2550) >> 8) & 0xFF,
    #         (pitch - 2266) & 0xFF, ((pitch - 2266) >> 8) & 0xFF
    #     ]

    #     self.write_register(hand_id, regdict['angleSet'], 4, val_reg)

    # def getwristangleact(self, hand_id):
    # return self.read6(hand_id, 'angleAct')

    def getangleact(self, hand_id: int = 1) -> list[int]:
        return self._read12(hand_id, "angleAct")

    def getangleset(self, hand_id: int = 1) -> list[int]:
        return self._read12(hand_id, "angleSet")

    def getposact(self, hand_id: int = 1) -> list[int]:
        return self._read12(hand_id, "angleAct")

    def getposset(self, hand_id: int = 1) -> list[int]:
        return self._read12(hand_id, "angleSet")

    def getspeedset(self, hand_id: int = 1) -> list[int]:
        return self._read12(hand_id, "speedSet")

    def getforceact(self, hand_id: int = 1) -> list[int]:
        return self._read12(hand_id, "forceAct")

    def getforceset(self, hand_id: int = 1) -> list[int]:
        return self._read12(hand_id, "forceSet")

    def getcurrentact(self, hand_id: int = 1) -> list[int]:
        return self._read6(hand_id, "angleAct")

    def geterror(self, hand_id: int = 1) -> list[int]:
        return self._read6(hand_id, "errCode")

    def gettemp(self, hand_id: int = 1) -> list[int]:
        return self._read6(hand_id, "temp")

    def get_pos(self, hand_id: int = 1) -> list[int]:
        return self.getposact(hand_id)


if __name__ == "__main__":
    pass
