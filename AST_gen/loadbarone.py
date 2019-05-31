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


def process_data(inputs):
    # Global calculs and formating

    data, graph_node_labels, docs_words = [], [], []
    # num_inits, errors = 0, 0
    errors = 0
    doc_tokenizer = docstring_tokenize

    for idx, inp in enumerate(inputs):
        # print("in inp: ", inp)
        try:
            if idx % 100 == 0:
                print('%.1f %%    \r' %
                      (idx / float(len(inputs)) * 100), end="")

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
                index_occurrence = 1
                i = 0
                for elem in supernode[1]:
                    node = elem[1]
                    matches = [ann for ann in ann_types if ann[0] == node]
                    print("matches: ", matches)
                    if len(matches) > 0:
                        assert len(matches) == 1
                        type_found.append(matches[0][1])
                if len(type_found) > 0:
                    type_found = sorted(
                        type_found, key=type_found.count, reverse=True)
                    print("sorted types: ", type_found)
                    ann_types.append([supernode[0], type_found[0]])

            print(occurrences)
            print(ann_types)

            data.append({"edges": edge_list,
                         "backbone_sequence": visitor.terminal_path,
                         "node_labels": graph_node_labels,
                         "annotation_type": ann_types})

        except Exception as e:
            print(e)
            print(inp)
            errors += 1
            traceback.print_exc()

    print("Generated %d graphs out of %d snippets" %
          (len(inputs) - errors, len(inputs)))

    return data


def explore_files(walk_dir):
    inp = []
    for root, subdirs, files in os.walk(walk_dir):
        # print('--\nroot = ' + root)

        for subdir in subdirs:
            # print('\t- subdirectory ' + subdir)
            inp = inp + explore_files(subdir)
            # print("ext: ", ext)
        for filename in files:
            file_path = os.path.join(root, filename)
            # print('\t- file %s (full path: %s)' % (filename, file_path))

            with open(file_path, encoding="ISO-8859-1") as f:
                # print(f_content)
                f_content = f.read()
                f_content = f_content.replace("    ", '\t')
                inp.append(f_content)

    # print('inp ret: ', inp)
    return inp


def main():
    # Get arguments from command line

    if len(sys.argv) < 2:
        print("missing repos master directory")
        exit(1)
    print("Exploring folders ...")
    walk_dir = sys.argv[1]
    inputs = explore_files(walk_dir)

    # print(inputs)
    # inputs = ['y: int = 0\nif x == 0:\n\tprint("hello")\n',
    #           'def slice(string: str, start: int, end: int) -> str:\n\treturn string[start:end]\n']
    #   inputs = ['x:int = 0 \nif x == 0: \n\tprint("hello")\n',
    #   'def slice (string: str, start: int, end: int) -> str: \n\treturn string[start:end]']

    # print("inputs: ", inputs)
    print("Start processing inputs.")
    graphs = process_data(inputs)

    # Save results
    save_jsonl_gz("._graphs.jsonl.gz", graphs)
    # save_jsonl_gz(args['OUT_FILE_PREFIX'] + "_summary.jsonl.gz", docs)


if __name__ == "__main__":
    main()
