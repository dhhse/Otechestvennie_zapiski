import docx
import re

from xml.dom import minidom

import fitz  # работает

root = minidom.Document()   #создаем хмл-файл. Есть еще другие библиотеки, типо ElementryTree
tei = root.createElement("TEI")
root.appendChild(tei)
teiheader = root.createElement("teiHeader")
tei.appendChild(teiheader)

filedesc = root.createElement("fileDesc")
teiheader.appendChild(filedesc)

titlestmt = root.createElement("titleStmt")
filedesc.appendChild(titlestmt)

title1 = root.createElement("title")
titlestmt.appendChild(title1)
body = root.createElement("body") #первый дочерний тег, боди. Планируется, что остальные теги (название журнала, год издания, авторы и прочее), будут дочерними тегами
title1.appendChild(body)

div = root.createElement("div")
body.appendChild(div)

doc = fitz.Document("/home/zhenya/PycharmProjects/project1/tdoc.pdf")
page_count = doc.pageCount
i = 0
text = ""
while i < page_count:
    pge = doc.loadPage(i)
    page = root.createElement("pb=")
    div.appendChild(page)
    page.appendChild(root.createTextNode(str(i)))
    p = root.createElement("p")
    div.appendChild(p)
    p.appendChild(root.createTextNode(pge.getText("text").replace("\n", " "))) 
    i += 1
xml_str = root.toprettyxml('\t')
save_path = ("test.xml")
with open(save_path, "w", encoding="utf-8") as f:
    f.write(xml_str)