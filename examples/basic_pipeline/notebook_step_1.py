# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.6.0
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% tags=["parameters"]
a = 11
b = 10

# %%
print(a)

# %% [markdown]
# ### Titanic dataset features summary
    
# %%
import pandas as pd
train_df = pd.read_csv('https://raw.githubusercontent.com/kubeflow-kale/examples/master/titanic-ml-dataset/data/train.csv')

# %%
train_df.describe()

# %% [markdown]
# #### Passengers age
    
# %%
_ = train_df['Age'].hist()

# %%
import numpy as np

outputs = {'d': a+b, 'e': a/b}
artifacts = {'x': np.random.randint(0, 100, 20)}
metrics = {'accuracy': np.random.randint(0, 100), 'recall': np.random.randint(0, 100)}
