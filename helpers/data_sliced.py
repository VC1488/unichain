data = ''

sig = data[:10]
print(sig)
data = data[10:]
while data:
    new_data = data[:64]
    print(new_data)
    data = data[64:]