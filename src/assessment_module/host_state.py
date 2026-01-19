import platform
import ctypes

def get_host_state():
    state = {}

    state['aslr_level'] = get_aslr_sys()

    state['os'] = platform.system()
    state['kernel'] = platform.release()

    state['glibc'] = get_glibc_version()

    return state

def get_aslr_sys():
        try:
            with open("/proc/sys/kernel/randomize_va_space", "r") as f:
                aslr_val = f.read().strip()
                return int(aslr_val)
                #0 = Off, 1= Conservative, 2 = Full
        except FileNotFoundError:
            return None

def get_glibc_version():
        try:
            libc = ctypes.CDLL("libc.so.6")
            
            libc.gnu_get_libc_version.restype = ctypes.c_char_p
            version_bytes = libc.gnu_get_libc_version()
            
            return version_bytes.decode('utf-8')
        except Exception as e:
            return "Unknown"