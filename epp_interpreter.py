import sys
import re
import traceback
import ast

class AddTransformer(ast.NodeTransformer):
    def visit_BinOp(self, node):
        self.generic_visit(node)
        if isinstance(node.op, ast.Add):
            return ast.Call(
                func=ast.Name(id='__add__', ctx=ast.Load()),
                args=[node.left, node.right],
                keywords=[]
            )
        return node

def transform_ast_code(py_code):
    try:
        tree = ast.parse(py_code)
        tree = AddTransformer().visit(tree)
        return ast.unparse(tree)
    except Exception as e:
        return py_code

KEYWORDS = [
    'call square root of', 'call round', 'call absolute of', 'call length of', 
    'call uppercase of', 'call lowercase of', 'call sort list', 'call reverse list',
    'joined with', 'list of', 'size of', 'item', 'of', 'call', 'with', 'record', 
    'true', 'false', 'and', 'or', 'not'
]
KEYWORDS_PATT = '|'.join(r'\b' + k.replace(' ', r'\s+') + r'\b' for k in sorted(KEYWORDS, key=len, reverse=True))

def process_expr(expr_str, known_records):
    # Pre-process pseudo code CALL func(args) -> func(args) before tokenization
    expr_str = re.sub(r'(?i)\bCALL\s+(\w+)\s*\(', r'\1(', expr_str)
    expr_str = re.sub(r'(?i)check if\s+(.*?)\s+is a number', r'isinstance(\1, (int, float))', expr_str)
    expr_str = re.sub(r'(?i)check if\s+(.*?)\s+is a string', r'isinstance(\1, str)', expr_str)
    expr_str = re.sub(r'(?i)check if\s+(.*?)\s+is a boolean', r'isinstance(\1, bool)', expr_str)
    expr_str = re.sub(r'(?i)check if\s+(.*?)\s+is a list', r'isinstance(\1, list)', expr_str)
    expr_str = expr_str.strip()
    if not expr_str: return ""
    tokens = []
    regex = r'(".*?"|\d+(?:\.\d+)?|==|!=|<=|>=|<|>|=|\+|-|\*|/|%|,|\[|\]|\(|\)|' + KEYWORDS_PATT + r'|[A-Za-z_][A-Za-z0-9_]*|\s+)'
    
    for match in re.finditer(regex, expr_str, re.IGNORECASE):
        val = match.group(0)
        if not val.strip(): continue
        
        lower_val = val.lower()
        if val.startswith('"'): typ = 'STRING'
        elif val[0].isdigit(): typ = 'NUMBER'
        elif val in ('==','!=','<=','>=','<','>','=','+','-','*','/','%',',','[',']','(',')'): typ = 'OP'
        elif lower_val in KEYWORDS: 
            typ = 'KEYWORD'
            val = lower_val
        else: typ = 'WORD'
        tokens.append((typ, val))
        
    merged = []
    for t in tokens:
        if t[0] == 'WORD' and merged and merged[-1][0] == 'WORD':
            merged[-1] = ('WORD', merged[-1][1] + '_' + t[1])
        else:
            merged.append(t)
            
    out_tokens = []
    closers = []
    i = 0
    while i < len(merged):
        typ, val = merged[i]
        
        if typ == 'KEYWORD':
            if val == 'true': out_tokens.append('True')
            elif val == 'false': out_tokens.append('False')
            elif val == 'joined with': 
                out_tokens.append('+')
            elif val == 'record': out_tokens.append('__Record__()')
            elif val == 'list of':
                out_tokens.append('[')
                closers.append(']')
            elif val == 'size of':
                out_tokens.append('len(')
                closers.append(')')
            elif val == 'call square root of': out_tokens.append('math.sqrt('); closers.append(')')
            elif val == 'call round': out_tokens.append('round('); closers.append(')')
            elif val == 'call absolute of': out_tokens.append('abs('); closers.append(')')
            elif val == 'call length of': out_tokens.append('len('); closers.append(')')
            elif val == 'call uppercase of': out_tokens.append('str('); closers.append(').upper()')
            elif val == 'call lowercase of': out_tokens.append('str('); closers.append(').lower()')
            elif val == 'call sort list': out_tokens.append('sorted('); closers.append(')')
            elif val == 'call reverse list': out_tokens.append('list(reversed('); closers.append('))')
            elif val == 'call':
                if i + 1 < len(merged):
                    func = merged[i+1][1]
                    i += 1
                    if i + 1 < len(merged) and merged[i+1][1] == 'with':
                        out_tokens.append(f"{func}(")
                        closers.append(')')
                        i += 1
                    else:
                        out_tokens.append(f"{func}()")
                else:
                    out_tokens.append("call")
            elif val == 'item':
                out_tokens.append('__item__(')
                closers.append(')')
            elif val == 'of':
                out_tokens.append(',')
            elif val == 'with':
                out_tokens.append(',')
            elif val == 'and': out_tokens.append('and')
            elif val == 'or': out_tokens.append('or')
            elif val == 'not': out_tokens.append('not')
        elif typ == 'OP' and val == '=':
            out_tokens.append('==')
        else:
            out_tokens.append(val)
        i += 1
        
    out_tokens.extend(reversed(closers))
    res = " ".join(out_tokens)
    
    for rec in known_records:
        res = re.sub(rf'\b{rec}_([a-zA-Z_]+)\b', rf'{rec}.\1', res)
        
    return res

def parse_epp(source_code, known_records=None, is_repl=False):
    if known_records is None: known_records = set()
    py_lines = []
    if not is_repl:
        py_lines = [
            "import math",
            "import sys",
            "import operator",
            "import os",
            "from epp_ui import epp_create_window, epp_set_window_html, epp_load_file_in_window, epp_load_url_in_window, epp_show_windows, epp_fetch_page, epp_read_html_text, epp_read_html_file",
        "def __add__(a, b):",
        "    if isinstance(a, str) or isinstance(b, str): return ''.join([str(a), str(b)])",
        "    return operator.add(a, b)",
        "def __ask__(prompt):",
        "    try:",
        "        val = input(prompt + ' ')",
        "        if val.isdigit(): return int(val)",
        "        try: return float(val)",
        "        except: return val",
        "    except EOFError:",
        "        return ''",
        "def __item__(idx, lst): return lst[int(idx) - 1]",
        "class __Record__:",
        "    def __init__(self):",
        "        self.__dict__ = {}",
        "    def __getattr__(self, name): return None",
        "    def __setattr__(self, name, value): self.__dict__[name] = value",
        "    def __str__(self): return str(self.__dict__)",
        "    def __repr__(self): return str(self.__dict__)",
        ""
    ]
    
    lines = source_code.split('\n')
    indent = 0
    line_map = {}
    
    in_program = False
    in_text_block = False
    text_block_var = None
    
    def emit(code, orig_line_idx):
        py_lines.append("    " * indent + code)
        line_map[len(py_lines)] = orig_line_idx + 1

    for orig_idx, orig_line in enumerate(lines):
        line = orig_line.strip()
        
        if in_text_block:
            if line.lower() == 'end text.' or line.lower() == 'end text':
                in_text_block = False
                continue
            safe_line = repr(orig_line + '\n')
            emit(f"{text_block_var} += {safe_line}", orig_idx)
            continue

        if not line: continue
        
        if line.endswith('.'): line = line[:-1]
        line = line.strip()
        lower_line = line.lower()

        m = re.match(r'(?i)^set\s+(.*?)\s+(?:to|=)\s+text block$', line)
        if m:
            var = process_expr(m.group(1), known_records)
            emit(f"{var} = ''", orig_idx)
            in_text_block = True
            text_block_var = var
            continue
            
        m = re.match(r'(?i)^write\s+(.*?)\s+to file\s+(.*)$', line)
        if m:
            content = process_expr(m.group(1), known_records)
            filename = process_expr(m.group(2), known_records)
            emit(f"with open({filename}, 'w') as __f__:", orig_idx)
            emit(f"    __f__.write(str({content}))", orig_idx)
            continue

        m = re.match(r'(?i)^read file\s+(.*?)\s+into\s+(.*)$', line)
        if m:
            filename = process_expr(m.group(1), known_records)
            var = process_expr(m.group(2), known_records)
            emit(f"with open({filename}, 'r') as __f__:", orig_idx)
            emit(f"    {var} = __f__.read()", orig_idx)
            continue
        
        if lower_line == 'start program':
            emit('def __main__():', orig_idx)
            indent += 1
            in_program = True
            continue
        if lower_line == 'end program':
            indent -= 1
            emit('__main__()', orig_idx)
            in_program = False
            continue
            
        if lower_line.startswith('note:'):
            emit(f"# {line}", orig_idx)
            continue
        
        # ── Pseudo code: // single-line comment ──
        if line.startswith('//'):
            emit(f"# {line[2:].strip()}", orig_idx)
            continue
            
        # ── UI: set window content of "X" to "...". (must be before generic set) ──
        m = re.match(r'(?i)^set window content of\s+(.*?)\s+to\s+(.*)$', line)
        if m:
            title = process_expr(m.group(1), known_records)
            html = process_expr(m.group(2), known_records)
            emit(f"epp_set_window_html({title}, {html})", orig_idx)
            continue

        m = re.match(r'(?i)^set\s+(.*?)\s+(?:to|=)\s+(.*)$', line)
        if m:
            var = process_expr(m.group(1), known_records)
            if m.group(2).lower() == 'record':
                known_records.add(var)
                emit(f"{var} = __Record__()", orig_idx)
                continue
            val = process_expr(m.group(2), known_records)
            emit(f"{var} = {val}", orig_idx)
            continue
            
        if lower_line == 'end record':
            continue
            
        m = re.match(r'(?i)^say\s+(.*)$', line)
        if m:
            val = process_expr(m.group(1), known_records)
            emit(f"print({val})", orig_idx)
            continue
            
        m = re.match(r'(?i)^ask\s+(.*?)\s+and store in\s+(.*)$', line)
        if m:
            prompt = process_expr(m.group(1), known_records)
            var = process_expr(m.group(2), known_records)
            emit(f"{var} = __ask__({prompt})", orig_idx)
            continue
            
        m = re.match(r'(?i)^if\s+(.*?)\s+then$', line)
        if m:
            cond = process_expr(m.group(1), known_records)
            emit(f"if {cond}:", orig_idx)
            indent += 1
            continue
            
        m = re.match(r'(?i)^(?:otherwise if|else\s*if|elseif|elif)\s+(.*?)\s+then$', line)
        if m:
            cond = process_expr(m.group(1), known_records)
            indent -= 1
            emit(f"elif {cond}:", orig_idx)
            indent += 1
            continue

        # ── Pseudo: ELSEIF / ELIF condition (no THEN) ──
        m = re.match(r'(?i)^(?:otherwise if|else\s*if|elseif|elif)\s+(.+)$', line)
        if m:
            cond = process_expr(m.group(1), known_records)
            indent -= 1
            emit(f"elif {cond}:", orig_idx)
            indent += 1
            continue
            
        if lower_line in ('otherwise', 'else'):
            indent -= 1
            emit("else:", orig_idx)
            indent += 1
            continue
            
        if lower_line in ('end if', 'endif'):
            indent -= 1
            continue
            
        m = re.match(r'(?i)^repeat\s+(.*?)\s+times$', line)
        if m:
            count = process_expr(m.group(1), known_records)
            emit(f"for __i__ in range(int({count})):", orig_idx)
            indent += 1
            continue
            
        if lower_line == 'end repeat':
            indent -= 1
            continue
            
        # Handle both E++ "while cond." and pseudo code "WHILE cond DO."
        m = re.match(r'(?i)^while\s+(.*?)\s+do$', line)
        if not m:
            m = re.match(r'(?i)^while\s+(.*)$', line)
        if m:
            cond = process_expr(m.group(1), known_records)
            emit(f"while {cond}:", orig_idx)
            indent += 1
            continue
            
        if lower_line in ('end while', 'endwhile'):
            indent -= 1
            continue
            
        m = re.match(r'(?i)^for each\s+(.*?)\s+in\s+(.*)$', line)
        if m:
            item = process_expr(m.group(1), known_records)
            lst = process_expr(m.group(2), known_records)
            emit(f"for {item} in {lst}:", orig_idx)
            indent += 1
            continue
            
        if lower_line in ('end for', 'endfor', 'next'):
            indent -= 1
            continue
            
        if lower_line == 'stop loop':
            emit("break", orig_idx)
            continue
            
        if lower_line == 'skip loop':
            emit("continue", orig_idx)
            continue
            
        m = re.match(r'(?i)^define\s+(.*?)\s+with\s+(.*)$', line)
        if m:
            fname = process_expr(m.group(1), known_records)
            args = process_expr(m.group(2), known_records)
            emit(f"def {fname}({args}):", orig_idx)
            indent += 1
            continue
            
        m = re.match(r'(?i)^define\s+(.*)$', line)
        if m:
            fname = process_expr(m.group(1), known_records)
            emit(f"def {fname}():", orig_idx)
            indent += 1
            continue
            
        m = re.match(r'(?i)^give back\s+(.*)$', line)
        if m:
            val = process_expr(m.group(1), known_records)
            if not val.strip(): val = "None"
            emit(f"return {val}", orig_idx)
            continue
            
        if lower_line in ('end define', 'end function', 'endfunction',
                          'end procedure', 'endprocedure',
                          'end algorithm', 'endalgorithm'):
            indent -= 1
            continue
            
        m = re.match(r'(?i)^add\s+(.*?)\s+to\s+(.*)$', line)
        if m:
            item = process_expr(m.group(1), known_records)
            lst = process_expr(m.group(2), known_records)
            emit(f"{lst}.append({item})", orig_idx)
            continue
            
        m = re.match(r'(?i)^remove\s+(.*?)\s+from\s+(.*)$', line)
        if m:
            item = process_expr(m.group(1), known_records)
            lst = process_expr(m.group(2), known_records)
            emit(f"{lst}.remove({item})", orig_idx)
            continue
            
        if lower_line == 'try':
            emit("try:", orig_idx)
            indent += 1
            continue
            
        if lower_line == 'on error':
            indent -= 1
            emit("except Exception as __e__:", orig_idx)
            indent += 1
            continue
            
        if lower_line == 'end try':
            indent -= 1
            continue
            
        m = re.match(r'(?i)^bring in\s+(.*)$', line)
        if m:
            mod = process_expr(m.group(1), known_records)
            emit(f"import {mod}", orig_idx)
            continue
            
        m = re.match(r'(?i)^call\s+(.*?)\s+with\s+(.*)$', line)
        if m:
            fname = process_expr(m.group(1), known_records)
            args = process_expr(m.group(2), known_records)
            emit(f"{fname}({args})", orig_idx)
            continue

        # ── Pseudo: CALL function(args) with parens (before generic E++ call) ──
        m = re.match(r'(?i)^call\s+(\w+)\s*\((.+)\)$', line)
        if m:
            fname = m.group(1)
            args = process_expr(m.group(2), known_records)
            emit(f"{fname}({args})", orig_idx)
            continue

        m = re.match(r'(?i)^call\s+(\w+)\s*\(\s*\)$', line)
        if m:
            fname = m.group(1)
            emit(f"{fname}()", orig_idx)
            continue
            
        m = re.match(r'(?i)^call\s+(.*)$', line)
        if m:
            fname = process_expr(m.group(1), known_records)
            emit(f"{fname}()", orig_idx)
            continue

        # ── UI: create window titled "X" sized W by H. (more specific, check first) ──
        m = re.match(r'(?i)^create window titled\s+(.*?)\s+sized\s+(\d+)\s+by\s+(\d+)$', line)
        if m:
            title = process_expr(m.group(1), known_records)
            emit(f"epp_create_window({title}, {m.group(2)}, {m.group(3)})", orig_idx)
            continue

        # ── UI: create window titled "X". ──
        m = re.match(r'(?i)^create window titled\s+(.*)$', line)
        if m:
            title = process_expr(m.group(1), known_records)
            emit(f"epp_create_window({title})", orig_idx)
            continue

        # ── UI: load file "Y" into window "X". ──
        m = re.match(r'(?i)^load file\s+(.*?)\s+into window\s+(.*)$', line)
        if m:
            filepath = process_expr(m.group(1), known_records)
            title = process_expr(m.group(2), known_records)
            emit(f"epp_load_file_in_window({title}, {filepath})", orig_idx)
            continue

        # ── UI: open url "U" in window "X". ──
        m = re.match(r'(?i)^open url\s+(.*?)\s+in window\s+(.*)$', line)
        if m:
            url = process_expr(m.group(1), known_records)
            title = process_expr(m.group(2), known_records)
            emit(f"epp_load_url_in_window({title}, {url})", orig_idx)
            continue

        # ── UI: show windows. ──
        if lower_line == 'show windows':
            emit("epp_show_windows()", orig_idx)
            continue

        # ── UI: fetch page "url" into VAR. ──
        m = re.match(r'(?i)^fetch page\s+(.*?)\s+into\s+(.*)$', line)
        if m:
            url = process_expr(m.group(1), known_records)
            var = process_expr(m.group(2), known_records)
            emit(f"{var} = epp_fetch_page({url})", orig_idx)
            continue

        # ── UI: read text from html VAR into VAR2. ──
        m = re.match(r'(?i)^read text from html\s+(.*?)\s+into\s+(.*)$', line)
        if m:
            src = process_expr(m.group(1), known_records)
            var = process_expr(m.group(2), known_records)
            emit(f"{var} = epp_read_html_text({src})", orig_idx)
            continue

        # ── UI: read html file "X" into VAR. ──
        m = re.match(r'(?i)^read html file\s+(.*?)\s+into\s+(.*)$', line)
        if m:
            filepath = process_expr(m.group(1), known_records)
            var = process_expr(m.group(2), known_records)
            emit(f"{var} = epp_read_html_file({filepath})", orig_idx)
            continue

        # ══════════════════════════════════════════════════════════════════════
        # ══  PSEUDO CODE SUPPORT                                            ══
        # ══  Standard pseudo code keywords that map to Python equivalents.  ══
        # ══════════════════════════════════════════════════════════════════════

        # ── Pseudo: DECLARE variable = value / DECLARE variable AS type ──
        m = re.match(r'(?i)^declare\s+(.*?)\s*=\s*(.*)$', line)
        if m:
            var = process_expr(m.group(1), known_records)
            val = process_expr(m.group(2), known_records)
            emit(f"{var} = {val}", orig_idx)
            continue

        m = re.match(r'(?i)^declare\s+(.*?)\s+as\s+(integer|int|float|real|double|string|char|boolean|bool|array)$', line)
        if m:
            var = process_expr(m.group(1), known_records)
            dtype = m.group(2).lower()
            defaults = {
                'integer': '0', 'int': '0', 'float': '0.0', 'real': '0.0',
                'double': '0.0', 'string': "''", 'char': "''",
                'boolean': 'False', 'bool': 'False', 'array': '[]'
            }
            emit(f"{var} = {defaults.get(dtype, 'None')}", orig_idx)
            continue

        # ── Pseudo: DECLARE variable (no initializer) ──
        m = re.match(r'(?i)^declare\s+(.+)$', line)
        if m:
            var = process_expr(m.group(1), known_records)
            emit(f"{var} = None", orig_idx)
            continue

        # ── Pseudo: ASSIGN variable = value / ASSIGN value TO variable ──
        m = re.match(r'(?i)^assign\s+(.*?)\s*=\s*(.*)$', line)
        if m:
            var = process_expr(m.group(1), known_records)
            val = process_expr(m.group(2), known_records)
            emit(f"{var} = {val}", orig_idx)
            continue

        m = re.match(r'(?i)^assign\s+(.*?)\s+to\s+(.*)$', line)
        if m:
            val = process_expr(m.group(1), known_records)
            var = process_expr(m.group(2), known_records)
            emit(f"{var} = {val}", orig_idx)
            continue

        # ── Pseudo: PRINT / OUTPUT / DISPLAY ──
        m = re.match(r'(?i)^(?:print|output|display)\s+(.*)$', line)
        if m:
            val = process_expr(m.group(1), known_records)
            emit(f"print({val})", orig_idx)
            continue

        # ── Pseudo: INPUT variable / READ variable ──
        m = re.match(r'(?i)^(?:input|read)\s+(.*?)\s+(?:with prompt|prompt)\s+(.*)$', line)
        if m:
            var = process_expr(m.group(1), known_records)
            prompt = process_expr(m.group(2), known_records)
            emit(f"{var} = __ask__({prompt})", orig_idx)
            continue

        m = re.match(r'(?i)^(?:input|read)\s+(.+)$', line)
        if m:
            var = process_expr(m.group(1), known_records)
            emit(f"{var} = __ask__('')", orig_idx)
            continue

        # ── Pseudo: FUNCTION name(args) / PROCEDURE name(args) ──
        m = re.match(r'(?i)^(?:function|procedure|algorithm)\s+(\w+)\s*\((.*)\)$', line)
        if m:
            fname = m.group(1)
            args = m.group(2).strip()
            if args:
                arg_list = ', '.join(a.strip() for a in args.split(','))
                emit(f"def {fname}({arg_list}):", orig_idx)
            else:
                emit(f"def {fname}():", orig_idx)
            indent += 1
            continue

        # ── Pseudo: FUNCTION name / PROCEDURE name (no parens) ──
        m = re.match(r'(?i)^(?:function|procedure|algorithm)\s+(\w+)$', line)
        if m:
            fname = m.group(1)
            emit(f"def {fname}():", orig_idx)
            indent += 1
            continue

        # ── Pseudo: END FUNCTION / END PROCEDURE / ENDFUNCTION ──
        if lower_line in ('end function', 'endfunction', 'end procedure',
                          'endprocedure', 'end algorithm', 'endalgorithm'):
            indent -= 1
            continue

        # ── Pseudo: RETURN value ──
        m = re.match(r'(?i)^return\s+(.*)$', line)
        if m:
            val = process_expr(m.group(1), known_records)
            if not val.strip(): val = "None"
            emit(f"return {val}", orig_idx)
            continue

        if lower_line == 'return':
            emit("return", orig_idx)
            continue

        # ── Pseudo: IF condition THEN ──
        m = re.match(r'(?i)^if\s+(.*?)\s+then$', line)
        if m:
            cond = process_expr(m.group(1), known_records)
            emit(f"if {cond}:", orig_idx)
            indent += 1
            continue

        # ── Pseudo: ELSE IF / ELSEIF / ELIF condition THEN ──
        m = re.match(r'(?i)^(?:else\s*if|elseif|elif)\s+(.*?)\s+then$', line)
        if m:
            cond = process_expr(m.group(1), known_records)
            indent -= 1
            emit(f"elif {cond}:", orig_idx)
            indent += 1
            continue

        # ── Pseudo: ELSE IF / ELSEIF / ELIF condition (no THEN) ──
        m = re.match(r'(?i)^(?:else\s*if|elseif|elif)\s+(.+)$', line)
        if m:
            cond = process_expr(m.group(1), known_records)
            indent -= 1
            emit(f"elif {cond}:", orig_idx)
            indent += 1
            continue

        # ── Pseudo: ELSE ──
        if lower_line == 'else':
            indent -= 1
            emit("else:", orig_idx)
            indent += 1
            continue

        # ── Pseudo: ENDIF / END IF ──
        if lower_line in ('endif', 'end if'):
            indent -= 1
            continue

        # ── Pseudo: FOR var = start TO end STEP step ──
        m = re.match(r'(?i)^for\s+(\w+)\s*(?:=|<-)\s*(.*?)\s+to\s+(.*?)\s+step\s+(.*)$', line)
        if m:
            var = m.group(1)
            start = process_expr(m.group(2), known_records)
            end = process_expr(m.group(3), known_records)
            step = process_expr(m.group(4), known_records)
            emit(f"for {var} in range(int({start}), int({end}) + 1, int({step})):", orig_idx)
            indent += 1
            continue

        # ── Pseudo: FOR var = start TO end ──
        m = re.match(r'(?i)^for\s+(\w+)\s*(?:=|<-)\s*(.*?)\s+to\s+(.*)$', line)
        if m:
            var = m.group(1)
            start = process_expr(m.group(2), known_records)
            end = process_expr(m.group(3), known_records)
            emit(f"for {var} in range(int({start}), int({end}) + 1):", orig_idx)
            indent += 1
            continue

        # ── Pseudo: NEXT / ENDFOR / END FOR ──
        if lower_line in ('next', 'endfor', 'end for'):
            indent -= 1
            continue

        # ── Pseudo: WHILE condition DO / WHILE condition ──
        m = re.match(r'(?i)^while\s+(.*?)\s+do$', line)
        if m:
            cond = process_expr(m.group(1), known_records)
            emit(f"while {cond}:", orig_idx)
            indent += 1
            continue

        # ── Pseudo: ENDWHILE / END WHILE ──
        if lower_line in ('endwhile', 'end while'):
            indent -= 1
            continue

        # ── Pseudo: DO (start of do-while) ──
        if lower_line == 'do':
            emit("while True:", orig_idx)
            indent += 1
            continue

        # ── Pseudo: LOOP WHILE condition / UNTIL condition ──
        m = re.match(r'(?i)^loop\s+while\s+(.*)$', line)
        if m:
            cond = process_expr(m.group(1), known_records)
            emit(f"if not ({cond}): break", orig_idx)
            indent -= 1
            continue

        m = re.match(r'(?i)^(?:loop\s+)?until\s+(.*)$', line)
        if m:
            cond = process_expr(m.group(1), known_records)
            emit(f"if {cond}: break", orig_idx)
            indent -= 1
            continue

        # ── Pseudo: REPEAT...UNTIL ──
        if lower_line == 'repeat':
            emit("while True:", orig_idx)
            indent += 1
            continue

        # ── Pseudo: SWITCH / CASE (mapped to if/elif chain) ──
        m = re.match(r'(?i)^switch\s+(.*)$', line)
        if m:
            # Store the switch variable for case matching
            switch_var = process_expr(m.group(1), known_records)
            emit(f"__switch_val__ = {switch_var}", orig_idx)
            continue

        m = re.match(r'(?i)^case\s+(.*)$', line)
        if m:
            val = process_expr(m.group(1), known_records)
            emit(f"if __switch_val__ == {val}:", orig_idx)
            indent += 1
            continue

        if lower_line in ('default', 'otherwise'):
            indent -= 1
            emit("else:", orig_idx)
            indent += 1
            continue

        if lower_line in ('endswitch', 'end switch', 'endcase', 'end case'):
            indent -= 1
            continue

        # ── Pseudo: BREAK / EXIT ──
        if lower_line in ('break', 'exit'):
            emit("break", orig_idx)
            continue

        # ── Pseudo: CONTINUE / NEXT ITERATION ──
        if lower_line in ('continue', 'next iteration'):
            emit("continue", orig_idx)
            continue

        # ── Pseudo: BEGIN / END (block markers) ──
        if lower_line == 'begin':
            # BEGIN acts as a no-op block opener in many pseudo code styles
            continue

        if lower_line == 'end':
            # END can close any open block
            if indent > 0:
                indent -= 1
            continue

        # ── Pseudo: CALL function(args) / CALL function ──
        m = re.match(r'(?i)^call\s+(\w+)\s*\((.*)\)$', line)
        if m:
            fname = m.group(1)
            args = process_expr(m.group(2), known_records)
            emit(f"{fname}({args})", orig_idx)
            continue

        # ── Pseudo: variable <- value (assignment arrow) ──
        m = re.match(r'^(\w+)\s*<-\s*(.+)$', line)
        if m:
            var = m.group(1)
            val = process_expr(m.group(2), known_records)
            emit(f"{var} = {val}", orig_idx)
            continue

        # ── Pseudo: INCREMENT var BY n / DECREMENT var BY n (must be before simple) ──
        m = re.match(r'(?i)^increment\s+(.*?)\s+by\s+(.*)$', line)
        if m:
            var = process_expr(m.group(1), known_records)
            val = process_expr(m.group(2), known_records)
            emit(f"{var} += {val}", orig_idx)
            continue

        m = re.match(r'(?i)^decrement\s+(.*?)\s+by\s+(.*)$', line)
        if m:
            var = process_expr(m.group(1), known_records)
            val = process_expr(m.group(2), known_records)
            emit(f"{var} -= {val}", orig_idx)
            continue

        # ── Pseudo: INCREMENT var / DECREMENT var ──
        m = re.match(r'(?i)^increment\s+(.*)$', line)
        if m:
            var = process_expr(m.group(1), known_records)
            emit(f"{var} += 1", orig_idx)
            continue

        m = re.match(r'(?i)^decrement\s+(.*)$', line)
        if m:
            var = process_expr(m.group(1), known_records)
            emit(f"{var} -= 1", orig_idx)
            continue

        # ── Pseudo: SWAP var1 AND var2 / SWAP var1, var2 ──
        m = re.match(r'(?i)^swap\s+(\w+)\s+(?:and|,)\s+(\w+)$', line)
        if m:
            v1 = m.group(1)
            v2 = m.group(2)
            emit(f"{v1}, {v2} = {v2}, {v1}", orig_idx)
            continue

        emit(process_expr(line, known_records), orig_idx)

    final_py_code = "\n".join(py_lines)
    final_py_code = transform_ast_code(final_py_code)
    return final_py_code, line_map

def run_epp(filename):
    with open(filename, 'r') as f:
        code = f.read()
    
    py_code, line_map = parse_epp(code)
    
    try:
        exec(py_code, {"__name__": "__main__"})
    except Exception as e:
        _, _, tb = sys.exc_info()
        tb_list = traceback.extract_tb(tb)
        epp_line = None
        for frame in reversed(tb_list):
            if frame.filename == '<string>' and frame.lineno in line_map:
                epp_line = line_map[frame.lineno]
                break
                
        if epp_line:
            print(f"E++ Runtime Error on line {epp_line}: {e}")
        else:
            print(f"E++ Runtime Error: {e}")

def repl():
    print("E++ Interactive Shell (REPL)")
    print("Type 'exit.' or 'quit.' to close.")
    
    py_setup, _ = parse_epp("", is_repl=False)
    context = {}
    exec(py_setup, context)
    
    known_records = set()
    code_buffer = []
    
    while True:
        try:
            prompt = "...> " if code_buffer else "E++> "
            line = input(prompt)
            if not line.strip() and not code_buffer: continue
            
            if not code_buffer and line.strip().lower() in ('exit.', 'quit.', 'exit', 'quit'):
                break
                
            code_buffer.append(line)
            joined = " ".join(code_buffer)
            starts = len(re.findall(r'(?i)\b(if|while|repeat|for each|for\s+\w+\s*(?:=|<-)|define|try|text block|function|procedure|algorithm|do|switch)\b', joined))
            ends = len(re.findall(r'(?i)\b(end if|endif|end while|endwhile|end repeat|end for|endfor|next|end define|end try|end text|end function|endfunction|end procedure|endprocedure|end algorithm|endalgorithm|end switch|endswitch|until)\b', joined))
            
            if starts > ends:
                continue
                
            epp_code = "\n".join(code_buffer)
            code_buffer = []
            
            py_code, _ = parse_epp(epp_code, known_records=known_records, is_repl=True)
            
            try:
                exec(py_code, context)
            except Exception as e:
                print(f"E++ Runtime Error: {e}")
                
        except KeyboardInterrupt:
            code_buffer = []
            print()
        except EOFError:
            break

def main():
    if len(sys.argv) < 2:
        repl()
    else:
        run_epp(sys.argv[1])

if __name__ == '__main__':
    main()
