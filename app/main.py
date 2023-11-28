import subprocess
import sys


def main(): 
    print("Logs from your program will appear here!")
    completed_process = subprocess.run([command, *args], capture_output=True)
    print(completed_process.stdout.decode("utf-8"))


if __name__ == "__main__":
    main()
