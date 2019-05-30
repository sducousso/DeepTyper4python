# astpretty --typed-3 t.py

import typed_ast.ast3 as ast3
import astpretty

astpretty.pprint(ast3.parse('x = 4  # type: int'))
