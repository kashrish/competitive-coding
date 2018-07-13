'''
from xml.etree.ElementTree import ElementTree
from xml.etree.ElementTree import Element
import xml.etree.ElementTree as etree

root = Element('person')
tree = ElementTree(root)

#print(etree.tostring(root))

name = Element('name')
root.append(name)

name.text = 'Julie'

root.set('id' , '123')

tree.write(open('person.xml' , 'wb') , encoding = 'ISO-8859-1')

'''


from xml.dom import minidom
import os

import topic_truthtable as ttu

t_table = ttu.t_table
nodes = ttu.nodes
column_cnt = ttu.column_cnt

for i in range(len(t_table)):
    
    for v in t_table[i]:
        
        if(v not in nodes):
            nodes[v] = column_cnt
            column_cnt += 1


reverse_map = {}

for key in nodes:
    reverse_map[nodes[key]] = key 


d_values = list(nodes.values())
d_values.sort()

cnt = 0

nodes = {}
for i in range(len(d_values)):
    
    nodes[reverse_map[d_values[i]]]= cnt
    cnt += 1

    
reverse_map = {}
for key in nodes:
    reverse_map[nodes[key]] = key 



root = minidom.Document()

xml = root.createElement('TopicDecisionTable')
xml.setAttribute('xmlns' , "http://ctg.intuit.com/tla/decisions")
xml.setAttribute('isTopLevel' , "true")
xml.setAttribute('isMultiCopy' , "false")
xml.setAttribute('category',"REQUIRED")
root.appendChild(xml)

TopicName = root.createElement('TopicName')
TopicName.appendChild(root.createTextNode('PrincipalResidence'))
Path = root.createElement('Path')
Path.appendChild(root.createTextNode('/Return/ReturnData'))
Header = root.createElement('Header')

for i in range(len(nodes)):
    Cell = root.createElement('Cell')
    Cell.setAttribute('xmlns:xsi' , "http://www.w3.org/2001/XMLSchema-instance")
    Cell.setAttribute('xsi:type' , "ExpressionColumn")
    Cell.setAttribute('index' , str(i))
    Nodes = root.createElement('Nodes')
    Node = root.createElement('Node')
    Node.appendChild(root.createTextNode('3'))
    Nodes.appendChild(Node)
    Cell.appendChild(Nodes)
    Expression = root.createElement('Expression')
    Expression.appendChild(root.createTextNode(reverse_map[i]))
    Cell.appendChild(Expression)
    XPathReferences = root.createElement('XPathReferences')
    Cell.appendChild(XPathReferences)
    
    Header.appendChild(Cell)




#import topic_truthtable as ttu
#t_table = ttu.t_table

xml.appendChild(TopicName)
xml.appendChild(Path)
xml.appendChild(Header)


for i in range(len(t_table)):
    Rows = root.createElement('Rows')
    Rows.setAttribute('index' , str(i))
    Rows.setAttribute('count' , '0')
    ValueCell = root.createElement('ValueCell')
    for v in t_table[i]:
        Cell = root.createElement('Cell')
        value = "true"
        if(t_table[i][v] == 1):
            value = "true"
        else:
            value = "false"
        
        Cell.setAttribute('index' , str(nodes[v]))
        Cell.setAttribute('value' , value)
        ValueCell.appendChild(Cell)
        
    Rows.appendChild(ValueCell)
    xml.appendChild(Rows)


    
    





xml_str = root.toprettyxml(indent = "\t")

save_path_file = 'PrincipalResidenceDecisionTable.xml'

with open(save_path_file , "w") as f:
    f.write(xml_str)