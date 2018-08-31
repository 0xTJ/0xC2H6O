#!/usr/local/bin/python3

import urllib.request
import json
import smtplib
from email.mime.text import MIMEText
import html.parser

baseStr = 'http://lcboapi.com'
formedStr = ''

listCount = 256
emailCount = 32

with open('token.txt', 'r') as tokenFile:
    apiToken=tokenFile.read().replace('\n', '')

def AddHeader(req):
    req.add_header('Authorization', 'Token ' + apiToken)
    return req

req = urllib.request.Request(baseStr + '/products?per_page=100')
req = AddHeader(req)

data = json.load(urllib.request.urlopen(req))
nextPagePath = data['pager']['current_page_path']
pageCount = data['pager']['total_pages']

products = {}

while nextPagePath != None:
    req = urllib.request.Request(baseStr + nextPagePath)
    req = AddHeader(req)
    data = json.load(urllib.request.urlopen(req))
#    print('Processing page ' + str(data['pager']['current_page']) + ' of ' + str(pageCount))
    nextPagePath = data['pager']['next_page_path']
    for item in data['result']:
        if item['inventory_count'] and not item['is_dead'] and not item['is_discontinued'] and item['alcohol_content'] > 0:
            products[item['id']] = item

sortedProducts = sorted(products, key = lambda k: products[k]['price_per_liter_of_alcohol_in_cents'])

for i in range(len(sortedProducts)):
    formedStr += '{:<32}'.format(products[sortedProducts[i]]['name'][:32]) + ' ' + '${:7.2f}'.format(products[sortedProducts[i]]['price_per_liter_of_alcohol_in_cents'] / 10.0)
    if products[sortedProducts[i]]['has_limited_time_offer'] == True:
        formedStr += ' ***SALE***'
    formedStr += '\n'

formedStr = 'Name Price ($/L alc.) [***SALE***]\n\n' + formedStr

print(formedStr)

#if formedStr.count('\n') > emailCount + 1:
#    emailStr = join(formedStr.split('\n')[:emailCount])
#else:
#    emailStr = formedStr

htmlStr = formedStr.encode('ascii', 'xmlcharrefreplace').decode()
htmlStr = htmlStr.replace(' ', '&nbsp;')
htmlStr = htmlStr.replace('\n', '<br />\n')
htmlStr = '<html><body><font face = \'monospace\'>' + htmlStr + '</font></body></html>'

with open('/var/www/0xtj.ca/html/lcbo/index.html', 'rb') as oldFile:
    oldHtmlString = oldFile.read().decode()

if oldHtmlString != htmlStr:
    with open('/var/www/0xtj.ca/html/lcbo/index.html', 'wb') as newFile:
        newFile.write(str.encode(htmlStr))
