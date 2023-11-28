import subprocess
import sys


def main(): 
    command = sys.argv[3]
    args = sys.argv[4:]
    completed_process = subprocess.run([command, *args], capture_output=True)
    print(completed_process.stdout.decode("utf-8"))
    process = subprocess.Popen(
        [command, *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = process.communicate()
    
    print(stdout.decode("utf-8"), end="")
    print(stderr.decode("utf-8"), file=sys.stderr, end="")


if __name__ == "__main__":
    main()
