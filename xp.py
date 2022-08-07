from cfscrape import create_scraper

SHORTENER = "urlshortx.com"
SHORTENER_API = "8fabf1c36bcaf7fb959b360ac8574f39815ae901"

longurl = input('enter url:')

def short_url(longurl: str) -> str:
     cget = create_scraper().get
     link = cget(f'https://{SHORTENER}/api?api={SHORTENER_API}&url={longurl}&format=text').text
     return link
print(short_url(longurl)) 
