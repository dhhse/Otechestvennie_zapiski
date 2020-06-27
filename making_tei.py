#Структура кода
from xml.dom import minidom 
import fitz #для чтения pdf

doc = fitz.Document("VOLUME_1.pdf")
page_count = doc.pageCount

##Шапка##
root = minidom.Document() #создаем корневой тег
tei = root.createElement("TEI") # тег, которому привязываем text
root.appendChild(tei)
teiheader = root.createElement("teiHeader")
tei.appendChild(teiheader)
filedesc = root.createElement("fileDesc")
teiheader.appendChild(filedesc)
titlestmt = root.createElement("titleStmt")
filedesc.appendChild(titlestmt)
title1 = root.createElement("title")
titlestmt.appendChild(title1)
title1.appendChild(root.createTextNode(doc.loadPage(2).getText("text").replace("\n", " "))) #ОТЕЧЕСТВЕННЫЕ ЗАПИСКИ и ТОМЪ номер тома - название журнала
text = root.createElement(
    "text")  # тег, которому привязываем теги fronts и body
tei.appendChild(text)
front = root.createElement(
    "front")  # тег, к которому привязываем теги с информацией о журнале
text.appendChild(front)
body = root.createElement(
    "body")  # тег, к которому привязываем теги с названиями разделов и журнальным номером страниц head и тег параграфов текста p. 
text.appendChild(body)
i = 2 #первый номер непустой страницы (с текстом)

##Цикл для разметки страниц
while i < page_count:
    pge = doc.loadPage(i) #загружаем страницу
    #if i == 2:
        # тег для основного номера страницы
        page = root.createElement("pb")
        front.appendChild(page)
        page.appendChild(root.createTextNode(str(i)))
        # тег для названия журнала
        mt = root.createElement("main_title")
        front.appendChild(mt)
        mt.appendChild(root.createTextNode(pge.getText("text").replace("\n", " ")))
        # номер тома
        number_of_volume = root.createElement("number_of_volume")
        front.appendChild(number_of_volume)
        number_of_volume.appendChild(
            root.createTextNode(pge.getText("text").split('\n')[40]))
    #if i == 3:
        page = root.createElement("pb")
        front.appendChild(page)
        page.appendChild(root.createTextNode(str(i)))
        # тип журнала
        type = root.createElement("type") #учено-литературный журнал
        front.appendChild(front)
        type.appendChild(
            root.createTextNode(pge.getText("text").split('\n')[0] + ' ' + pge.getText("text").split('\n')[1]))
        # эпиграф
        epigraph = root.createElement("epigraph")
        front.appendChild(epigraph)
        epigraph.appendChild(root.createTextNode(
            pge.getText("text").split('\n')[2] + ' ' + pge.getText("text").split('\n')[3] + ' ' +
            pge.getText("text").split('\n')[4] + ' ' + pge.getText("text").split('\n')[5] + ' ' +
            pge.getText("text").split('\n')[6] + ' ' + pge.getText("text").split('\n')[7]))
        # мета-информация
        meta= root.createElement("meta_information") #пример: № 7  С. ПЕТЕРБУРГ. ВЪ ТИПОГРАфІИ А. БОРОДИНА И КОМП. 1842.
        front.appendChild(meta)
        meta.appendChild(
            root.createTextNode(pge.getText("text").split('\n')[8] + ' ' + pge.getText("text").split('\n')[9]))
    #if i == 4:
        page = root.createElement("pb")
        front.appendChild(page)
        page.appendChild(root.createTextNode(str(i)))
        #оглавление
        contents = root.createElement("contents")
        front.appendChild(contents)
        contents.appendChild(
            root.createTextNode(pge.getText("text").replace('\n', ' ').replace('-  ', '')))
        # примечание редактора
        edit_notes = root.createElement("edit_notes_title")
        front.appendChild(edit_notes)
        edit_notes.appendChild(
            root.createTextNode(pge.getText("text").split('\n')[2] + pge.getText("text").split('\n')[4] +
                                pge.getText("text").split('\n')[5]))
        # примечание редактора: сам текст
        edit = root.createElement("edit_notes")
        front.appendChild(edit)
        edit.appendChild(
            root.createTextNode(pge.getText("text").replace('\n', ' ').replace('-  ', '')))
        # год, если есть: ГОДЪ ЧЕТВЕРТЫЙ
        year = root.createElement("year")
        front.appendChild(year)
        year.appendChild(root.createTextNode(pge.getText("text").split('\n')[1]))
    #if i == 5:
        page = root.createElement("pb")
        front.appendChild(page)
        page.appendChild(root.createTextNode(str(i)))
        # цензоры
        censors = root.createElement("censorship_approval") # Печатать позволяется
        front.appendChild(censors)
        censors.appendChild(root.createTextNode(pge.getText("text").replace('\n', ' ')))
    #if i == 6:
        page = root.createElement("pb")
        body.appendChild(page)
        page.appendChild(root.createTextNode(str(i)))
        # заголовки и журнальный номер страницы. 
        head = root.createElement("head")
        body.appendChild(head)
        head.appendChild(root.createTextNode(
            pge.getText("text").split('\n')[0] + ' ' + pge.getText("text").split('\n')[1] + ' ' +
            pge.getText("text").split('\n')[2] + ' ' + pge.getText("text").split('\n')[3] + ' '))
        # текст
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
        p.appendChild(root.createTextNode(pge.getText("text").replace('\n', ' ').replace('-  ', '')))
    if i > 1058:
        p = root.createElement("p")
        body.appendChild(p)
        p.appendChild(root.createTextNode(pge.getText("text").replace('\n', ' ').replace('-  ', '')))
    i += 1
xml_str = root.toprettyxml('\t') #тело готового xml
save_path = ("corrected.xml")
#with open(save_path, "w", encoding="utf-8") as f: сохраняем в документ
#    f.write(xml_str)
    
#КОД, ЕСЛИ В ТОМЕ ЕСТЬ INDEXERROR ИЗ-ЗА ПУСТЫХ СТРАНИЦ (ПРОЩЕ ИХ УДАЛИТЬ)
#ТЕЛО ЦИКЛА
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
