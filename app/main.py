import subprocess
import sys
import os
import shutil
import ctypes


CLONE_NEWPID = 0x20000000


def main():
    command = sys.argv[3]
    args = sys.argv[4:]

    # create tmp directory as /tmp/<path from command>
    tmp_dir_name = "/tmp"
    command_path = os.path.dirname(command)
    tmp_directory_path = os.path.join(tmp_dir_name, command_path[1:])

    os.makedirs(tmp_directory_path, exist_ok=True)

    # copy the executable to the tmp directory
    shutil.copy2(command, tmp_directory_path)
    os.chroot(tmp_dir_name)

    # crate new PID namespace
    libc = ctypes.cdll.LoadLibrary(None)
    libc.unshare(CLONE_NEWPID)

    completed_process = subprocess.run([command, *args], capture_output=True)
    if completed_process.stdout:
        print(completed_process.stdout.decode("utf-8"), file=sys.stdout, end="")
    else:
        print(completed_process.stderr.decode("utf-8"), file=sys.stderr, end="")

    sys.exit(completed_process.returncode)


if __name__ == "__main__":
    main()
