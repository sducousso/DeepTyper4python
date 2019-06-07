import sys
import os
import json
import re

"""
Preprocess data such as node labels are split for camel case and snake case to a list of subtokens
"""


def subtokenizer(token):
    subtokens = token.split('_')
    res = []
    for su in subtokens:
        res += re.sub('([A-Z][a-z]+)', r' \1',
                      re.sub('([A-Z]+)', r' \1', su)).split()
    return res


if __name__ == "__main__":
    subtokenizer("")
