import base64
import os


def convert2base64(filename):
    with open(f"data/{filename}", 'rb') as file:
        file_content = file.read()

    base64_one = base64.b64encode(file_content)    
    out_file = filename.split(".")[0]
    with open(f"data/{out_file}.b64", 'wb') as out_file:
        out_file.write(base64_one)



for item in os.listdir("data"):
    convert2base64(item)



