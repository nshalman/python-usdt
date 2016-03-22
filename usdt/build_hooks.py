import os
import platform
import subprocess

OS = platform.os.uname()[0]
ARCH = platform.architecture()[0]


def post_build():
    """Compile libusdt"""
    extra = ""
    if OS == "SunOS" and ARCH == "32bit":
        extra = "ARCH=i386"

    linker_flag = "--whole-archive"
    compiler = subprocess.check_output(["cc", "--version"])
    if b"clang" in compiler:
        linker_flag = "-force_load"

    libdir = os.getcwd() + "/build/lib/usdt/libusdt"
    source = libdir + "/libusdt.a"
    library = libdir + ".so"
    try:
        if os.system("cd %s ; make %s clean all" % (libdir, extra)) == 0:
            os.system("gcc -g -shared -o %s -Wl,%s %s" %
                      (library, linker_flag, source))
    except:
        pass
