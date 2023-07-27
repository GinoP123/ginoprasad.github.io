#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import subprocess as sp
import yaml
import shutil
from tqdm import tqdm


# # Convert notebooks to html

# In[2]:


os.chdir('/Users/ginoprasad/ginoprasad.github.io')


# In[3]:


metadata_path = 'metadata.yaml'
with open(metadata_path) as infile:
    metadata = yaml.safe_load(infile)


# In[4]:


for project_notebook_path in metadata['Projects'][:]:
    if not os.path.exists(project_notebook_path):
        print(f"REMOVING {project_notebook_path}")
        metadata['Projects'].remove(project_notebook_path)
        with open(metadata_path, 'w') as outfile:
            yaml.dump(metadata, outfile, default_flow_style=False)


# In[5]:


temp_path = f'{os.getcwd()}/projects/temp.html'


# In[6]:


max_base_filename_length = 50


# In[7]:


temp_path


# In[8]:


project_notebook_path


# In[9]:


project_names, project_paths = [], []
for project_notebook_path in tqdm(metadata['Projects']):
    title_line = sp.run(f"head -n 200 '{project_notebook_path}'", shell=True, capture_output=True).stdout.decode().split('\n')
    title_line = title_line[title_line.index('   "source": [') + 1]
    project_name = title_line.strip().lstrip('"# ').replace('"', '')
    if project_name[-3:] == '\\n,':
        project_name = project_name[:-3]
    project_name = project_name.strip()
    
    project_base_path = os.path.basename(project_notebook_path)[:-len('.ipynb')]
    while len(project_base_path) > max_base_filename_length:
        project_base_path = ' '.join(project_base_path.split(' ')[:-1])
    if not project_base_path:
        print(f"\n\n\n\n\tWarning: Project '{project_name}' Name exceeds recommended length\n\n\n\n")
        project_base_path = project_name
    project_path = f'{os.getcwd()}/projects/{project_base_path}.html'
    
    assert project_path not in project_paths
    project_names.append(project_name)
    project_paths.append(project_path)
    
    if os.path.getmtime(project_path) > os.path.getmtime(project_notebook_path):
        continue
    
    print(project_base_path)
    print(f"Converting {project_notebook_path}")
    sp.run(f"jupyter nbconvert --to html '{project_notebook_path}' --output '{temp_path}'", shell=True)
    print(f'Project Name: {project_name}')

    with open(temp_path) as infile:
        lines = infile.readlines()


    title = ' '.join(map(lambda x: x[0].upper() + x[1:] if x else x, project_base_path.split('_')))
    lines[5] = lines[5][:len('<title>')] + title + lines[5][lines[5].index('</title>'):]
 
    with open(temp_path, 'w') as outfile:
        lines.insert(5, '<link rel="icon" href="../docs/assets/logo.png"><iframe src="../header.html" style="height: 12rem; width: 100%" frameborder="0" scrolling="no"></iframe>\n')
        outfile.write(''.join(lines))
    os.rename(temp_path, project_path)
    
    print('\n')


# In[10]:


project_names


# In[11]:


index_html_path = 'index.html'
index_html_lines = open(index_html_path).readlines()


# In[12]:


publications_list_index_start = ["Publications" in x for x in index_html_lines].index(True) + 2
publications_list_index_end = index_html_lines[publications_list_index_start:].index('\t\t</ul>\n') + publications_list_index_start

publications_list = []
for publication in metadata['Publications']:
    name = publication['name']
    publications_list.append(f'\t\t\t<li>\n\t\t\t\t<p>{name}<p>\n\t\t\t\t<h3>&emsp;&emsp;{publication["journal"]}</h3>\n\t\t\t\t&emsp;&emsp;&emsp;&emsp;<a href="{publication["doi"]}">{publication["doi"]}</a>\n\t\t\t</li>\n')
index_html_lines = index_html_lines[:publications_list_index_start] + publications_list + index_html_lines[publications_list_index_end:]


# In[13]:


project_list_index_start = ["Cool Projects" in x for x in index_html_lines].index(True) + 2
project_list_index_end = index_html_lines[project_list_index_start:].index('\t\t</ul>\n') + project_list_index_start

new_project_list =  [f'\t\t\t<li><a href="projects/{os.path.basename(html_path)}">{name}</a></li>\n' for name, html_path in zip(project_names, project_paths)]
index_html_lines = index_html_lines[:project_list_index_start] + new_project_list + index_html_lines[project_list_index_end:]
index_html_lines[project_list_index_start-2] = f"\t\t<h2> Cool Projects ({len(metadata['Projects'])}) </h2>\n"


# # Copying CV and Updating Links

# In[14]:


assert shutil.copy(metadata['CV'], f"projects/{os.path.basename(metadata['CV'])}")


# In[15]:


tag_dict = {tag: metadata[tag] for tag in ['CV', 'LinkedIn', 'GitHub']}
tag_dict['CV'] = f"projects/{os.path.basename(tag_dict['CV'])}"


# In[16]:


for i, line in enumerate(index_html_lines):
    for tag in tag_dict:
        prefix = f"<a id='{tag}' href='"
        if line.startswith(prefix):
            print(line.strip())
            new_line = prefix + tag_dict[tag] + line[len(prefix) + line[len(prefix):].index("'"):]
            print(new_line)
            index_html_lines[i] = new_line
    
    if line.startswith(prefix):
        del tag_dict[tag]


# # Writing Updated Index File

# In[17]:


with open(index_html_path, 'w') as outfile:
    outfile.write(''.join(index_html_lines))


# In[18]:


sp.run(f"cd '{os.getcwd()}'; git add .; git commit -m 'Automated Website Update'; git push origin main", shell=True)


# # Updating Python Script

# In[19]:


if hasattr(__builtins__,'__IPYTHON__'):
    sp.run(f"jupyter nbconvert --to script 'update_website.ipynb' --output 'update_website'", shell=True)


# In[ ]:




