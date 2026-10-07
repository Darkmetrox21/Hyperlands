import base64, hashlib, hmac, json, time, secrets

def enc(data): return base64.urlsafe_b64encode(data).decode().rstrip('=')
def dec(data): return base64.urlsafe_b64decode(data+'='*(-len(data)%4))
def create_token(payload,key):
    data=dict(payload,nonce=secrets.token_urlsafe(12),issued=int(time.time()))
    body=enc(json.dumps(data,ensure_ascii=False,separators=(',',':')).encode())
    return body+'.'+enc(hmac.new(key.encode(),body.encode(),hashlib.sha256).digest())
def verify_token(token,key):
    if len(token)>16000: raise ValueError('Invitación inválida')
    body,sig=token.split('.',1)
    expected=enc(hmac.new(key.encode(),body.encode(),hashlib.sha256).digest())
    if not hmac.compare_digest(expected,sig): raise ValueError('Firma inválida')
    data=json.loads(dec(body))
    if not isinstance(data,dict) or not isinstance(data.get('name'),str): raise ValueError('Invitación inválida')
    if data.get('expires') and time.time()>int(data['expires']): raise ValueError('Invitación caducada')
    return data
