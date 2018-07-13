
import ast
import astunparse
import copy
import os
import re
import xml.etree.ElementTree as ET
from sympy import Symbol
from sympy.logic import simplify_logic
from sympy.parsing.sympy_parser import parse_expr
from pathlib import Path
#source = open('temp.py').read()
#tree = ast.parse(source)
#print(ast.dump(tree))
#os.remove('filename')
#os.system("python sampleAST.py > node2.txt")


nodes = {} # nodes is a dictionary  where key is variable name and value is a distinct integer
#nodes just maps a variable to some distinct integer
column_cnt = 1 # this is a counter which will increment whenever a new variable comes 

curr_step = ''

comp_cnt = 0 # counter 

'''
e_dict is a dictionary which will store a single row in the truth table and when we reach the 
destination step we append this e_dict to t_table list(appending a new row to truth table)
'''
e_dict = {}

''' 
to store the truth table for a topic  , we are using a list t_table . Each entry of t_table list will
be a dictionary , representing  a row in the truth table . The key of the dictionary will be a 
column name and its value will be 1(YES) and 0(NO)
'''
t_table = []


exp_sym = {} # mapping from expression to symbol
sym_exp = {} # reverse mapping of symbol to expression

'''
local_var_dict is a dictionary where the key is string representing name of a local variable in
python snippets and value for the key is a list of ui_fields on which this local variable depends .
same name for a local variable across multiple python snippets .(not handled for now)
'''
local_var_dict = {} 

regx_ui_field = '(tds|sp|taxp)([.])([A-Za-z0-9_]+)' # regex to capture the UI fields
calc_regex = '_calc[ \t]*[=][ \t]*["].*["]' # regex to capture the python snippets in the easystep xmls

# first step id regex to extract firse step id from interview
fsid_regex = 'first_step_id[ \t]*[=][ \t]*["].*["]' 

start_step = 's_pr_intro'   # starting easystep xml
dest_step = 's_pr_summary'  # end-of-topic easystep xml

loc =  '../../Downloads/turbotax-desktop-develop/content/easystep/xml/en'

s_folder = '/step/'
i_folder = '/interview/'

topic_name = 'PrincipalResidence'


visit_xml = {}    # to keep record of already visited xml files

rec_stack = {}  # to keep record of xmls in the current recursion stack
parent_step = 'start'  # to keep record of the parent step of the curr_step

def build_file_path(xml_file , xml_type = 'step'):
    f_path = ''
    if( xml_type == 'step' ):
        f_path = loc + s_folder  + topic_name + '/' + xml_file + '.xml'
    else:
        f_path = loc + i_folder + topic_name + '/' + xml_file + '.xml'
    return f_path    


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
    cval = 0
    #assuming that the comparisons == 1,!=0 , > , >= stand for yes condition i.e; flag = 1
    #can be modified later
    flag = 0
    
    if(isinstance(tt.comparators[0] , ast.Str )):
        if(tt.comparators[0].s == ''):
            cval = 0
    elif(isinstance(tt.comparators[0] , ast.Num )):
        cval = tt.comparators[0].n
    
    if(opgt or opgte or (opeq and cval >= 1)or(opneq and cval == 0)):
        flag = 1
    return flag




# helps to set column name in truth/decision table
def set_column_name(obj):
    if(isinstance(obj , ast.Name)):
        return obj.id
    elif(isinstance(obj , ast.Call)):
        return (astunparse.unparse(obj)[:-1])
        #return obj.func.id
    elif(isinstance(obj , ast.Compare)):
        if(isinstance(obj.left , ast.Call)):
            if(isinstance(obj.left.func , ast.Attribute)):
                return (astunparse.unparse(obj.left.func.value))[:-1]  
            return (astunparse.unparse(obj.left)[:-1])
            # [:-1] for removing \n which occurs as the last character
        else :    
            return obj.left.id
        
    #if(isinstance(expr.value.func , ast.Attribute)):
            #    
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
                elif(isinstance(itr.operand,ast.Name) or isinstance(itr.operand,ast.Call)):
                    condn.values[i].operand = set_val(copy.copy(itr.operand ))
                else:
                    solve_ifcond(itr.operand)
                    
            elif(isinstance(itr,ast.BoolOp)):
                solve_ifcond(itr)
                
        return None        
    elif(isinstance(condn ,ast.Compare)):
        return set_val(copy.copy(condn))
    elif(isinstance(condn , ast.UnaryOp)):
        if(isinstance(condn.operand,ast.Compare)):
            condn.operand = set_val(copy.copy(condn.operand ))
        elif( isinstance(condn.operand,ast.Name) or isinstance(condn.operand,ast.Call) ):
            condn.operand = set_val(copy.copy(condn.operand ))
        else:
            # case for BoolOp inside Not
            solve_ifcond(condn.operand)
        return condn    
        
    elif(isinstance(condn , ast.Name) or isinstance(condn, ast.Call)):
        return set_val(copy.copy(condn))


# to get the column name of  the truth table        
def get_column_name(itr):
    return sym_exp[itr.id]

# converts the condition in if to SOP(sum  of products form)
def convert_to_SOP(tt , carry_cond):
    cond_str = (astunparse.unparse(tt))[:-1] # [:-1] for removing \n which occurs as the last character

    # these replacements for converting the string to sympy logical expression
    # repalacing and with & , or with | , not with ~
    cond_str = cond_str.replace("and" ,"&")  
    cond_str = cond_str.replace("or" , "|")
    cond_str = cond_str.replace("not", "~")
    
    pe = parse_expr(cond_str)   # this function helps to convert the arg. string to sympy expression
    pe = ~carry_cond & pe      # use of carry_cond as explained above
    pe = simplify_logic(pe,'dnf')       # this function simplifies pe to SOP form
    # dnf stands for disjunctive normal form other name for SOP form
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

def find_next_xml(ss):
    xml_type =   ss[:(ss.index('|'))].strip()
    xml_file = ss[(ss.index('|')+1):].strip()
    # here handle  "step|s_pr_sp_transfer_1(showSummary=%d)"
    if(xml_type == 'interview'):
        xml_file = xml_file[:(xml_file.index('('))].strip()
    if(xml_type == 'step' and '(' in xml_file):
        xml_file = xml_file[:(xml_file.index('('))].strip()
    
        
    return  xml_type , xml_file


def handle_return(return_ob):
    global curr_step
    global parent_step
    #print(return_ob.value)
    if(isinstance(return_ob.value , ast.Num)):
        return 
    if(isinstance(return_ob.value , ast.Str)):
        xml_type , xml_file = find_next_xml(return_ob.value.s)
        
        if(xml_type == 'interview'):
            # handling intewrview 
            #computing interview xml location
            f_loc = build_file_path(xml_file , xml_type)
            
            # getting the first step id from yhe interview
            
            first_step = extract_from_xml(f_loc , xml_type = 'interview')
            
            # now we shall parse the first_step xml
            if(type(first_step) == list):
                return 
            
            parent_step = curr_step 
            
            curr_step = first_step
            
            f_loc = build_file_path(first_step , 'step')
            
            py_snippet = extract_from_xml(f_loc , xml_type = 'step')
            parse_ps(py_snippet)
            
        elif(xml_type == 'return'):
            # shall look into this later
            return 
        elif(xml_type == 'step'):
            
            parent_step = curr_step 
            
            curr_step = xml_file
            
            f_loc = build_file_path(xml_file , xml_type)
            py_snippet = extract_from_xml(f_loc , xml_type = 'step')
            parse_ps(py_snippet)


# this function helps to build decision/truth table 

def extract_UI_field(expr):
    # we will extract out the actual UI field from this expr
    if(isinstance(expr.value , ast.Call)):
        if(isinstance(expr.value.func , ast.Attribute)):
            return astunparse.unparse(expr.value.func.value)[:-1] 
            # [:-1] for removing \n which occurs as the last character
    return ''
    
def extract_for_mapper(exp_str):
    # will be completed later 
    return exp_str

def handle_local_var_dependency(v , rhs):
    # here I will try to handle only assignment and concatenation operation
    #local_var_dict
    
    global nodes
    global column_cnt
    
    rhs_str = (astunparse.unparse(rhs))[:-1] # [:-1] for removing \n which occurs as the last character
    ui_var = re.findall(regx_ui_field,rhs_str)
    
    if(v not in local_var_dict):
        local_var_dict[v] = list()
        for itr in ui_var:
            uvar = ''.join(itr)
            local_var_dict[v].append((uvar))
            if uvar not in nodes:
                nodes[uvar] = column_cnt
                column_cnt += 1
    else:
        for itr in ui_var:
            uvar = ''.join(itr)
            local_var_dict[v].append((uvar))
            if uvar not in nodes:
                nodes[uvar] = column_cnt
                column_cnt += 1
    
       
            
def build_decision_table(tree , carry_cond , inside_if = 1):
    # inside_if comes into picture when you encounter some return statement while parsing
    # inside_if is a flag which indicates whether a return statement is inside somew if or not
    # carry_cond for else part 
    '''
    carry_condn contains the SOP form for if condition
    eg. if(cond1):
            ......
        elif(cond2):
            ......
    for this case complete condition for elif part will be ~cond1 & cond2
    so we need to carry cond1  for elif , this is done here by carry_cond        
    '''
    
    global nodes
    global column_cnt
    
    for  b in tree : 
        
        
        if(isinstance(b ,ast.Assign)):
            
            if(isinstance(b.targets[0] , ast.Name)):
                v = b.targets[0].id
                handle_local_var_dependency(v,b.value)
            
            
            if(v not in nodes):
                nodes[v] = column_cnt
                column_cnt += 1
            # assuming that assign stmt is in form var  = ...    
        elif(isinstance(b,ast.Expr)):
            
            v = extract_UI_field(b)
            if(v == '' or (v not in nodes)):
                nodes[v] = column_cnt
                column_cnt += 1
                
        elif(isinstance(b , ast.Return) and inside_if):
            handle_return(b)
            
        elif(isinstance(b , ast.If)):  # checks for if statements
            tt = b.test
            #print(astunparse.unparse(tt)[:-1])       
            if(isinstance(tt,ast.Compare) or isinstance(tt,ast.Name) or isinstance(tt,ast.Call)):
                tt = solve_ifcond(tt) 
            else :
                solve_ifcond(tt) 
            # pe is sympy object which will be used later for carry_cond
            # for details about pe look into convert_to_SOP() module
            
            pe , alist = convert_to_SOP(tt , carry_cond)    
            for itr in alist:
                build_dtable_row(itr)
                build_decision_table(b.body,False)
                clear_dtable_entry(itr)
            
            # now we will handle else condition
                
            # else part parsing
            # we can check the case for only else 
            # the ast generated for 'elif' will be like that of an 'else' and in else's body 
            # there is an 'if'
            if(check_if(b.orelse)):
                build_decision_table( b.orelse , pe)           # calling for elif part
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
def parse_ps( py_snippet = []):
    global curr_step
    global parent_step
    tmp_list = list(inp_tag)
    
    tmp_curr = curr_step
    tmp_parent = parent_step
    #print(tmp_curr)
    rec_stack[curr_step] = 1    
    for pycode in py_snippet:
        
        tree = ast.parse(pycode)
        process_inp_list(tmp_list)
        curr_step = tmp_curr
        build_decision_table(tree.body , False , inside_if = 0 )
        #process_inp_list(tmp_list , clear_entry = 1)  
    
    curr_step = tmp_curr
    rec_stack[curr_step] = 0
    curr_step = tmp_parent

inp_tag = []
def extract_input_fields(root):
    if(root.tag == 'InputField'):
        inp_tag.append(root)
        return
    for child in root:
        extract_input_fields(child)

def process_inp_list(inp_tag , clear_entry = 0):
    global column_cnt
    for inp in inp_tag:
        attr_dict = inp.attrib
        if('default_mapping' in attr_dict):
            if(clear_entry):
                if attr_dict['default_mapping'] in e_dict :
                    del e_dict[attr_dict['default_mapping']]
            else:
                #print(attr_dict['default_mapping'])
                nodes[attr_dict['default_mapping']] = column_cnt
                column_cnt += 1
                e_dict[attr_dict['default_mapping']] = 1
# this function extracts:
# first step id from xml if the xml file is an interview and returns it
# list of python snippets from the xml file if the xml file is an step
def extract_from_xml(xml_file , xml_type = 'step'):
    
    my_file = Path(xml_file)
    
    if(not my_file.is_file()):
        return list()
    
    
    if(xml_file == dest_step ): # this condition is for the case when we reach the destination
        #print('hello')
        #print('\n****************\n')
        t_table.append(dict(e_dict))
        return list()           # xml for the topic
    
    if(curr_step in rec_stack and rec_stack[curr_step] == 1) : # if the curr_step is already present in the recursion stack
        return list()
    
    # if not present in recursion stack
    
    
    
    
    
    
    '''
    if( xml_file in visit_xml ):
        return list()
    
    visit_xml[xml_file] = 1
    '''
    
    # the xml file passed to this function is read as a string and stored in ss
    ss = open( xml_file , encoding='ISO-8859-1' ).read()
    
    if(xml_type == 'interview'):
        #finding first step id 
        first_step = re.findall(fsid_regex , ss)[0]
        #print(first_step)
        # some processing to get the first step id  enclosed in double quotes
        idx1 = first_step.index('"')
        idx2 = first_step.index('"' , idx1+1)
        first_step = str(first_step[idx1+1:idx2])
        #print(first_step)
        return first_step
    
    
    #   when xml_type is step ,  we find all the python calcs and store it in mlist
    
    
    '''
    now we will try to find all the input  UI fields present on some screen .
    '''
    global inp_tag
    inp_tag.clear()
    
    root = ET.fromstring(ss)
    extract_input_fields(root)
    
    
    
    
    mlist = re.findall(calc_regex , ss)
    # some processing to get the python code enclosed in double quotes
    for i in range(len(mlist)):
        idx1 = mlist[i].index('"')
        idx2 = mlist[i].index('"' , idx1+1)
        mlist[i] = str(mlist[i][idx1+1 : idx2])
        mlist[i] = unencodePythonSnippet(  mlist[i] )
    
    return mlist

def expand_ttable():
    for i in range(len(t_table)):
        # row is a dictionary 
        del_list = []
        temp_dict = {}
        for key in t_table[i] :
            if key in local_var_dict :
                for val in local_var_dict[key]:
                    temp_dict[val] = t_table[i][key]
                    
                del_list.append(key)
        
        for d in del_list:
            del t_table[i][d]  
        for key in temp_dict :
            t_table[i][key] = temp_dict[key]    

    


        
def start_generation():
    global curr_step
    parent_step = 'start'
    curr_step = start_step
    f_loc = build_file_path(xml_file = start_step , xml_type = 'step')
    py_snippet = extract_from_xml(f_loc, 'step')
    parse_ps(py_snippet)
dest_step = build_file_path(xml_file = dest_step , xml_type = 'step')    
start_generation()  
expand_ttable()  

# not handled the case for same local variable in different python snippet and file

