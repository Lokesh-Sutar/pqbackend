import requests

url = 'http://localhost:8000/api/chat'
prompt = 'Find me information about Nvidia, Apple. I want to invest in those companies so tell me when should I jump in.'

with requests.get(url, params={'prompt': prompt}, stream=True) as resp:
    if resp.status_code != 200:
        print('Error:', resp.status_code)
    else:
        for chunk in resp.iter_lines(decode_unicode=True):
            if chunk:
                print()
                print(chunk, end='', flush=True)

print('\n--- stream ended ---')
