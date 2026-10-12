#!/usr/bin/env python3
from bs4 import BeautifulSoup
import re
MORSE = {v:k for k,v in {
'A':'.-','B':'-...','C':'-.-.','D':'-..','E':'.','F':'..-.','G':'--.','H':'....','I':'..','J':'.---','K':'-.-','L':'.-..','M':'--','N':'-.','O':'---','P':'.--.','Q':'--.-','R':'.-.','S':'...','T':'-','U':'..-','V':'...-','W':'.--','X':'-..-','Y':'-.--','Z':'--..',
'0':'-----','1':'.----','2':'..---','3':'...--','4':'....-','5':'.....','6':'-....','7':'--...','8':'---..','9':'----.'}.items()}
soup=BeautifulSoup(open('artifacts/wellspring.html'), 'html.parser')
words=[]
for stanza in soup.select_one('pre').text.strip().split('\n\n'):
    out=''
    for line in stanza.splitlines():
        code=''.join('-' if len(m.group())==3 else '.' for m in re.finditer(r' +',line))
        out += MORSE.get(code, f'[{code}]')
    words.append(out)
print(' '.join(words))
