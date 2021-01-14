#coding=utf-8
import requests
import time
import base64
import json

t1 = time.time()
s = requests
text = '李明的颜色情感,色情'
data={'text':text}
r = s.post('http://0.0.0.0:8875/findsensitivewords', data)

print(json.loads(r.text))
print('time cost:', time.time() - t1)
