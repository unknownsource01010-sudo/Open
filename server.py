from flask import Flask,request,jsonify,send_from_directory
from urllib.parse import quote_plus,urlparse
import re,requests
from bs4 import BeautifulSoup
app=Flask(__name__,static_folder='.')
SOURCES={
 'Walmart':'https://www.walmart.com/search?q={q}', 'Home Depot':'https://www.homedepot.com/s/{q}',
 'Lowes':'https://www.lowes.com/search?searchTerm={q}', 'eBay':'https://www.ebay.com/sch/i.html?_nkw={q}',
 'Target':'https://www.target.com/s?searchTerm={q}', 'Best Buy':'https://www.bestbuy.com/site/searchpage.jsp?st={q}',
 'Ace':'https://www.acehardware.com/search?query={q}', 'Menards':'https://www.menards.com/main/search.html?search={q}',
 'Tractor Supply':'https://www.tractorsupply.com/tsc/search/{q}', 'Harbor Freight':'https://www.harborfreight.com/search?q={q}',
 'Google Shopping':'https://www.google.com/search?tbm=shop&q={q}' }
UA={'User-Agent':'Mozilla/5.0 PromoProwler/7.0'}
PRICE=re.compile(r'\$\s*([0-9]{1,5}(?:,[0-9]{3})*(?:\.\d{2})?)')
COUPON=re.compile(r'(?i)(?:code|coupon|promo)\s*[:\-]?\s*([A-Z0-9][A-Z0-9_-]{3,20})')
def safe_url(u):
 try:return urlparse(u).scheme in ('http','https')
 except:return False
@app.get('/')
def home():return send_from_directory('.', 'index.html')
@app.post('/api/search')
def search():
 q=(request.json or {}).get('q','').strip(); out=[]
 if not q:return jsonify({'offers':[]})
 for merchant,tpl in SOURCES.items():
  u=tpl.format(q=quote_plus(q))
  try:
   r=requests.get(u,headers=UA,timeout=8); txt=BeautifulSoup(r.text,'html.parser').get_text(' ',strip=True)
   vals=[float(x.replace(',','')) for x in PRICE.findall(txt)[:80]]
   vals=[x for x in vals if .01<x<100000]
   if vals: out.append({'merchant':merchant,'product':q,'price':min(vals),'shipping':None,'tax':None,'discount':0,'code':'','codeStatus':'unverified','url':u,'sourceStatus':'live-page-observed'})
   else: out.append({'merchant':merchant,'product':q,'price':None,'shipping':None,'tax':None,'discount':0,'code':'','codeStatus':'unverified','url':u,'sourceStatus':'search-link-only'})
  except Exception: out.append({'merchant':merchant,'product':q,'price':None,'shipping':None,'tax':None,'discount':0,'code':'','codeStatus':'unverified','url':u,'sourceStatus':'blocked-or-unavailable'})
 return jsonify({'offers':out})
@app.post('/api/promos')
def promos():
 data=request.json or {}; merchant=data.get('merchant',''); product=data.get('product',''); urls=data.get('urls',[]); found=[]
 queries=[f'https://www.google.com/search?q={quote_plus(merchant+" "+product+" promo code coupon")}',f'https://www.google.com/search?q={quote_plus(merchant+" coupon code") }']
 for u in list(urls)+queries:
  if not safe_url(u):continue
  try:
   t=BeautifulSoup(requests.get(u,headers=UA,timeout=8).text,'html.parser').get_text(' ',strip=True)
   for c in COUPON.findall(t):
    if c.upper() not in {x['code'] for x in found}:found.append({'code':c.upper(),'status':'candidate','source':u})
  except:pass
 return jsonify({'codes':found[:30]})
@app.post('/api/verify')
def verify():
 # Retailers differ; no fake verification. Browser/manual checkout evidence can mark a code verified.
 d=request.json or {}; evidence=d.get('evidence','').strip(); discount=float(d.get('discount') or 0)
 ok=bool(evidence and discount>=0)
 return jsonify({'verified':ok,'status':'verified-from-checkout-evidence' if ok else 'needs-checkout-verification'})
@app.post('/api/rank')
def rank():
 offers=(request.json or {}).get('offers',[])
 for o in offers:
  p=o.get('price'); s=o.get('shipping'); t=o.get('tax'); d=o.get('discount') or 0
  o['deliveredTotal']=round(float(p)+float(s or 0)+float(t or 0)-float(d),2) if p is not None else None
 offers.sort(key=lambda x:(x.get('deliveredTotal') is None,x.get('deliveredTotal') or 1e99))
 return jsonify({'offers':offers})
if __name__=='__main__':app.run(host='127.0.0.1',port=8787)
