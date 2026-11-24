"""Bounded AST-to-SymPy construction. Never eval, sympify, or parse_expr user text."""
import ast
import re
import sympy as sp

class UnsupportedMath(ValueError): pass
SYMBOLS={n:sp.Symbol(n,real=True) for n in 'xyzt'}
FUNCTIONS={'sin':sp.sin,'cos':sp.cos,'tan':sp.tan,'sqrt':sp.sqrt}

def parse(expression):
    if len(expression)>300 or not re.fullmatch(r'[\w\s.+*/^()\-]+',expression,flags=re.ASCII):
        raise UnsupportedMath('Use a short arithmetic or algebraic expression')
    expression=expression.replace('^','**').strip()
    depth=0
    for char in expression:
        if char=='(':depth+=1
        elif char==')':depth-=1
        if depth>16:raise UnsupportedMath('Expression is too deeply nested')
    expression=re.sub(r'(?<=\d)(?=[A-Za-z(])|(?<=\))(?=[\dA-Za-z(])','*',expression)
    expression=re.sub(r'\b([xyzt])(?=\()' ,r'\1*',expression)
    expression=re.sub(r'\b[xyzt]{2,4}\b',lambda m:'*'.join(m[0]),expression)
    try: tree=ast.parse(expression,mode='eval')
    except (SyntaxError,RecursionError): raise UnsupportedMath('Malformed expression')
    if sum(1 for _ in ast.walk(tree))>90: raise UnsupportedMath('Expression is too complex')
    def build(node,depth=0):
        if depth>14: raise UnsupportedMath('Expression is too deeply nested')
        child=lambda n:build(n,depth+1)
        if isinstance(node,ast.Constant) and type(node.value) in (int,float):
            if not sp.Float(node.value).is_finite or abs(node.value)>1000000:raise UnsupportedMath('Number is too large')
            return sp.Rational(str(node.value))
        if isinstance(node,ast.Name):
            if node.id in SYMBOLS:return SYMBOLS[node.id]
            if node.id=='pi':return sp.pi
            raise UnsupportedMath('Only x, y, z, t and pi are supported')
        if isinstance(node,ast.UnaryOp) and isinstance(node.op,(ast.UAdd,ast.USub)):
            value=child(node.operand);return -value if isinstance(node.op,ast.USub) else value
        if isinstance(node,ast.BinOp):
            left,right=child(node.left),child(node.right)
            if isinstance(node.op,ast.Add):result=left+right
            elif isinstance(node.op,ast.Sub):result=left-right
            elif isinstance(node.op,ast.Mult):result=left*right
            elif isinstance(node.op,ast.Div):
                if right==0:raise UnsupportedMath('Division by zero')
                result=left/right
            elif isinstance(node.op,ast.Pow):
                if right.is_Integer is not True or abs(right)>8:raise UnsupportedMath('Use integer exponents between -8 and 8')
                result=left**right
            else:raise UnsupportedMath('Unsupported operator')
            if sp.count_ops(result)>45 or len(str(result))>600:raise UnsupportedMath('Expression is too complex')
            return result
        if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id in FUNCTIONS and len(node.args)==1 and not node.keywords:
            value=child(node.args[0])
            if value.has(sp.Function):raise UnsupportedMath('Nested functions are unsupported')
            return FUNCTIONS[node.func.id](value)
        raise UnsupportedMath('Unsupported mathematical syntax')
    result=build(tree.body)
    if result.has(sp.zoo,sp.oo,-sp.oo,sp.nan,sp.I):raise UnsupportedMath('A finite real result is required')
    return result

def polynomial(expr,degree=8):
    if not expr.free_symbols:return
    try:
        p=sp.Poly(expr,*sorted(expr.free_symbols,key=str))
        if p.total_degree()>degree or len(p.terms())>24:raise UnsupportedMath('Polynomial is too complex')
    except sp.PolynomialError:raise UnsupportedMath('Use a polynomial for this operation')

def fmt(expr):return str(expr).replace('**','^')

def solve(question,language='en'):
    """Return None for prose; return a verified result or a safe clarification for math."""
    q=question.strip();sw=language=='sw'
    operation='evaluate'
    commands=[('differentiate|derivative of|find the derivative of|kokotoa derivativi','differentiate'),
              ('integrate|integral of|find the integral of|kokotoa integrali','integrate'),
              ('simplify|rahisisha','simplify'),('factorize|factorise|factor|changanua','factor'),
              ('substitute|weka thamani','substitute'),('solve|tatua|calculate|evaluate|hesabu','evaluate')]
    expression=q
    for pattern,op in commands:
        m=re.match(r'^(?:'+pattern+r')\s+(.+)$',q,re.I)
        if m:operation=op;expression=m[1].strip();break
    # Prose such as "solve calculus" belongs to topic clarification, not the parser.
    if not re.search(r'\d|[+*/^=]|\b[xyzt]\b|\b(?:sin|cos|tan|sqrt)\(',expression):return None
    try:
        steps=[];latex='';verified=False
        if '=' in expression and operation!='substitute':
            equations=expression.split(';')
            if len(equations)>2:raise UnsupportedMath('Use at most two simultaneous linear equations')
            pairs=[]
            for equation in equations:
                if equation.count('=')!=1:raise UnsupportedMath('Use one equals sign per equation')
                left,right=map(parse,equation.split('='));polynomial(left-right,2);pairs.append((left,right))
            variables=sorted(set().union(*(a.free_symbols|b.free_symbols for a,b in pairs)),key=str)
            if not variables or len(variables)>2:raise UnsupportedMath('Use one or two variables')
            if len(pairs)==2:
                if len(variables)!=2:raise UnsupportedMath('Use two variables in a simultaneous system')
                for a,b in pairs:polynomial(a-b,1)
                solutions=sp.solve([a-b for a,b in pairs],variables,dict=True)
            else:
                if len(variables)!=1:raise UnsupportedMath('Give a second equation for two variables')
                solutions=sp.solve(pairs[0][0]-pairs[0][1],variables,dict=True)
            if not solutions or any(set(s)!=set(variables) for s in solutions):raise UnsupportedMath('No unique finite real solution was found')
            verified=all(all(sp.simplify((a-b).subs(s))==0 for a,b in pairs) for s in solutions)
            if not verified:raise UnsupportedMath('Could not verify the solution')
            if len(pairs)==1 and sp.Poly(pairs[0][0]-pairs[0][1],variables[0]).degree()==1:
                var=variables[0];p=sp.Poly(pairs[0][0]-pairs[0][1],var);a,b=p.all_coeffs()
                left,right=pairs[0];constant=sp.expand(left).coeff(var,0);right_coefficient=sp.expand(right).coeff(var)
                if right_coefficient:steps.append((f'Toa {fmt(right_coefficient*var)} pande zote mbili.' if sw else f'Subtract {fmt(right_coefficient*var)} from both sides.'))
                steps += [(f'Toa {fmt(constant)} pande zote mbili.' if sw else f'Subtract {fmt(constant)} from both sides.'),f'{fmt(a*var)} = {fmt(-b)}',
                       (f'Gawa kwa {fmt(a)}.' if sw else f'Divide by {fmt(a)}.')]
            else:steps=[('Tatua milinganyo kisha hakiki kila jibu katika milinganyo ya mwanzo.' if sw else 'Solve the polynomial equations, then substitute each candidate into the original equations.')]
            result='; '.join(', '.join(f'{v} = {fmt(s[v])}' for v in variables) for s in solutions)
            latex=r'\quad\text{or}\quad '.join(', '.join(sp.latex(v)+'='+sp.latex(s[v]) for v in variables) for s in solutions)
        elif operation=='substitute':
            m=re.fullmatch(r'(.+?)\s+(?:at|where|when|kwa)\s+([xyzt])\s*=\s*(.+)',expression,re.I)
            if not m:raise UnsupportedMath('Example: substitute x^2 + 1 at x = 3')
            expr=parse(m[1]);polynomial(expr);value=parse(m[3])
            if value.free_symbols:raise UnsupportedMath('Substitute a numeric value')
            out=expr.subs(SYMBOLS[m[2].lower()],value);result=fmt(out);latex=sp.latex(out);verified=True
            steps=[('Weka thamani uliyopewa katika kila nafasi ya kigezo.' if sw else 'Replace the variable with the given value, then evaluate.')]
        else:
            expr=parse(expression);variables=sorted(expr.free_symbols,key=str)
            if operation in ('differentiate','integrate'):
                if len(variables)>1:raise UnsupportedMath('Use one variable for calculus')
                var=variables[0] if variables else SYMBOLS['x']
                if expr.has(sp.Function):
                    if expr.func not in (sp.sin,sp.cos) or not expr.args[0].is_polynomial(var) or sp.degree(expr.args[0],var)>1:
                        raise UnsupportedMath('Calculus supports polynomials and sin/cos of linear expressions')
                else:polynomial(expr)
                out=sp.diff(expr,var) if operation=='differentiate' else sp.integrate(expr,var)
                verified=sp.simplify(sp.diff(expr,var)-out)==0 if operation=='differentiate' else sp.simplify(sp.diff(out,var)-expr)==0
                steps=[('Tumia kanuni ya nguvu kwa kila neno; hakiki kwa derivativi.' if sw else 'Apply the power rule to each polynomial term (or the chain rule for sin/cos). Check the derivative.')]
                result=fmt(out)+(' + C' if operation=='integrate' else '');latex=sp.latex(out)+(' + C' if operation=='integrate' else '')
            else:
                if operation=='factor':polynomial(expr);out=sp.factor(expr)
                else:
                    if expr.free_symbols:polynomial(sp.together(expr).as_numer_denom()[0]);polynomial(sp.together(expr).as_numer_denom()[1])
                    out=sp.simplify(expr)
                verified=sp.simplify(out-expr)==0;result=fmt(out);latex=sp.latex(out)
                steps=[('Rahisisha; hakiki usawa wa aljebra. Vizuizi vya kigawanyo cha mwanzo bado vinatumika.' if sw else 'Simplify and check algebraic equivalence. Original denominator restrictions still apply.')]
        if not verified:raise UnsupportedMath('Result verification failed')
        answer='\n'.join(steps+[result,('Imethibitishwa kwa hesabu za alama.' if sw else 'Verified symbolically.')])
        return dict(answer=answer,result=result,latex=latex,steps=steps,verified=True,source='SymPy symbolic verification',mode='symbolic mathematics',match_score=1.0)
    except (UnsupportedMath,ValueError,TypeError,NotImplementedError,ZeroDivisionError,RecursionError) as exc:
        return dict(answer=('Siwezi kutatua hili kwa usalama. Tumia usemi rahisi au omba msaada wa mwalimu.' if sw else 'I cannot solve this safely. Use a supported short expression or ask your teacher.'),
                    reason=str(exc)[:160],verified=False,source='No verified mathematical result',mode='math clarification',match_score=0)

def equivalent(left,right):
    """Closed numeric answers only; no variables, executable syntax, or approximate guesses."""
    try:
        a,b=parse(str(left)),parse(str(right))
        return not (a.free_symbols|b.free_symbols) and sp.simplify(a-b)==0
    except (UnsupportedMath,ValueError,TypeError,RecursionError):return False
