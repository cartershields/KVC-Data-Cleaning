#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# Below you will find a combination of a cleaning script and data summary script for the dataset from 
# Keep Vietnam Clean's (KVC) project regarding waste observations in Vietnam.
# The cleaning script works as an ETL (extract, transform, load) pipeline for a dataset. 
# It ingests the .csv file from Anecdata for the project. 
# The data is then cleaned saved to your device as a new dataset.
# Next, the new dataset is summarized in various pivot tables and summary variables.

# Last updated in May 2023 by Carter Shields (carterishields@gmail.com, cis2af@virginia.edu)
# For best results, run the .ipynb file in a jupyter notebook. 
# When running in jupyter notebook, for each of the following blocks, press the 'run' button above


# In[1]:


# Import necessary packages

import json
import pandas as pd
import os
import numpy as np


# In[ ]:


# Download the dataset to your device using this link: https://www.anecdata.org/projects/view/477/data
# If you know your file path name for the data, enter it when prompted in the 'file_input' block

# If you do not know your file path name, run this next block of code to find it
# Once you press run, it should navigate back to your desktop.
# If it does not, go back to your desktop where you will see a pop-up that let's you navigate to your file
# When you locate the data file, click open. 
# A text box will appear with a box containing words like this:
# <_io.TextIOWrapper name='/Users/cartershields/Desktop/GSVS 4991/ObserveDebris_kinh_t__sinh_th_i_vi_t_nam-2022-12-20_06.28.21.csv' mode='r' encoding='UTF-8'>

# Where you see the word name=, select all the text from the first ' (apostrophe) until the next ' (apostrophe). 
# Copy this text
# Paste when prompted after running the 'file_input' block


# In[ ]:


import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd

app = tk.Tk()

app.title('Tkinter Dialog')
app.geometry('600x350')

text = tk.Text(app, height=12)

text.grid(column=0, row=0, sticky='nsew')

# Function to open the file dialog:

def open_csv_file():
    f = fd.askopenfile(filetypes=[('CSV files', '*.csv')], initialdir="D:/Downloads")
    text.insert('1.0', f)

open_button = ttk.Button(app, text='Open a File', command=open_csv_file)
open_button.grid(sticky='w', padx=250, pady=50)

app.mainloop()


# In[2]:


# When you run this block, you will be prompted to enter the filepath that you just found or already knew
# Press enter after you paste it

file_input = input("Paste the file path of the data set:")


# In[3]:


# This block reads in the csv file from your device using the filename just provided
filename = file_input
df = pd.read_csv(filename, header = 'infer', index_col = 'observation_url')


# In[4]:


# Creating an original summary for the data before cleaning
shape = df.shape

# Number of Observations
print('Number of observations before cleaning = ', shape[0])

# Number of Columns
print('Number of columns before cleaning = ', shape[1])


# In[5]:


# Cleaning dataset as a whole

# Delete observations before April 2022

recent_df = df.loc[(df['observed'] > '2022-03-31')]

# recent_df is a data frame of all observations starting on 2022-04-01

# Deleting columns that are no longer needed after the standardization of variables in 2022. 

df2 = recent_df.drop(['license', 'license_url', 'Metal_(%)', 'Plastic_(%)', 'Furniture_(%)', 
                      'Biodegradable_Organic_(%)', 'Balloons_(%)', 'Electronics_(%)', 'Glass_(%)', 
                      'Medical_Supplies___Personal_Hygiene_(%)', 'Vermin', 'Hazardous_Waste_(%)', 'Smoking_Related_(%)', 
                      'Mixed_Items_(%)', 'Other_(%)', 'Comments', 'Original_User', 'Waste_Container_Volume_(l)', 
                      'Image 1', 'Image 2', 'Image 3', 'Image 4', 'Image 5', 'Image 6', 'Image 7', 'Image 8', 
                      'Image 9', 'Image 10', 'Image 11', 'Image 12', 'Image 13', 'Image 14', 'Image 15', 'Image 16', 
                      'Image 17', 'Image 18', 'Image 19', 'Image 20', 'Image 21', 'Image 22', 'Image 23', 'Image 24', 
                      'Image 25', 'Image 26', 'Image 27', 'Image 28', 'Image 29', 'Image 30', 'Image 31', 'Image 32', 
                      'Image 33', 'Image 34', 'Image 35', 'Image 36', 'Image 37', 'Image 38', 'Image 39', 'Image 40', 
                      'Image 41', 'Image 42', 'Image 43', 'Image 44', 'Image 45'], axis = 1)

# df2 is a data frame of the observations starting on 2022-04-01 with the unnecessary columns removed.

# Change column title because some functions do not like working with parentheses
df2["Waste_Vol_Liters"] = df2['Waste_Volume_(l)']

# Update data frame to only include observations within Vietnam.

# Delete observations that do not contain location data or are not in Vietnam.
# Uses the general range of between 6N and 25N for latitude and 100E and 115E for longitude for Vietnam.
# This assumption is flawed if an observation is taken outside Vietnam but near the borders.

df2 = df2.drop(df2[df2.lat < 6].index) 
df2 = df2.drop(df2[df2.lat > 25].index)
df2 = df2.drop(df2[df2.lng > 115].index)
df2 = df2.drop(df2[df2.lng < 100].index)

# Removing NaN in "What_is_near" and "Special_Hazards" columns to be left blank

df2['What_is_near'] = df2['What_is_near'].replace(np.nan, '0', regex=True)
df2['Special_Hazards'] = df2['Special_Hazards'].replace(np.nan, '0', regex=True)

# Creating new column titled "Unique_ID" that combines id and row_id
# The Unique_ID column allows each child observation to have it's own unique identifier for future analysis.

df2["Unique_ID"] = df2['id'].astype(str) +"."+ df2["row_id"].astype(str)

# Moves Unique_ID from last position to first position in dataframe
cols = list(df2.columns)
cols = [cols[-1]] + cols[:-1]
df2 = df2[cols]


# In[6]:


# Cleaning variables that apply to just parent observations

# Ignore the warning blocks, the code is working properly. The red here is not an error.

# Change single column of special hazards to six binary columns
# Inserts zeros into these columns for all observations
df2['Hypodermic_Needles'] = '0'
df2['Batteries'] = '0'
df2['Paint_solvents_other_chemicals'] = '0'
df2['Vermin'] = '0'
df2['Other_medical_waste'] = '0'
df2['E-waste'] = '0'

# Inserts ones for observations when that specific hazard is present
df2['Hypodermic_Needles'][df2['Special_Hazards'].str.contains("hypodermic needles")] = 1
df2['Batteries'][df2['Special_Hazards'].str.contains("batteries")] = 1
df2['Paint_solvents_other_chemicals'][df2['Special_Hazards'].str.contains("paint, solvents, other chemicals")] = 1
df2['Vermin'][df2['Special_Hazards'].str.contains("vermin (rats, cockroaches, etc.)")] = 1
df2['Other_medical_waste'][df2['Special_Hazards'].str.contains("other medical wastes")] = 1
df2['E-waste'][df2['Special_Hazards'].str.contains("e-waste")] = 1


# Change single column of "what is near" to five binary columns based on if contains feature

# Inserts zeros into these columns for all observations
df2['Cafe'] = '0'
df2['School'] = '0'
df2['Water'] = '0'
df2['Hospital'] = '0'
df2['Park'] = '0'

# Inserts ones for observations when that location type is near
df2['Cafe'][df2['What_is_near'].str.contains("Cafe")] = 1
df2['School'][df2['What_is_near'].str.contains("School")] = 1
df2['Water'][df2['What_is_near'].str.contains("Water")] = 1
df2['Hospital'][df2['What_is_near'].str.contains("Hospital")] = 1
df2['Park'][df2['What_is_near'].str.contains("Park")] = 1

# Ignore the warning blocks, the code is working properly. The red here is not an error.


# In[7]:


# Cleaning variables that apply to just child observations

# Create column for the volume of a specific type of waste in an observation
df2['Type_Liters'] = df2['Waste_Vol_Liters'] * (df2['Waste_Type_Percent_(%)']/100)


# In[8]:


# Creating a summary for the new dataframe
shape_new = df2.shape
print()

# Number of Observations (rows)
print('Number of observations after cleaning = ', shape_new[0])

# Number of Columns
print('Number of columns after cleaning = ', shape_new[1])
print()


# In[10]:


# Choosing an output for the cleaned data to be saved to your device.

# User input either JSON or CSV to write the updated file to a local file.
# Input is case sensitive.
# If user tries to input another file type, it throws an error that loops back to the user needing to input again.

# Cleaned data will be exported to the same directory as where the original data was.

clean_csv = "_CLEANED.csv"
new_csv = filename[:-4] + clean_csv

clean_json = "_CLEANED.json"
new_json = filename[:-4] + clean_json

input_type = input("Enter the file type you would like to output to (CSV or JSON; case sensitive):")

if input_type == 'CSV':
    data = os.path.join(os.getcwd())
    output_file = os.path.join(data, new_csv)
    df2.to_csv(output_file)
    print('File (CSV) outputted as: ' + new_csv)
elif file_type == 'JSON':
    data = os.path.join(os.getcwd())
    output_file = os.path.join(data, new_json)
    df2.to_json(output_file)
    print('File (JSON) outputted as: ' + new_json)
else:
    print('File type not found. Enter either CSV or JSON.')


# In[ ]:


# The following code is the summary for the cleaned dataset. 
# If you only want to clean the dataset, you can stop here. 
# As more observations are added to the dataset, the script can be re-run to see the updated information.


# In[ ]:


# PARENT OBSERVATIONS PIVOT TABLE

# Automated pivot table that shows observations as their whole site (referred to as parent observation):
parent_pivot = df2.pivot_table(index=['id', 'lat', 'lng', 'Illegal_Dumping', 'Foul_Odor', 'Cafe', 'School', 'Water', 
                                      'Hospital', 'Park', 'Hypodermic_Needles', 'Batteries', 
                                      'Paint_solvents_other_chemicals', 'Vermin', 'Other_medical_waste', 'E-waste'], 
                           values=['Waste_Vol_Liters', 'row_id'], 
                           aggfunc={'Waste_Vol_Liters': 'min', 'row_id':'count'})
print(parent_pivot)

# df_pivot acts as a new dataframe of just the entire site observation (parent)
# the pivot table shows the information pertaining to that entire site

# If you are familiar with how pivot tables work in excel and have some basic knowledge of python:
# you can customize the pivot table to include whichever variables are of interest to you
# If you include columns that have NAs, the pivot table will only include the rows that have completed values for all 
# rows in all columns you selected


# In[ ]:


# Save the parent pivot table you made above as a csv to your device

pp_csv = "_PARENT_PIVOT.csv"
pp_title = filename[:-4] + pp_csv

pp_exp = os.path.join(os.getcwd())
output_file_parent_pivot = os.path.join(pp_exp, pp_title)
parent_pivot.to_csv(output_file_parent_pivot)
print('File (CSV) outputted as: ' + pp_title)


# In[ ]:


# CHILD OBSERVATIONS PIVOT TABLE
child_pivot = df2.pivot_table(index=['Unique_ID', 'lat', 'lng', 'Type_Liters'], 
                           values=['Waste_Vol_Liters', 'Waste_Type_Percent_(%)', 'Waste_Type'], 
                           aggfunc={'Waste_Vol_Liters': 'min', 'Waste_Type_Percent_(%)': 'min', 'Waste_Type': 'min'})
print(child_pivot)


# In[ ]:


# Save the child pivot table you made above as a csv to your device

cp_csv = "_CHILD_PIVOT.csv"
cp_title = filename[:-4] + cp_csv

cp_exp = os.path.join(os.getcwd())
output_file_child_pivot = os.path.join(cp_exp, cp_title)
child_pivot.to_csv(output_file_child_pivot)
print('File (CSV) outputted as: ' + cp_title)


# In[ ]:


# Total Volume by Waste Type (using child obs)

# Read in the parent pivot file 

filename_parent_pivot = pp_title
df_pp = pd.read_csv(filename_parent_pivot, header = 'infer', index_col = 'id')


# In[ ]:


total_vol = df_pp['Waste_Vol_Liters'].sum()
type_liters = df2.groupby(["Waste_Type"]).Type_Liters.sum()
type_perc_of_total = round((type_liters / total_vol) *100,2)
vol_big = pd.concat([type_liters, type_perc_of_total], axis=1)

# Issue is it labels both columns as type_liters

# Save the above table as a csv to your device to then be imported back to change column names
# No need to actually use this file for anything

vol_big_csv = "_VOLUME_WRONG_TITLES.csv"
vol_big_title = filename[:-4] + vol_big_csv

vol_big_exp = os.path.join(os.getcwd())
output_file_vol_big = os.path.join(vol_big_exp, vol_big_title)
vol_big.to_csv(output_file_vol_big)

# Read in previous file

filename_vol_big = vol_big_title
df_vb = pd.read_csv(filename_vol_big, header = 'infer', index_col = 'Waste_Type')

# Writes new column titles for this table to then be saved to your device
# This is the file to look at for volume summary

df_vb1 = df_vb.rename(columns={'Type_Liters.1': 'Type_Percent_of_Total_Volume'})
volume_csv = "_VOLUME_SUMMARY.csv"
volume_title = filename[:-4] + volume_csv

volume_exp = os.path.join(os.getcwd())
output_file_volume = os.path.join(volume_exp, volume_title)
df_vb1.to_csv(output_file_volume)
print('File (CSV) outputted as: ' + volume_title)


# In[ ]:


# You can now delete the file that ends in "_VOLUME_WRONG_TITLES.csv" if you would like

