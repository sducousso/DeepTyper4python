import sys
import os
import json
import re

"""
Preprocess data such as node labels are split for camel case and snake case to a list of subtokens
"""


def main():
    if len(sys.argv) < 3:
        print("uasge: python3 preprocessing.py input_data_file output_data_file")
        exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    if os.path.exists(output_file):
        os.remove(output_file)

    with open(input_file, "r") as inf:
        with open(output_file, "a") as ouf:
            for line in inf:
                j_content = json.loads(line)
                for idx, node in enumerate(j_content["node_labels"], 0):
                    # print(node)
                    subtokens = node.split('_')
                    sub = []
                    for su in subtokens:
                        sub += re.sub('([A-Z][a-z]+)', r' \1',
                                      re.sub('([A-Z]+)', r' \1', su)).split()
                    # print(sub)
                    j_content["node_labels"][idx] = sub
                # print(j_content["node_labels"])
                json.dump(j_content, ouf)


if __name__ == "__main__":
    main()
