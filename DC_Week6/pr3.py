FREQ_START = 512
FREQ_STEP = 128
HEX_LIST = ['0', '1', '2', '3', '4',
            '5', '6', '7', '8', '9',
            'A', 'B', 'C', 'D', 'E',
            'F']
HEX = set(HEX_LIST)

rules = {}
print('Frequency Rules:')
rules['START'] = FREQ_START
for i in range(len(HEX_LIST)):
    h = HEX_LIST[i]
    rules[h] = FREQ_START + FREQ_STEP + FREQ_STEP*(i+1)
rules['END'] = FREQ_START + FREQ_STEP + FREQ_STEP*(len(HEX_LIST)) + FREQ_STEP*2

for k, v in rules.items():
    print(f'{k}: {v}')
