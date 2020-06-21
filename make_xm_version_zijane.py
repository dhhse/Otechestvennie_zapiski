from xml.dom import minidom
import fitz 

root = minidom.Document()
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
body = root.createElement(
    "body")  # первый дочерний тег, боди. Планируется, что остальные теги (название журнала, год издания, авторы и прочее), будут дочерними тегами
title1.appendChild(body)
doc = fitz.Document("VOLUME_1.pdf")
page_count = doc.pageCount
i = 2
while i < page_count:
    pge = doc.loadPage(i)
    page = root.createElement("pb")
    body.appendChild(page)
    page.appendChild(root.createTextNode(str(i)))
    if i == 2:
        volume = root.createElement("volume")
        body.appendChild(volume)
        volume.appendChild(root.createTextNode(pge.getText("text").replace("\n", " ")))
    if i == 3:
        other_information = root.createElement("type")
        body.appendChild(other_information)
        other_information.appendChild(
            root.createTextNode(pge.getText("text").split('\n')[0] + ' ' + pge.getText("text").split('\n')[1]))
        epigraph = root.createElement("epigraph")
        other_information.appendChild(epigraph)
        epigraph.appendChild(root.createTextNode(
            pge.getText("text").split('\n')[2] + ' ' + pge.getText("text").split('\n')[3] + ' ' +
            pge.getText("text").split('\n')[4] + ' ' + pge.getText("text").split('\n')[5] + ' ' +
            pge.getText("text").split('\n')[6] + ' ' + pge.getText("text").split('\n')[7]))
        publication = root.createElement("publication_city_year")
        other_information.appendChild(publication)
        publication.appendChild(
            root.createTextNode(pge.getText("text").split('\n')[8] + ' ' + pge.getText("text").split('\n')[9]))
    if i == 4:
        typographie = root.createElement("typographie")
        body.appendChild(typographie)
        typographie.appendChild(root.createTextNode(pge.getText("text").split('\n')[0]))
        year = root.createElement("year")
        typographie.appendChild(year)
        year.appendChild(root.createTextNode(pge.getText("text").split('\n')[1]))
    if i == 5:
        censors = root.createElement("censorship_approval")
        body.appendChild(censors)
        censors.appendChild(root.createTextNode(pge.getText("text").replace('\n', ' ')))
    if i == 6:
        head = root.createElement("head")
        body.appendChild(head)
        head.appendChild(root.createTextNode(
            pge.getText("text").split('\n')[0] + ' ' + pge.getText("text").split('\n')[1] + ' ' +
            pge.getText("text").split('\n')[2] + ' ' + pge.getText("text").split('\n')[3] + ' '))
        p = root.createElement("p")
        body.appendChild(p)
        p.appendChild(root.createTextNode(pge.getText("text").replace('\n', ' ')))
    if 7 <= i <= 1058: # учет содержания
        head = root.createElement("head")
        body.appendChild(head)
        head.appendChild(root.createTextNode(
            pge.getText("text").split('\n')[0] + ' ' + pge.getText("text").split('\n')[1]))
        p = root.createElement("p")
        body.appendChild(p)
        p.appendChild(root.createTextNode(pge.getText("text").replace('\n', ' ')))
    if i > 1058:
        p = root.createElement("p")
        body.appendChild(p)
        p.appendChild(root.createTextNode(pge.getText("text").replace('\n', ' ')))
    i += 1
xml_str = root.toprettyxml('\t')
save_path = ("corrected.xml")
with open(save_path, "w", encoding="utf-8") as f:
    f.write(xml_str)
#КОД, ЕСЛИ В ТОМЕ ЕСТЬ INDEXERROR
i = 2
while i != page_count:
    pge = doc.loadPage(i)
    page = root.createElement("pb")
    body.appendChild(page)
    page.appendChild(root.createTextNode(str(i)))
    if i == 2:
        volume = root.createElement("volume")
        body.appendChild(volume)
        volume.appendChild(root.createTextNode(pge.getText("text").replace('\n', ' ')))
    if i == 3:
        other_information = root.createElement("type")
        body.appendChild(other_information)
        other_information.appendChild(
            root.createTextNode(pge.getText("text").split('\n')[5] + pge.getText("text").split('\n')[6]))
        epigraph = root.createElement("epigraph")
        body.appendChild(epigraph)
        epigraph.appendChild(root.createTextNode(
            pge.getText("text").split('\n')[7] + pge.getText("text").split('\n')[8] + pge.getText("text").split('\n')[9]))
        number_of_volume = root.createElement("number_of_volume")
        body.appendChild(number_of_volume)
        number_of_volume.appendChild(
            root.createTextNode(pge.getText("text").split('\n')[10] + pge.getText("text").split('\n')[11]))
        meta = root.createElement("meta_information")
        body.appendChild(meta)
        meta.appendChild(root.createTextNode(
            pge.getText("text").split('\n')[12] + pge.getText("text").split('\n')[13] + pge.getText("text").split('\n')[
                14]))
    if i == 4:
        typographie = root.createElement("censorship_approval")
        body.appendChild(typographie)
        typographie.appendChild(root.createTextNode(pge.getText("text").split('\n')[1] + pge.getText("text").split('\n')[2]))
    if i == 5:
        head = root.createElement("head")
        body.appendChild(head)
        head.appendChild(root.createTextNode(
            pge.getText("text").split('\n')[1] + ' ' + pge.getText("text").split('\n')[2] + ' ' +
            pge.getText("text").split('\n')[3] + ' ' + pge.getText("text").split('\n')[4] + ' '))
        p = root.createElement("p")
        body.appendChild(p)
        p.appendChild(root.createTextNode(pge.getText("text").replace('\n', ' ')))
    if 6 <= i < 1046:
        try:# учет содержания
            head = root.createElement("head")
            body.appendChild(head)
            head.appendChild(root.createTextNode(pge.getText("text").split('\n')[0] + pge.getText("text").split('\n')[1]))
            p = root.createElement("p")
            body.appendChild(p)
            p.appendChild(root.createTextNode(pge.getText("text").replace('\n', ' ')))
        except IndexError as er:
            print('defected_page') #ГДЕ СМЕЩЕНЫ СТРАНИЦЫ, ПРОСТО БУДЕТ ТЕГ PB С НОМЕРОМ СТРАНИЦЫ
    if i >= 1046:
        p = root.createElement("p")
        body.appendChild(p)
        p.appendChild(root.createTextNode(pge.getText("text").replace('\n', ' ')))
    i += 1
xml_str = root.toprettyxml('\t')
save_path = ("volume_2.xml")
with open(save_path, "w", encoding="utf-8") as f:
    f.write(xml_str)
