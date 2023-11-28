import subprocess
import sys
import os


def main(): 
    command = sys.argv[3]
    args = sys.argv[4:]

    completed_process = subprocess.run([command, *args], capture_output=True)
    if completed_process.stdout:
        print(completed_process.stdout.decode("utf-8"), file=sys.stdout, end="")
    else:
        print(completed_process.stderr.decode("utf-8"), file=sys.stderr, end="")
    
    sys.exit(completed_process.returncode)


if __name__ == "__main__":
    main()
