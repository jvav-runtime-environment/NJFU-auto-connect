"""负责确保只有一个进程"""

import ctypes

kernel32 = ctypes.windll.kernel32


def can_create():
    """检查是否已经有一个实例在运行"""
    mutex = kernel32.CreateMutexA(None, False, "NJFU-auto-connect".encode("utf-8"))

    if not mutex or kernel32.GetLastError() == 183:
        return False
    return True
