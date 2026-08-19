with open('report.py', 'r') as f:
    code = f.read()

code = code.replace(
'''    try:
        ib.connect('127.0.0.1', 7497, clientId=999)''',
'''    import random
    try:
        ib.connect('127.0.0.1', 7497, clientId=random.randint(2000, 9000))'''
)

with open('report.py', 'w') as f:
    f.write(code)
