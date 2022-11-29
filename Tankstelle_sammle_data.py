#!/usr/bin/env python
# coding: utf-8

# In[1]:


##importieren benötigter module
from bs4 import BeautifulSoup
import requests
import re
from datetime import datetime
import schedule
import time


##function zum zeitstempel generieren und formatieren
def timestamp():
    #generieren des zeitstempel objekts
    dateTimeObj = datetime.now()
    #wandeln der einzelenen objekte in string
    jahr = str(dateTimeObj.year)
    monat = str(dateTimeObj.month)
    tag = str(dateTimeObj.day)
    stunde = str(dateTimeObj.hour)
    minute = str(dateTimeObj.minute)
    
    #wenn stunde oder minutr nur aus einer Ziffer bestehen dann eine "0" davorsetzten
    if len(stunde) == 1:
        minute_adv = "0" + minute
    else: minute_adv = minute
    
    if len(minute) == 1:
        minute_adv = "0" + minute
    else: minute_adv = minute
    
    #return des formatieren timestamps
    return f"{jahr}_{monat}_{tag} {stunde}.{minute_adv}"
    

##function zum ausführen des Programms in gewünschten zeitabständen
#intervall: zeitabstand in Minuten ; programm: programm welches ausgeführt wird
def repeat(intervall,programm):
    schedule.every(intervall).minutes.do(programm)
    #Loop der schedule immer laufenlässt
    while True:
        #checkt ob eine aufgabe ausgeefürt wird
        schedule.run_pending()
        time.sleep(1)

##function welche alle 4 inputs vergleicht und den kleinsten zurück gibt
def smalest(a,b,c,s):
    w = len(a)
    x = len(b)
    y = len(c)
    z = len(s)
    #checken ob die einzelen ergebniss listen unterschiedlich lang sind und die kürzeste als anzahl der ergebnisse nehemen
    if w <= x and w <= y and w <= z:
        return  w
    elif x <= w and x <= y and x <= z:
        return  x
    elif y <= x and y <= w and y <= z:
        return  y
    else:
        return  z
    
    
##funtion welche das main programm enthält
#item: art des Kraftstoffes: E5 = 7 ; E10 = 5 ; Diesel = 3
def web_scrap_tankstelle():   
    results = 0
    #url auf welcher nach daten gesucht wird mit {item} zum einstellen des gewünschten kraftstoffes und {umkr} zum einstellen des umkreises
    #item: art des Kraftstoffes: E5 = 7 ; E10 = 5 ; Diesel = 3
    item = 7
    umkr = 10
    url = f"https://www.clever-tanken.de/tankstelle_liste?spritsorte=7&r=25&ort=10178+Berlin&lon=13.4709248&lat=52.5041664&sort=p&page=1"
            #https://www.clever-tanken.de/tankstelle_liste?lat=52.5041664&lon=13.4709248&ort=10178+Berlin&spritsorte=3&r=5
    ##laden und übersetz en des textes der url
    seite = requests.get(url).text
    doc = BeautifulSoup(seite, "html.parser")
    
    
    pages_doc = doc.find("span",("class=","page-current text-color-white-gray"))
    pages = int(str(pages_doc).split(">")[1].split("n")[1][1])
    list = [timestamp()]
    for n in range(1,pages,1):
        url_chp = f"https://www.clever-tanken.de/tankstelle_liste?spritsorte=7&r=25&ort=10178+Berlin&lon=13.4709248&lat=52.5041664&page={n}"
        #https://www.clever-tanken.de/tankstelle_liste?lat=52.5041664&lon=13.4709248&ort=10178+Berlin&spritsorte=3&r=5
        ##laden und übersetz en des textes der url
        seite_chp = requests.get(url_chp).text
        soup = BeautifulSoup(seite_chp, "html.parser")
        
        
        #finden der namen aller Tankstellen und speichern in einer liste
        name_doc = soup.find_all("span",("class","fuel-station-location-name"))
        #finden der straßen aller Tankstellen und speichern in einer liste
        straße_doc = soup.find_all("div",("class","fuel-station-location-street"))
        #finden der postleitzahl und des ortes aller tankstellen und speichern in einer liste
        ort_doc = soup.find_all("div",("class","fuel-station-location-city"))
        #finden des preises des gewählten krafstoffes aller tankstellen und speicher in einer liste
        preis_doc = soup.find_all("div",("class","price-text price text-color-ct-blue"))
        #herausfinden der menge an ergebnissen pro kategorie
        #print(name_doc)
        
        #das kleinste der ergebnisse herausfinden
        results_fresh = smalest(name_doc,straße_doc,ort_doc,preis_doc)
        results += results_fresh
        #print(results)
        #timestamp als erstes objekt in liste schreiben
        #list = [timestamp()]
        #results als zwewites objekt in liste schreiben
        #list.append(f"{results}")
        ##for loop zum herauslesen der einzelnen daten wird so oft wiederholt wie ergebnisse vorhanden sind+
        #variablen m,n,o,p sind indexe zum auswählen der gespliteten strings
        for m,n,o,p in zip(range(1,results_fresh*2,2),range(1,results_fresh*2,2),range(1,results_fresh*2,2),range(1,results_fresh*4,4)):
            #speicher den namen der tankstelle als str in einer variablen
            name = str(name_doc).split(">")[m].split("<")[0]
            #speicher die straße der tankstelle als str in einer variablen
            straße = str(straße_doc).split(">")[n].split("<")[0]
            #speicher die postleitzahl und den ort als str in einer variablen
            ort = str(ort_doc).split(">")[o].split("<")[0]
            #speicher den preis der tankstelle in einen str, dann in einen float, + 0.01€ wegen der 0.9 ct pro liter
            preis = float(str(preis_doc).split(">")[p].split("<")[0].replace(" ","")) +0.01
            
            #adresse zusammenfügen
            adresse = straße + ", " + ort
            
            #liste erstllen mit name adresse und preis
            data_list = f"{name},{adresse},{preis}"
            #print(data_list)
            list.append(data_list)
            #erstellte liste an vordefinierte liste anhängen
            #list.append(f"{results}")
        #print(list)
        ##erstellte liste in ein .txt file schreiben
        #.txt file im write modus öffnen
    list.append(f"{results}")
    
    file_name = f"\{timestamp()} data_tankstelle"
    file_directory_begin = r"C:\Users\finnh\Documents\Python_Prj\Tankstelle\Data"
    file_directory = file_directory_begin + file_name
    text_file = open(file_directory,"x")
        #die einzelnen listen einträge einzeln pro zeile in die .txt datei einfügen (vorher in str umwandeln)
    for line in list:
        text_file.write(line)
        text_file.write("\n")
        #.txt datei schließen
    text_file.close()

#web_scrap_tankstelle()    
##ausführen des Programms alle 5 minuten
schedule.every(5).minutes.do(web_scrap_tankstelle)
while True:
    schedule.run_pending()
    time.sleep(1)


