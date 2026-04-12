import subprocess

proc = subprocess.Popen(
    ["python", "-c", "for i in range(5): print(i)"],
    stdout=subprocess.PIPE,
    text=True
)

for line in proc.stdout:
    print("Empfangen:", line.strip()import subprocess

proc = subprocess.Popen(
    ["python", "-c", "for i in range(5): print(i)"],
    stdout=subprocess.PIPE,
    text=True
)

for line in proc.stdout:
    print("Empfangen:", line.strip()))
