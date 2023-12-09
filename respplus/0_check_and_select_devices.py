#%%
import sounddevice as dev
from pprint import pprint as print
import pandas as pd

#%%
device_list = dev.query_devices()
print(device_list)

#%%
#for host_api in  dev.query_hostapis():
#    print(host_api)

#%%
props = list()
for device_number in range(len(device_list)): #dev.default.device:
    props.append(device_list[device_number])
df = pd.DataFrame(props)
df.set_index('index')
# %% デバイス選択
dev.default.device = [4,5]

