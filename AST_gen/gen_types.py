import typed_ast


def t_subscript(node):
    assert hasattr(node, 'value')
    assert hasattr(node, 'slice')
    v = t_master(node.value)
    s = t_master(node.slice)
    assert v is not None
    if s is None:
        s = 'None'
    return v + '[' + s + ']'


def t_tuple(node):
    assert hasattr(node, 'elts')
    e1 = t_master(node.elts[0])
    e2 = t_master(node.elts[1])
    if e1 is None:
        e1 = 'None'
    if e2 is None:
        e2 = 'None'
    # print("elts 0: ", e1)
    # print("elts 1: ", e2)
    return '(' + e1 + ', ' + e2 + ')'


def t_name(node):
    assert hasattr(node, 'id')
    return node.id


def t_list(node):
    assert hasattr(node, 'elts')
    t = '['
    for e in node.elts:
        t += t_master(e) + ', '
    t = t[:-2]  # to delete last ", "
    t += ']'
    return t


def t_attribute(node):
    assert hasattr(node, 'value')
    assert hasattr(node, 'attr')
    return t_master(node.value) + '.' + node.attr


def t_str(node):
    assert hasattr(node, 's')
    return node.s


def t_index(node):
    assert hasattr(node, 'value')
    return t_master(node.value)


def t_ellipsis(node):
    return 'Any'


def t_name_constante(node):
    assert hasattr(node, 'value')
    if node.value is None:
        return 'None'
    return node.value


def t_num(node):
    assert hasattr(node, 'n')
    return node.n


def t_master(node):
    if type(node) == typed_ast._ast3.Subscript:
        return t_subscript(node)
    elif type(node) == typed_ast._ast3.Tuple:
        return t_tuple(node)
    elif type(node) == typed_ast._ast3.Name:
        return t_name(node)
    elif type(node) == typed_ast._ast3.List:
        return t_list(node)
    elif type(node) == typed_ast._ast3.Attribute:
        return t_attribute(node)
    elif type(node) == typed_ast._ast3.Str:
        return t_str(node)
    elif type(node) == typed_ast._ast3.Index:
        return t_index(node)
    elif type(node) == typed_ast._ast3.Ellipsis:
        return t_ellipsis(node)
    elif type(node) == typed_ast._ast3.NameConstant:
        return t_name_constante(node)
    elif type(node) == typed_ast._ast3.Num:
        return t_num(node)
    else:
        print(
            "\n\n\n ===========================\n  master type ", type(node), "\n ==============================\n\n\n")
#BoolOp, Call, Slice, ExtSlice


#"Callable[(], AbstractResource)]"
