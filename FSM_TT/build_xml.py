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

import sampleAST as ttu
t_table = ttu.t_table

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

n = len(ttu.nodes)


for i in range(n):
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
    Cell.appendChild(Expression)
    XPathReferences = root.createElement('XPathReferences')
    Cell.appendChild(XPathReferences)
    
    Header.appendChild(Cell)

Rows = root.createElement('Rows')
Rows.setAttribute('index' , '0')
Rows.setAttribute('count' , '0')



t_table = ttu.t_table
nodes = ttu.nodes
column_cnt = ttu.column_cnt
for i in range(len(t_table)):
    ValueCell = root.createElement('ValueCell')
    for v in t_table[i]:
        Cell = root.createElement('Cell')
        value = "true"
        if(t_table[i][v] == 1):
            value = "true"
        else:
            value = "false"
        if(v not in nodes):
            nodes[v] = column_cnt
            column_cnt += 1
        Cell.setAttribute('index' , str(nodes[v]))
        Cell.setAttribute('value' , value)
        ValueCell.appendChild(Cell)
        
    Rows.appendChild(ValueCell)
    



xml.appendChild(TopicName)
xml.appendChild(Path)
xml.appendChild(Header)
xml.appendChild(Rows)




xml_str = root.toprettyxml(indent = "\t")

save_path_file = 'PrincipalResidenceDecisionTable.xml'

with open(save_path_file , "w") as f:
    f.write(xml_str)