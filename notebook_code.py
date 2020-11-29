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

# %%
for i in range(a):
    print(i)

# %%
print('asdf')

# %%
data = {
    'a': np.random.randint(0, 100, 20),
    'b': np.random.randint(0, 100, 20)
}

df = pd.DataFrame(data=data)
df.plot()

# %%
outputs = {'a': a, 'b': b}
artifacts = {'x': np.random.randint(0, 100, 20)}
