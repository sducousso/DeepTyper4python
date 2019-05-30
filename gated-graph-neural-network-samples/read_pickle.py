import sys
import pickle

if len(sys.argv) == 1:
        print("Expected pickle file to parse in argument")
        exit()

objects = []
with (open(sys.argv[1], "rb")) as openfile:
    while True:
        try:
            objects.append(pickle.load(openfile))
        except EOFError:
            break
print(objects)