from lib.pim_wrapper import PIM
import pandas as pd
from tqdm import tqdm
from datetime import datetime


# Basic Data
print('Timestamp START', datetime.now())
pim_object = PIM()

pim_channel = pim_object.get_channels(name='PIM')
pim_channel_types = pim_object.get_channel_entity_types(pim_channel)

for pim_channel_type in pim_channel_types:
    error = 0
    if pim_channel_type in ['Item', 'Product', 'Resource']:
        print('Fetching data for {0}'.format(pim_channel_type))
        entities = pim_object.get_entities_by_type(pim_channel, pim_channel_type)
        df_all = pd.DataFrame()
        for entity_id in tqdm(entities['entityIds'][:10]):  # take only 10 first items 
            if pim_channel_type == 'Item':
                res = pim_object.get_item_fields(entity_id)
            elif pim_channel_type == 'Product':
                res = pim_object.get_product_fields(entity_id)
            elif pim_channel_type == 'Resource':
                res = pim_object.get_resource_fields(entity_id)
            df_entity = pd.json_normalize(res)
            if df_all.empty:
                df_all = df_entity
            else:
                df_all = df_all.append(df_entity)
        df_all.to_csv("{0}.csv".format(pim_channel_type))

    else:
        print('entityTypeID not supported ({0})'.format(pim_channel_type))
print('Timestamp END', datetime.now())
