import sys
import re
import ast

class AddTransformer(ast.NodeTransformer):
    def visit_BinOp(self, node):
        self.generic_visit(node)
        if isinstance(node.op, ast.Add):
            return ast.Call(
                func=ast.Name(id='__add', ctx=ast.Load()),
                args=[node.left, node.right],
                keywords=[]
            )
        return node

def transform_add(py_expr):
    try:
        tree = ast.parse(py_expr, mode='eval')
        tree = AddTransformer().visit(tree)
        return ast.unparse(tree)
    except Exception as e:
        return py_expr

def transpile(source_code):
    lines = source_code.split('\n')
    py_lines = [
        "def __add(a, b):",
        "    if isinstance(a, str) or isinstance(b, str): return str(a) + str(b)",
        "    return a + b",
        "def __say(x): print(x)",
        "def __ask(prompt):",
        "    v = input(prompt)",
        "    if v.isdigit(): return int(v)",
        "    try: return float(v)",
        "    except: return v",
        ""
    ]
    
    indent = 0
    def emit(line):
        py_lines.append("    " * indent + line)

    for orig_line in lines:
        line = orig_line.strip()
        if not line:
            continue
            
        if line.endswith('.'):
            line = line[:-1]
        line = line.strip()
        line = line.replace(',', '')
        
        if line.startswith('note ') or line.startswith('remark '):
            emit('# ' + line)
            continue
            
        strings = []
        def repl_str(m):
            strings.append(m.group(0))
            return f"__STR{len(strings)-1}__"
        line = re.sub(r'".*?"', repl_str, line)
        
        line = line.replace(' divided by ', ' / ')
        line = line.replace(' times ', ' * ')
        line = line.replace(' plus ', ' + ')
        line = line.replace(' minus ', ' - ')
        line = line.replace(' modulo ', ' % ')
        
        line = line.replace(' is not ', ' != ')
        line = line.replace(' is greater than ', ' > ')
        line = line.replace(' is less than ', ' < ')
        line = line.replace(' is at least ', ' >= ')
        line = line.replace(' is at most ', ' <= ')
        line = line.replace(' equals ', ' == ')
        line = re.sub(r'\b is \b', ' == ', line)
        
        line = re.sub(r'\btrue\b', 'True', line)
        line = re.sub(r'\bfalse\b', 'False', line)
        line = re.sub(r'\ba new list\b', '[]', line)
        line = re.sub(r'\bas a number\b', '', line)
        line = re.sub(r'\bas text\b', '', line)
        line = re.sub(r'\bas a truth value\b', '', line)
        
        line = re.sub(r'\bthe size of\s+(.*?)\b', r'len(\1)', line)
        line = re.sub(r'\bitem\s+(.*?)\s+of\s+(.*?)\b', r'\2[int(\1)-1]', line)

        def process_expr(e):
            def repl_call(m):
                func = m.group(1).replace(' ', '_')
                args = m.group(2)
                if args:
                    args = [a.strip().replace(' ', '_') for a in args.split(' and ')]
                    return f"{func}({', '.join(args)})"
                return f"{func}()"
            e = re.sub(r'call\s+(.*?)(?:\s+with\s+(.*))?$', repl_call, e)

            e = re.sub(r'\band\b', ' __AND__ ', e)
            e = re.sub(r'\bor\b', ' __OR__ ', e)
            e = re.sub(r'\bnot\b', ' __NOT__ ', e)
            
            e = e.replace('&&', ' __AND__ ')
            e = e.replace('||', ' __OR__ ')
            e = re.sub(r'!(?!=)', ' __NOT__ ', e)
            
            while True:
                e_new = re.sub(r'(?<=[a-zA-Z])\s+(?=[a-zA-Z])', '_', e)
                if e_new == e: break
                e = e_new
                
            e = e.replace('__AND__', 'and')
            e = e.replace('__OR__', 'or')
            e = e.replace('__NOT__', 'not')
            
            for i, s in enumerate(strings):
                e = e.replace(f'__STR{i}__', s)
                
            return e

        let_match = re.match(r'^let\s+(.*?)\s+(?:be|=)\s+(.*)$', line)
        set_match = re.match(r'^set\s+(.*?)\s+(?:to|=)\s+(.*)$', line)
        if let_match:
            var = process_expr(let_match.group(1))
            val = transform_add(process_expr(let_match.group(2)))
            emit(f"{var} = {val}")
        elif set_match:
            var = process_expr(set_match.group(1))
            val = transform_add(process_expr(set_match.group(2)))
            emit(f"{var} = {val}")
        elif line.startswith('say '):
            val = transform_add(process_expr(line[4:]))
            emit(f"__say({val})")
        elif line.startswith('ask ') and ' and store it in ' in line:
            parts = line[4:].split(' and store it in ', 1)
            prompt = transform_add(process_expr(parts[0]))
            var = process_expr(parts[1])
            emit(f"{var} = __ask({prompt})")
        elif line.startswith('if '):
            cond = process_expr(line[3:])
            emit(f"if {cond}:")
            indent += 1
        elif line.startswith('else if '):
            cond = process_expr(line[8:])
            indent -= 1
            emit(f"elif {cond}:")
            indent += 1
        elif line == 'else':
            indent -= 1
            emit("else:")
            indent += 1
        elif line == 'end if':
            indent -= 1
        elif line.startswith('while '):
            cond = process_expr(line[6:])
            emit(f"while {cond}:")
            indent += 1
        elif line == 'end while':
            indent -= 1
        elif line.startswith('repeat ') and line.endswith(' times'):
            count = process_expr(line[7:-6])
            emit(f"for _ in range({count}):")
            indent += 1
        elif line == 'end repeat':
            indent -= 1
        elif line == 'break out' or line == 'stop':
            emit("break")
        elif line.startswith('define ') and ' accepting ' in line:
            parts = line[7:].split(' accepting ', 1)
            fname = process_expr(parts[0])
            args = [process_expr(a.strip()) for a in parts[1].split(' and ')]
            emit(f"def {fname}({', '.join(args)}):")
            indent += 1
        elif line == 'end define':
            indent -= 1
        elif line.startswith('return '):
            val = transform_add(process_expr(line[7:]))
            emit(f"return {val}")
        elif line.startswith('add ') and ' to ' in line:
            parts = line[4:].split(' to ', 1)
            item = transform_add(process_expr(parts[0]))
            lst = process_expr(parts[1])
            emit(f"{lst}.append({item})")
        elif line.startswith('remove ') and ' from ' in line:
            parts = line[7:].split(' from ', 1)
            item = transform_add(process_expr(parts[0]))
            lst = process_expr(parts[1])
            emit(f"{lst}.remove({item})")
        elif line == 'attempt':
            emit("try:")
            indent += 1
        elif line == 'if it fails':
            indent -= 1
            emit("except Exception:")
            indent += 1
        elif line == 'end attempt':
            indent -= 1
        else:
            val = transform_add(process_expr(line))
            emit(val)
            
    return "\n".join(py_lines)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python epp.py <file.epp>")
        sys.exit(1)
        
    with open(sys.argv[1], 'r') as f:
        source = f.read()
        
    py_code = transpile(source)
    out_file = sys.argv[1] + '.py'
    with open(out_file, 'w') as f:
        f.write(py_code)
        
    print(f"--- Running {sys.argv[1]} ---")
    namespace = {}
    exec(py_code, namespace)
