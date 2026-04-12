import io

stream = io.StringIO("Hallo\nWelt\n")

for line in stream:
    print(line.strip())
