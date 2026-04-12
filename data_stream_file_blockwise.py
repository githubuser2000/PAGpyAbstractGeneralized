with open("data.bin", "rb") as f:
    while chunk := f.read(1024):
        print(chunk)
