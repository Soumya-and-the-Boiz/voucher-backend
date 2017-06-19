
# coding: utf-8

# In[73]:

import pandas as pd
conn = pd.read_csv('final_ranks/Connectivity.csv').set_index('TRACT_ID')['Rank'].to_dict()
tran = pd.read_csv('final_ranks/Transportation.csv').set_index('TRACT_ID')['Rank'].to_dict()
well = pd.read_csv('final_ranks/Wellness.csv').set_index('TRACT_ID')['Rank'].to_dict()
edu = pd.read_csv('final_ranks/Education.csv').set_index('TRACT_ID')['Rank'].to_dict()
categories = [conn, edu, tran, well]


# In[74]:

def get_ranks(tract_ids):
    some_tracts = {}
    i=0
    for tract in tract_ids:
        some_tracts[str(tract)]=[]
        for cat_dict in categories:
            some_tracts[str(tract)].append(cat_dict[tract])
        i+=1
    return some_tracts


# In[75]:

def get_weights(some_tracts):
    avg_sums = [0,0,0,0]
    for i in range(len(categories)):
        for tract in some_tracts.keys():
            avg_sums[i] += some_tracts[tract][i]/len(some_tracts)
    avg_total = sum(avg_sums)
    weights = {}
    return [1 - avgs/float(avg_total) for avgs in avg_sums]


# In[118]:

import operator
def rank_tracts(some_tracts, weights):
    losses = {}
    for big_tract in conn:
        loss = 0
        i=0
        for cat_dict in categories:
            cat_loss=0
            for tract in some_tracts.keys():
                cat_loss += (some_tracts[tract][i]-cat_dict[big_tract])**2
            cat_loss = float(cat_loss)*weights[i]
            loss+=cat_loss
            i+=1
        losses[big_tract]=loss
    return map(lambda x: int(x[0]),sorted(losses.items(), key=operator.itemgetter(1)))


# In[121]:

def predict(tract_ids):
    some_tracts = get_ranks(tract_ids)
    weights = get_weights(some_tracts)
    return rank_tracts(some_tracts,weights)


# In[ ]:
