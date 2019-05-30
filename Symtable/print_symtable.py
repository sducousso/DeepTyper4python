import symtable
import sys


def describe_symtable(st, recursive=True, indent=0):
    def print_d(s, *args):
        prefix = ' ' * indent
        print(prefix + s, *args)

    assert isinstance(st, symtable.SymbolTable)
    print_d('Symtable: type=%s, id=%s, name=%s' % (
        st.get_type(), st.get_id(), st.get_name()))
    print_d('  nested:', st.is_nested())
    print_d('  has children:', st.has_children())
    print_d('  identifiers:', list(st.get_identifiers()))
    print_d('  globals:', list(st.get_globals()))
    print_d('  locals:', list(st.get_locals()))
    print_d('  frees:', list(st.get_frees()))
    for ident in list(st.get_identifiers()):
        print_d('   name: ', ident)
        # print_d('   entry:', symtable.SymbolTable.lookup(
        # ident.SymbolTable.get_name()))

    if recursive:
        for child_st in st.get_children():
            describe_symtable(child_st, recursive, indent + 5)


code = """def slice(s, start, end):
	return s[start:end] """

if __name__ == "__main__":

    describe_symtable(symtable.symtable(code, "basic_python.py", "exec"))
