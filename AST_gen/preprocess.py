import sys

if len(sys.argv) < 2:
    print("missing file to parse")
    exit(1)

with open(sys.argv[1]) as f:
    inputs = f.read()
    # inputs = "".join(line.rstrip() for line in f)
    inputs = inputs.replace("\n", " DCNL ").replace(
        "\t", " DCSP ").replace("    ", "  DCSP")
print(inputs)
