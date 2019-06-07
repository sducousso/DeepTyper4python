"""
Usage:
    loadbarone.py [options] INPUT_CODE_DATA INPUT_DOCS_DATA OUT_FILE_PREFIX

Options:
    -h --help                  Show this screen.
    --debug                    Enable debug routines. [default: False]
    --task-type                The type of task to extract this. Either "func-doc" or "func-name". Defaults to "func-doc".
"""
# from ast import parse
from typed_ast.ast3 import parse
from collections import defaultdict
# from docopt import docopt
import re
import json

from utils import save_jsonl_gz
from gen import AstGraphGenerator

import traceback

import astpretty
import os
import sys
from split import groupby
from pprint import pprint

# Monitoring


class Monitoring:
    def __init__(self):
        self.count = 0
        self.errors = []
        self.file = ""
        self.empty_files = []

    def increment_count(self):
        self.count += 1

    def found_error(self, err, trace):
        self.errors.append([self.file, err, trace])

    def treat_file(self, filename):
        self.file = filename


# Save file
def save(data):
    with open('_graph.json', 'w') as f:
        json.dump(data, f)


def process_data(inputs, monitring):
    # Global calculs and formating

    data, graph_node_labels, docs_words = [], [], []
    data_ann = []
    # num_inits, errors = 0, 0
    # errors = 0
    # passed = 0

    for idx, inp in enumerate(inputs):
        try:
            # print("in inp: ", inp)
            # if idx % 100 == 0:
            #     print('%.1f %%    \r' %
            #           (idx / float(len(inputs)) * 100), end="")

            visitor = AstGraphGenerator()
            # astpretty.pprint(parse(inp, mode='exec'))
            visitor.visit(parse(inp, mode='exec'))

            edge_list = [(t, origin, destination)
                         for (origin, destination), edges
                         in visitor.graph.items() for t in edges]

            graph_node_labels = [label.strip() for (
                _, label) in sorted(visitor.node_label.items())]

            ann_types = visitor.annotation_types

            occurrences = [
                [edge[0], edge[1], edge[2]] for edge in edge_list if edge[0] == "occurrence_of"]
            occurrences = [[k, list(i)]
                           for k, i in groupby(lambda edge: edge[2], occurrences)]

            # Assign majority type for each supernode
            for supernode in occurrences:
                type_found = []
                for elem in supernode[1]:
                    node = elem[1]
                    matches = [ann for ann in ann_types if ann[0] == node]
                    if len(matches) > 0:
                        type_found.append(matches[0][1])
                if len(type_found) > 0:
                    type_found = sorted(
                        type_found, key=type_found.count, reverse=True)
                    ann_types.append([supernode[0], type_found[0]])

            supernodes = list(visitor.representations.values())

            vocab = [[k, v] for k, v in visitor.vocab.items()]
            print(vocab)

            # print(supernodes)
            # print(occurrences)
            # print(ann_types)

            if len(ann_types) == 0:
                monitring.empty_files.append(monitring.file)
                return None, None

            data.append({"edges": edge_list,
                         "backbone_sequence": visitor.terminal_path,
                         "supernodes": supernodes,
                         "node_labels": graph_node_labels,
                         "annotation_type": ann_types,
                         "vocabulary": vocab})
            data_ann.append(ann_types)
            # passed += 1

        except Exception as e:
            monitring.found_error(e, traceback.format_exc())
            # print(e)
            # print(inp)
            # errors += 1
            # traceback.print_exc()

    # print("Generated %d graphs out of %d snippets" %
        #   (len(inputs) - errors, len(inputs)))
    # print("Passed: ", passed)

    return data, data_ann


def explore_files(walk_dir, monitoring):
    inp = []
    ann = []
    for root, subdirs, files in os.walk(walk_dir):
        print('--\nroot = ' + root)
        for subdir in subdirs:
            # print('\t- subdirectory ' + subdir)
            inpt, annt = explore_files(subdir, monitoring)
            inp += inpt
            ann += annt
            # explore_files(subdir, monitoring)
            # print("ext: ", ext)
        for filename in files:
            file_path = os.path.join(root, filename)
            # print('\t- file %s (full path: %s)' % (filename, file_path))

            with open(file_path, encoding="ISO-8859-1") as f:
                # print(f_content)
                monitoring.increment_count()
                monitoring.treat_file(file_path)
                f_content = f.read()
                f_content = f_content.replace("    ", '\t')
                # print(f_content)
                graph, ann_graph = process_data([f_content], monitoring)
                if graph is not None and graph != []:
                    # print(graph[0])
                    # save_jsonl_gz("._graphs.jsonl.gz", graph)
                    # save(graph)
                    inp.append(graph[0])
                    ann.append(ann_graph[0])

    # print('inp ret: ', inp)
    return inp, ann


def main():
    # Get arguments from command line

    if len(sys.argv) < 2:
        print("missing repos master directory")
        exit(1)
    print("Exploring folders ...")
    walk_dir = sys.argv[1]
    monitoring = Monitoring()
    outputs, outputs_ann = explore_files(walk_dir, monitoring)
    # explore_files(walk_dir, monitoring)

    # print(inputs)
    # inputs = ['y: int = 0\nif x == 0:\n\tprint("hello")\n',
    #           'def slice(string: str, start: int, end: int) -> str:\n\treturn string[start:end]\n']
    #   inputs = ['x:int = 0 \nif x == 0: \n\tprint("hello")\n',
    #   'def slice (string: str, start: int, end: int) -> str: \n\treturn string[start:end]']

    # print("inputs: ", inputs)
    # print("Start processing inputs.")
    # graphs = process_data(inputs)

    # Save results
    save_jsonl_gz("._graphs_mock.jsonl.gz", outputs)

    # Labels for int=1, other=0
    for line in range(len(outputs_ann)):
        for ann in range(len(outputs_ann[line])):
            outputs_ann[line][ann][1] = 1 if outputs_ann[line][ann][1] == "int" else 0

    save_jsonl_gz("._graphs_mock_labels.jsonl.gz", outputs_ann)
    # save_jsonl_gz(args['OUT_FILE_PREFIX'] + "_summary.jsonl.gz", docs)

    print("Done.")
    print("Generated %d graphs out of %d snippets" %
          (monitoring.count - len(monitoring.errors), monitoring.count))
    pprint(monitoring.errors)

    # with open('noAnnotations_mock.txt', 'w') as f:
    #     for item in monitoring.empty_files:
    #         f.write("%s\n" % item)

    # with open('logs_mock.txt', 'w') as f:
    #     for item in monitoring.errors:
    #         f.write("%s\n" % item)


if __name__ == "__main__":
    main()
