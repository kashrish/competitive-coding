
#ast.parse()
#ast.dump()
#astunparse.unparse()
import ast
import astunparse
import copy
import os
import re
import xml.etree.ElementTree as ET
from sympy import Symbol
from sympy import symbols
from sympy.logic import simplify_logic
from sympy.parsing.sympy_parser import parse_expr
#source = open('temp.py').read()
#tree = ast.parse(source)
#print(ast.dump(tree))
#os.remove('filename')
#os.system("python sampleAST.py > node2.txt")
nodes = {}
column_cnt = 1
e_dict = {}
t_table = []
exp_sym = {} # mapping from expression to symbol
sym_exp = {} # reverse mapping of symbol to expression
comp_cnt = 0

calc_regex = '_calc[ \t]*[=][ \t]*["].*["]'

#this function helps to find the next python script


def find_next_script(ss):
      
    return ss[(ss.index('|')+1):].strip()


# here flag represents YES or NO i.e; flag =1 means YES  flag = 0 means NO 
def set_flag(tt):
    # checking what type of comparison it is
    if(isinstance(tt,ast.Call) or isinstance(tt,ast.Name)):
        return 1
    opeq = isinstance(tt.ops[0],ast.Eq)
    opgt = isinstance(tt.ops[0],ast.Gt)
    opgte = isinstance(tt.ops[0] , ast.GtE)
    oplt = isinstance(tt.ops[0],ast.Lt)
    oplte = isinstance(tt.ops[0],ast.LtE)
    opneq = isinstance(tt.ops[0] , ast.NotEq)
    # here assuming ast.Num
    cval = tt.comparators[0].n
    #assuming that the comparisons =1,!=0 , > , >= stand for yes condition i.e; flag = 1
    #can be modified later
    flag = 0
    if(opgt or opgte or (opeq and cval == 1)or(opneq and cval == 0)):
        flag = 1
    return flag


# helps to set column name in truth/decision table
def set_column_name(obj):
    if(isinstance(obj , ast.Name)):
        return obj.id
    elif(isinstance(obj , ast.Call)):
        return obj.func.id
    elif(isinstance(obj , ast.Compare)):
        return obj.left.id
# generates ast.Name and ast.UnaryOp objects for repacement in the ast    
def set_val(cmpr):
    global comp_cnt
    
    col_name = set_column_name(cmpr)
    if( col_name not in exp_sym):
        comp_cnt += 1
        sym_val =  'cmp' + str(comp_cnt)
        exp_sym[col_name] = sym_val
        sym_exp[sym_val] = col_name
    flag = set_flag(cmpr)
    if(flag):
        ob = ast.Name(id = exp_sym[col_name],ctx = ast.Load())
        return ob
    else :
        ob = ast.UnaryOp(op = ast.Not() , operand = ast.Name(id = exp_sym[col_name] , ctx = ast.Load()))
        return ob
    
# solve_ifcond function tries to assign a unique value to each ast.Compare object
# and hacks into the parse tree to  replace each comparision object by an ast.Name object        
def solve_ifcond(condn):  # comp_cnt for keeping count of comparison conditions encountered
    
    if(isinstance(condn ,ast.BoolOp))  :
        l = len(condn.values)
        for i in range(0,l):
            itr = condn.values[i]
            if(isinstance(itr,ast.Call) or isinstance(itr,ast.Name)):
                condn.values[i] = set_val(copy.copy(itr))
            elif(isinstance(itr,ast.Compare)):
                condn.values[i] = set_val(copy.copy(itr))
            elif(isinstance(itr,ast.UnaryOp)):
                if(isinstance(itr.operand,ast.Compare)):
                    condn.values[i].operand = set_val(copy.copy(itr.operand ))
                elif(isinstance(itr.operand,ast.Name)):
                    condn.values[i].operand = set_val(copy.copy(itr.operand ))
                else:
                    solve_ifcond(itr.operand)
                    
            elif(isinstance(itr,ast.BoolOp)):
                solve_ifcond(itr)
                
        return None        
    elif(isinstance(condn ,ast.Compare)):
        return set_val(copy.copy(condn))
        
    elif(isinstance(condn , ast.Name) or isinstance(condn, ast.Call)):
        return set_val(copy.copy(condn))


# to get the column name of  the truth table        
def get_column_name(itr):
    return sym_exp[itr.id]

# converts the condition in if to SOP(sum  of products form)
def convert_to_SOP(tt , carry_cond):
    cond_str = (astunparse.unparse(tt))[:-1] # for removing \n which occurs as the last character

    # these replacements for converting the string to sympy logical expression
    # repalacing and with & , or with | , not with ~
    cond_str = cond_str.replace("and" ,"&")  
    cond_str = cond_str.replace("or" , "|")
    cond_str = cond_str.replace("not", "~")
    
    pe = parse_expr(cond_str)    
    pe = ~carry_cond & pe      # this function helps to convert the arg. string to sympy expression
    pe = simplify_logic(pe,'dnf')       # this function simplifies b to SOP form
    
    # now we do re-replacement    to make it a python expression
    cond_str = str(pe)
    
    #print(cond_str)
    cond_str = cond_str.replace('&' , ' and ')
    cond_str = cond_str.replace('|', ' or ')
    cond_str = cond_str.replace('~', ' not ')
    return pe , cond_str.split("or")


# handling else condition
def handle_else(pe):
    pe = simplify_logic(~pe,'dnf')       # this function simplifies b to SOP form
    
    # now we do re-replacement    to make it a python expression
    cond_str = str(pe)
    
    #print(cond_str)
    cond_str = cond_str.replace('&' , ' and ')
    cond_str = cond_str.replace('|', ' or ')
    cond_str = cond_str.replace('~', ' not ')
    return cond_str.split("or")



# this function helps to build truth table entry
def build_dtable_row(cmp_cond):
    arg_str = 'tmp = ' + cmp_cond  # string for parsing
    tr = ast.parse(arg_str)
    itr = tr.body[0].value
    
    if(isinstance(itr,ast.Name)):
        e_dict[get_column_name(itr)] = 1
    elif(isinstance(itr,ast.UnaryOp)):
        e_dict[get_column_name(itr.operand)] = 0      # if expression contains eg. 'not a'
    elif(isinstance(itr,ast.BoolOp)):
        for tt in itr.values:
            if(isinstance(tt,ast.Name)):
                e_dict[get_column_name(tt)] = 1
            elif(isinstance(tt,ast.UnaryOp)):
                e_dict[get_column_name(tt.operand)] = 0
     
#   this function helps to clear truth table entry 
def clear_dtable_entry(cmp_cond):
    arg_str = 'tmp = ' + cmp_cond  # string for parsing
    tr = ast.parse(arg_str)
    itr = tr.body[0].value
    
    if(isinstance(itr,ast.Name)):
        if get_column_name(itr) in e_dict :
            del e_dict[get_column_name(itr)]
    elif(isinstance(itr,ast.UnaryOp)):
        if get_column_name(itr.operand) in e_dict :
            del e_dict[get_column_name(itr.operand)]     # if expression contains eg. 'not a'
    elif(isinstance(itr,ast.BoolOp)):
        for tt in itr.values:
            if(isinstance(tt,ast.Name)):
                if get_column_name(tt) in e_dict :
                    del e_dict[get_column_name(tt)]
            elif(isinstance(tt,ast.UnaryOp)):
                if get_column_name(tt.operand) in e_dict :
                    del e_dict[get_column_name(tt.operand)]
# checks whether there is some if statement inside else of some if
def check_if(body):
    for itr in body:
        if isinstance(itr , ast.If):
            return 1
    return 0   

# this function helps to build decision/truth table 
def build_decision_table(tree , carry_cond):
    # carry_cond for else part 
    global edges
    global nodes
    global column_cnt
    
    for  b in tree : 
        
        if(isinstance(b ,ast.Assign)):
            v = b.targets[0].id
            if(v == 'next_ps'):
                pscript = find_next_script(b.value.s)
                if(pscript == 'final_dest.py'):
                    t_table.append(dict(e_dict))
                    return
                parse_ps(pscript)
                
            else:
                if(v not in nodes):
                    nodes[v] = column_cnt
                    column_cnt += 1
                
            
        elif(isinstance(b , ast.If)):  # checks for if statements
            tt = b.test
            if(isinstance(tt,ast.Compare) or isinstance(tt,ast.Name) or isinstance(tt,ast.Call)):
                tt = solve_ifcond(tt) 
            else :
                solve_ifcond(tt) 
                
            pe , alist = convert_to_SOP(tt , carry_cond)    
            for itr in alist:
                build_dtable_row(itr)
                build_decision_table(b.body,False)
                clear_dtable_entry(itr)
            
            # now we will handle else condition
                
            # else part parsing
            # we can check the case for only else 
            
            if(check_if(b.orelse)):
                build_decision_table( b.orelse , pe)           # calling for else part
            elif( len(b.orelse) > 0):
                # if the b.orelse doesn't contain any ast.If obj 
                alist = handle_else(pe)
                for itr in alist :
                    build_dtable_row(itr)
                    build_decision_table(b.orelse,False)
                    clear_dtable_entry(itr)
                

# this function used for replacing unicode encodings with the corresponding characters  
# function borrowed from .java file                    
def unencodePythonSnippet( s ):
    s = s.replace('&#10;' , '\n')
    s = s.replace("&apos;", "'")
    s = s.replace("&quot;", '"')
    s = s.replace("&lt;", "<")
    s = s.replace("&gt;", ">")
    return s
    

# this function parses the python and builds AST     
# this function helps to parse a python script passed as parameter           
def parse_ps(pscript):
    source = unencodePythonSnippet( open(pscript).read() )
    tree = ast.parse(source)
    build_decision_table(tree.body , False)


# this function extracts the python snippets from the xml file
def extract_from_xml(xml_file):
    ss = open(xml_file , encoding='ISO-8859-1').read()
    mlist = re.findall(calc_regex , ss)
    for i in range(len(mlist)):
        idx1 = mlist[i].index('"')
        idx2 = mlist[i].index('"' , idx1+1)
        mlist[i] = str(mlist[i][idx1+1 : idx2])
        mlist[i] = unencodePythonSnippet(  mlist[i] )
    
          
    fh = open('py_new.py' , 'w')
    fh.close()
    fh = open('py_new.py' , 'a')
    for itr in mlist:
        fh.write(itr + '\n\n\n\n  ********************* \n\n\n\n\n')
        
    fh.close()        
    return mlist


inp_tag = []
def extract_input_fields(root):
    if(root.tag == 'InputField'):
        inp_tag.append(root)
        return
    for child in root:
        extract_input_fields(child)
        



#mlist = extract_from_xml('./PrincipalResidence/s_pr_sp_dispose.xml')


parse_ps('step1.py')
#print(t_table) 


'''
pscript = 'temp.py'
source = open(pscript).read()
tree = ast.parse(source)
'''


'''
xml_file  = './PrincipalResidence/s_pr_intro.xml'

ss = open(xml_file , encoding='ISO-8859-1').read()
root = (ET.parse(xml_file)).getroot()  #= ET.fromstring(ss)
extract_input_fields(root)

for inp in inp_tag:
    attr_dict = inp.attrib
    if('default_mapping' in attr_dict):
        print(attr_dict['default_mapping'])
'''

