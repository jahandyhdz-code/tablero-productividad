import urllib.request, urllib.error, sys

urls = [
    'https://tablero-productividad-bodega.onrender.com/login',
    'https://render.com',
    'https://api.github.com',
    'https://google.com',
]

for url in urls:
    try:
        r = urllib.request.urlopen(url, timeout=10)
        print(f'OK  ({r.status}) {url}')
    except urllib.error.HTTPError as e:
        print(f'HTTP {e.code}  {url}')
    except Exception as ex:
        print(f'FAIL {type(ex).__name__}: {str(ex)[:60]}  -- {url}')
