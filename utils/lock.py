"""负责确保只有一个进程"""

import ctypes

kernel32 = ctypes.windll.kernel32


def can_create():
    mutex = kernel32.CreateMutexA(None, False, "NJFU-auto-connect".encode("utf-8"))

    if mutex == 0:
        return False

    if ctypes.GetLastError() == 183:
        return False
    else:
        return True
