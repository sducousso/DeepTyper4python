import graphviz
import json
from os.path import abspath, dirname, isfile, isdir
import sys


def plot(graph):
    dot = graphviz.Digraph(
        comment="Augmented AST of a Python snippet", node_attr={"shape": "plaintext"}
    )

    for idx, node_label in enumerate(graph["node_labels"]):
        dot.node(str(idx), node_label)

    colours = {
        "NextToken": "black",
        "child": "green",
        "last_lexical": "pink",
        "last_use": "blue",
        "last_write": "red",
        "computed_from": "purple",
        "return_to": "brown",
        "occurrence_of": "yellow",
    }

    for edge in graph["edges"]:
        edge_label = edge[0]
        dot.edge(
            str(edge[1]),
            str(edge[2]),
            label=edge_label,
            color=colours[edge_label],
            labelfontsize="8.0",
        )

    opath = abspath(sys.argv[2])
    assert isdir(dirname(opath)), "output base directory doesn't exist"
    dot.render(opath, view=True)
    # dot.render(opath)


def main():
    assert len(sys.argv) == 3, "Usage: <path to input json> <path to output pdf>"
    ipath = sys.argv[1]
    assert isfile(ipath), "input isn't a file"

    with open(ipath, encoding="utf8") as f:
        plot(json.load(f))


if __name__ == "__main__":
    main()
