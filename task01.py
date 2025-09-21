#!/usr/bin/env python
# coding: utf-8

# # 1. Import geospatial data (GeoJSON/CSV with lat-long)

# ### 01.import library

# In[1]:


import pandas as pd


# ### 02.Load dataset

# In[2]:


df = pd.read_csv('covid_19_Global.csv', dtype={"Lat": str, "Long": str})

# Select random 10,000 rows (without replacement)
sample_df = df.sample(n=10000, random_state=42)  

# Save the sampled data
sample_df.to_csv("covid_19_Global_sampled.csv", index=False)

print("Random 10,000 rows selected and saved as covid_19_Global_sampled.csv")


# In[3]:


print(sample_df)


# In[4]:


#data type
sample_df.dtypes


# ### 03.Check for missing values
# 

# In[13]:


sample_df.isnull().sum()


# ### 04.Drop duplicates

# In[9]:


sample_df = df.drop_duplicates()


# ### 05.Convert date to datetime format

# In[10]:


sample_df["Date"] = pd.to_datetime(sample_df["Date"])
sample_df["Date"]


# ### 06.Clean Lat/Long: replace multiple dots and convert to float

# In[14]:


sample_df["Lat"] = sample_df["Lat"].astype(str).str.replace(r"\.", "", regex=True).str.replace(",", ".", regex=True).astype(float) / 1e4
sample_df["Long"] = sample_df["Long"].astype(str).str.replace(r"\.", "", regex=True).str.replace(",", ".", regex=True).astype(float) / 1e4


# ### 07.Saved the cleaned dataframe

# In[15]:


sample_df.to_csv('covid_19_Global_sampled.csv', index=False)
print("Data cleaned and saved successfully!")


# In[ ]:




