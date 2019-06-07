"""
Usage:
    loadbarone.py [options] INPUT_CODE_DATA INPUT_DOCS_DATA OUT_FILE_PREFIX

Options:
    -h --help                  Show this screen.
    --debug                    Enable debug routines. [default: False]
    --task-type                The type of task to extract this. Either "func-doc" or "func-name". Defaults to "func-doc".
"""
from typed_ast.ast3 import parse
from collections import defaultdict
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
import ray

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


# Extracts function names


def decl_tokenizer(decl):
    function_name = re.search('(?<=def )[\w_-]+(?=\(.*\):)', decl).group(0)
    return splitter(function_name)


# Tokenize on spaces and around delimiters.
# Keep delimiters together only if it makes sense (e.g. parentheses, dots)
docstring_regex_tokenizer = re.compile(
    r"[^\s,'\"`.():\[\]=*;>{\}+-/\\]+|\\+|\.+|\(\)|{\}|\[\]|\(+|\)+|:+|\[+|\]+|{+|\}+|=+|\*+|;+|>+|\++|-+|/+")


def docstring_tokenize(docstr: str):
    return [t for t in docstring_regex_tokenizer.findall(docstr) if t is not None and len(t) > 0]


@ray.remote
def process_data(file_path):
    # Global calculs and formating
    m = Monitoring()
    m.file = file_path

    data, graph_node_labels = [], []
    inp = ""

    with open(file_path, encoding="ISO-8859-1") as f:
        # print(f_content)
        m.increment_count()
        m.treat_file(file_path)
        f_content = f.read()
        f_content = f_content.replace("    ", '\t')
        inp = f_content
        # print(f_content)

    try:

        visitor = AstGraphGenerator()
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
                # print("elem: ", elem)
                matches = [ann for ann in ann_types if ann[0] == node]
                # print("matches: ", matches)
                # if len(graph_node_labels) > 65:
                # print("65: ", graph_node_labels[65])
                if len(matches) > 0:
                    # print("matches: ", matches)
                    if len(matches) != 1:
                        graph_node_labels = [
                            g for g in graph_node_labels if g != matches[0]]
                        graph_node_labels.append(matches[0])
                    type_found.append(matches[0][1])
            if len(type_found) > 0:
                type_found = sorted(
                    type_found, key=type_found.count, reverse=True)
                # print("sorted types: ", type_found)
                ann_types.append([supernode[0], type_found[0]])

        # print(occurrences)
        # print(ann_types)

        if len(ann_types) == 0:
            m.empty_files.append(m.file)
            data = None
        else:
            data.append({"edges": edge_list,
                         #  "backbone_sequence": visitor.terminal_path,
                         "node_labels": graph_node_labels,
                         "annotation_type": ann_types})

        # passed += 1

    except Exception as e:
        m.found_error(e, traceback.format_exc())
        # print(e)
        # print(inp)
        # errors += 1
        # traceback.print_exc()

    return (data, m)


def explore_files(walk_dir):
    inp = []
    for root, subdirs, files in os.walk(walk_dir):
        print('--\nroot = ' + root)
        inp += ray.get([process_data.remote(f)
                        for f in [os.path.join(root, filename) for filename in files]])
        for subdir in subdirs:
            # print('\t- subdirectory ' + subdir)
            inp = inp + explore_files(subdir)

    # print('inp ret: ', inp)
    return inp


def main():
    # Get arguments from command line

    if len(sys.argv) < 2:
        print("missing repos master directory")
        exit(1)
    print("Exploring folders ...")
    walk_dir = sys.argv[1]
    monitoring = Monitoring()
    ray.init()
    outputs = explore_files(walk_dir)
    # print(outputs[1])
    # print(outputs[0][1].count)
    graphs = []
    for o in outputs:
        if o[0] is not None:
            graphs.append(o[0][0])
        monitoring.count += o[1].count
        monitoring.errors += o[1].errors
        monitoring.empty_files += o[1].empty_files

    # print(graphs)

    # Save results
    save_jsonl_gz("._graphs_p.jsonl.gz", graphs)

    print("Done.")
    print("Generated %d graphs out of %d snippets" %
          (monitoring.count - len(monitoring.errors), monitoring.count))
    pprint(monitoring.errors)

    with open('noAnnotations_p.txt', 'w') as f:
        for item in monitoring.empty_files:
            f.write("%s\n" % item)

    with open('logs_p.txt', 'w') as f:
        for item in monitoring.errors:
            f.write("%s\n" % item)


if __name__ == "__main__":
    main()
