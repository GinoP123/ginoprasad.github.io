#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import glob
import subprocess as sp
import yaml
import shutil
from tqdm import tqdm
import numpy as np
import datetime
import re


# # Convert notebooks to html

# In[2]:


os.chdir('/Users/ginoprasad/ginoprasad.github.io')
index_html_path = 'index.html'
header_html_path = 'header.html'
metadata_path = 'metadata.yaml'
temp_path = f'{os.getcwd()}/projects/temp.html'
max_base_filename_length = 50


# In[78]:


with open(metadata_path) as infile:
    metadata = yaml.safe_load(infile)


# In[4]:


for project_notebook_path in metadata['Projects'][:]:
    if not os.path.exists(project_notebook_path):
        print(f"REMOVING {project_notebook_path}")
        metadata['Projects'].remove(project_notebook_path)
        with open(metadata_path, 'w') as outfile:
            yaml.dump(metadata, outfile, default_flow_style=False)


# In[7]:


def get_notebook_metadata(project_notebook_path):
    notebook_metadata_str = sp.run(f"head -n 200 '{project_notebook_path}'", shell=True, capture_output=True).stdout.decode().split('\n')
    notebook_metadata_str = ''.join(notebook_metadata_str[notebook_metadata_str.index('   "source": [')+1:notebook_metadata_str.index('   ]')])
    
    notebook_metadata = {}
    notebook_metadata['title'] = re.search('(?<=# ).*?(?<=\\\\n)', notebook_metadata_str).group(0)[:-2]
    notebook_metadata['authors'] = re.search('(?<=#### ).*?(?<=\\\\n)', notebook_metadata_str).group(0)[:-2]
    notebook_metadata['date'] = re.search('[0-9][0-9]/[0-9][0-9]/[0-9][0-9][0-9][0-9]', notebook_metadata_str).group(0)
    
    return notebook_metadata


# In[8]:


project_names, project_paths, project_dates = [], [], []
for project_notebook_path in tqdm(metadata['Projects']):
    notebook_metadata = get_notebook_metadata(project_notebook_path)    
    project_base_path = os.path.basename(project_notebook_path)[:-len('.ipynb')]

    while len(project_base_path) > max_base_filename_length:
        project_base_path = ' '.join(project_base_path.split(' ')[:-1])
    if not project_base_path:
        print(f"\n\n\n\n\tWarning: Project '{notebook_metadata['title']}' Name exceeds recommended length\n\n\n\n")
        project_base_path = notebook_metadata['title']
    notebook_metadata['project_path'] = f'{os.getcwd()}/projects/{project_base_path}.html'
    
    assert notebook_metadata['project_path'] not in project_paths
    project_names.append(notebook_metadata['title'])
    project_paths.append(notebook_metadata['project_path'])
    project_dates.append(notebook_metadata['date'])
    
    if os.path.exists(notebook_metadata['project_path']) and os.path.getmtime(notebook_metadata['project_path']) > os.path.getmtime(project_notebook_path):
        continue
    
    print(project_base_path)
    print(f"Converting {project_notebook_path}")
    sp.run(f"jupyter nbconvert --to html '{project_notebook_path}' --output '{temp_path}'", shell=True)
    print(f"Project Name: {notebook_metadata['title']}")

    with open(temp_path) as infile:
        lines = infile.readlines()


    title = ' '.join(map(lambda x: x[0].upper() + x[1:] if x else x, project_base_path.split('_')))
    lines[5] = lines[5][:len('<title>')] + title + lines[5][lines[5].index('</title>'):]
 
    with open(temp_path, 'w') as outfile:
        lines.insert(5, '<link rel="icon" href="../docs/assets/logo.png"><iframe src="../header.html" style="height: 12rem; width: 100%" frameborder="0" scrolling="no"></iframe>\n')
        outfile.write(''.join(lines))
    os.rename(temp_path, notebook_metadata['project_path'])
    
    print('\n')

datetimes = [datetime.datetime.strptime(project_date, '%m/%d/%Y') for project_date in project_dates]
sort_list = lambda ls: [y[1] for y in sorted(enumerate(ls), key=lambda x: datetimes[x[0]], reverse=True)]
project_names, project_paths, project_dates = map(sort_list, (project_names, project_paths, project_dates))
[os.remove(x) for x in glob.glob(f'{os.getcwd()}/projects/*') if x not in project_paths]
None


# In[91]:


with open(index_html_path) as infile:
    index_html_lines = infile.readlines()


# In[87]:


project_template = "\t\t\t<li><div class=link><a href=\"projects/{}\">{}</a></div><div class='date'><img src='docs/assets/calendar_icon.png'><span class=date>{}</span></div></li>\n"

project_list_index_start = ["Cool Projects" in x for x in index_html_lines].index(True) + 2
project_list_index_end = index_html_lines[project_list_index_start:].index('\t\t</ul>\n') + project_list_index_start

new_project_list =  [project_template.format(os.path.basename(html_path), name, date) for name, html_path, date in zip(project_names, project_paths, project_dates)]
index_html_lines = index_html_lines[:project_list_index_start] + new_project_list + index_html_lines[project_list_index_end:]
index_html_lines[project_list_index_start-2] = re.sub("(?<=\\().*?(?=\\))",  str(len(metadata['Projects'])), index_html_lines[project_list_index_start-2])


# In[66]:


with open(index_html_path, 'w') as outfile:
    outfile.write(''.join(index_html_lines))


# # Copying CV and Updating Links

# In[79]:


assert shutil.copy(metadata['CV'], f"projects/{os.path.basename(metadata['CV'])}")


# In[80]:


tag_dict = {tag: metadata[tag] for tag in ['CV', 'LinkedIn', 'GitHub', 'GoogleScholar', 'ORCID']}
tag_dict['CV'] = f"projects/{os.path.basename(tag_dict['CV'])}"
tag_dict['Logo'] = metadata['DomainLink']


# In[81]:


with open("header.html") as infile:
    header_html_string = infile.read()


# In[82]:


for tag_name, tag_value in tag_dict.items():
    header_html_string = re.sub(f"(?<=<a id='{tag_name}' href=').*?(?='>)", tag_value, header_html_string)


# In[83]:


with open("header.html", 'w') as outfile:
    outfile.write(header_html_string)


# # Writing Updated Index File

# In[17]:


sp.run(f"cd '{os.getcwd()}'; git add .; git commit -m 'Automated Website Update'; git push origin main", shell=True)


# # Updating Python Script

# In[16]:


if hasattr(__builtins__,'__IPYTHON__'):
    sp.run(f"jupyter nbconvert --to script 'update_website.ipynb' --output 'update_website'", shell=True)


# In[ ]:




