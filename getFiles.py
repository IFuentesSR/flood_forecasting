import urllib
import requests
import os
import re
from zipfile import ZipFile

# Queensland
url = 'https://water-monitoring.information.qld.gov.au/cgi/webhyd.pl?co={}&t=rscf_org&v=140.00_141.00_ATQ&vn=Stream%20Discharge&ds=ATQ&p=All%20data,18000101000000,18000101000000,period,1&pp=&r=rate&o=Download,download&i=All%20points,Point,1&catid=rs&1565759657186'
urlMonthly = 'https://water-monitoring.information.qld.gov.au/cgi/webhyd.pl?co={}&t=rscf_org&v=140.00_141.00_ATQ&vn=Stream%20Discharge&ds=ATQ&p=All%20data,18000101000000,18000101000000,period,1&pp=&r=rate&o=Download,download&i=Monthly,Month,1&catid=rs&1568522232936'
with open('QueenslandFile.txt') as txt:
    file = txt.read()
allStations = re.findall(r'\d{6}\\*[A-Z]', file)
stations = list(set(allStations))

for file in stations:
    try:
        url2 = requests.get(urlMonthly.format(file)).content
        url2 = url2.decode()
        urllib.request.urlretrieve(url2[11:-2], 'monthly/{}.zip'.format(file))
    except:
        print(file)


# NSW
urlNSW = 'https://realtimedata.waternsw.com.au/cgi/webhyd.pl?co={}&t=rscf_org&v=100.00_141.00_CP&vn=Discharge%20Rate&ds=CP&p=All%20data,18000101000000,18000101000000,period,1&pp=0&r=rate&o=Download,download&i=All%20points,Point,1&catid=rs&1565760526658'
urlNSWMonthly = 'https://realtimedata.waternsw.com.au/cgi/webhyd.pl?co={}&t=rscf_org&v=100.00_141.00_CP&vn=Discharge%20Rate&ds=CP&p=All%20data,18000101000000,18000101000000,period,1&pp=0&r=rate&o=Download,download&i=Monthly,Month,1&catid=rs&1568522691356'
with open('NSWStations.txt') as txt:
    file = txt.read()
allStations = list(set(re.findall(r'\d{6}', file)))

fails = []
for file in allStations:
    try:
        url2 = requests.get(urlNSWMonthly.format(file)).content
        url2 = url2.decode()
        urllib.request.urlretrieve(url2[-96:-2], 'monthly/{}.zip'.format(file))
    except:
        fails.append(file)
        print(file)
        continue


# Victoria
urlVic = 'http://data.water.vic.gov.au/cgi/webhyd.pl?co={}&t=rscf_org&v=100.00_141.00_PUBLISH&vn=Stream%20Discharge%20(Ml/d)&ds=PUBLISH&p=All%20data,18000101000000,18000101000000,period,1&pp=0&r=rate&o=Download,download&i=All%20points,Point,1&catid=rs&1565761752339'

with open('VictoriaStations.txt') as txt:
    file = txt.read()
allStations = re.findall(r'\d{6}', file)
stations = list(set(allStations))

fails = []
for file in stations:
    try:
        url2 = requests.get(urlVic.format(file)).content
        url2 = url2.decode()
        urllib.request.urlretrieve(url2[11:-2], '{}.zip'.format(file))
    except:
        fails.append(file)
        print(file)

# unziping files
zipFiles = [n for n in os.listdir(os.path.join(os.getcwd(), 'monthly')) if n.endswith('.zip')]
for n in zipFiles:
    with ZipFile('monthly/{}'.format(n), 'r') as zip:
        zip.extractall(path=os.path.join(os.getcwd(), 'monthly'))
