import astpretty
# import ast
import typed_ast.ast3 as ast3
import sys

'''
Display each node name and value
Take file name in command line argument
'''


def print_node_value(node, str):
    for f in ast3.iter_fields(node):
        print(str)
        print(f)


def visit(node, handle_node, str):
    handle_node(node, str)
    str = str + "-"
    for child in ast3.iter_child_nodes(node):
        visit(child, handle_node, str)


def main():
    str = ""
    if len(sys.argv) == 1:
        print("Expected file to parse in argument")
        exit()

    with open(sys.argv[1], "r") as source:
        tree = ast3.parse(source.read())
        visit(tree, print_node_value, str)


main()
