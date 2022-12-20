#!/usr/bin/env python3
# coding: utf-8

# # Convert notebooks to html

# In[2]:


import pandas as pd
import os
import subprocess as sp


# In[3]:


notebook_list_csv_path = 'csv_files/notebooks_to_add.csv'


# In[4]:


notebook_list = pd.read_csv(notebook_list_csv_path)


# In[5]:


notebook_list['Name']


# In[6]:


output_paths = []
for name, path in zip(notebook_list['Name'], notebook_list['Path']):
    file_base = os.path.splitext(os.path.basename(path))[0]
    output_paths.append(f'{os.getcwd()}/html_files/{file_base}.html')
    print(f"Converting {name}")
    print(f'Output Path: {output_paths[-1]}')
    sp.run(f"jupyter nbconvert --to html '{path}' --output '{output_paths[-1]}'", shell=True)
notebook_list['HTML_Path'] = output_paths


# In[7]:


index_html_path = 'index.html'


# In[8]:


index_html_lines = open(index_html_path).readlines()


# In[9]:


project_list_index_start = index_html_lines.index('<ul>\n') + 1
project_list_index_end = index_html_lines.index('</ul>\n')


# In[11]:


new_project_list =  [f'\t<li><a href="html_files/{os.path.basename(html_path)}">{name}</a></li>\n' for name, html_path in zip(notebook_list['Name'], notebook_list['HTML_Path'])]


# In[12]:


new_project_list


# In[13]:


with open(index_html_path, 'w') as outfile:
    outfile.write(''.join(index_html_lines[:project_list_index_start] + new_project_list + index_html_lines[project_list_index_end:]))


# In[ ]:




