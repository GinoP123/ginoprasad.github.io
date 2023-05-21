#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import subprocess as sp
import yaml
import shutil


# # Convert notebooks to html

# In[11]:


os.chdir('/Users/ginoprasad/ginoprasad.github.io')


# In[12]:


metadata_path = 'metadata.yaml'


# In[13]:


with open(metadata_path) as infile:
    metadata = yaml.safe_load(infile)


# In[14]:


for project_notebook_path in metadata['Projects'][:]:
    if not os.path.exists(project_notebook_path):
        print(f"REMOVING {project_notebook_path}")
        metadata['Projects'].remove(project_notebook_path)
        with open(metadata_path, 'w') as outfile:
            yaml.dump(metadata, outfile, default_flow_style=False)
        


# In[15]:


metadata


# In[16]:


temp_path = f'{os.getcwd()}/projects/temp.html'


# In[17]:


max_base_filename_length = 50


# In[19]:


temp_path


# In[20]:


project_notebook_path


# In[18]:


project_names, project_paths = [], []
for project_notebook_path in metadata['Projects']:
    print(f"Converting {project_notebook_path}")
    sp.run(f"jupyter nbconvert --to html '{project_notebook_path}' --output '{temp_path}'", shell=True)
    
    with open(temp_path) as infile:
        lines = infile.readlines()

    title_line = sp.run(f"grep '<h1' '{temp_path}'", shell=True, capture_output=True).stdout.decode().split('\n')[0]
    project_name = title_line[title_line.index('>')+1:]
    project_name = project_name[:project_name.index('<')]
    print(f'Project Name: {project_name}')

    project_base_path = os.path.basename(project_notebook_path)[:-len('.ipynb')]
    while len(project_base_path) > max_base_filename_length:
        project_base_path = ' '.join(project_base_path.split(' ')[:-1])
    title = ' '.join(map(lambda x: x[0].upper() + x[1:] if x else x, project_base_path.split('_')))
    lines[5] = lines[5][:len('<title>')] + title + lines[5][lines[5].index('</title>'):]
 
    with open(temp_path, 'w') as outfile:
        lines.insert(5, '<link rel="icon" href="../docs/assets/logo.png"><iframe src="../header.html" style="height: 17rem; width: 100%" frameborder="0" scrolling="no"></iframe>\n')
        outfile.write(''.join(lines))
    
    if not project_base_path:
        print(f"\n\n\n\n\tWarning: Project '{project_name}' Name exceeds recommended length\n\n\n\n")
        project_base_path = project_name
    print(f'Project Path: {project_base_path}')
    project_path = f'{os.getcwd()}/projects/{project_base_path}.html'
    
    assert project_path not in project_paths
    os.rename(temp_path, project_path)
    
    project_names.append(project_name)
    project_paths.append(project_path)
    print('\n')


# In[10]:


index_html_path = 'index.html'


# In[11]:


index_html_lines = open(index_html_path).readlines()


# In[12]:


project_list_index_start = index_html_lines.index('\t\t<ul>\n') + 1
project_list_index_end = index_html_lines.index('\t\t</ul>\n')


# In[13]:


new_project_list =  [f'\t\t\t<li><a href="projects/{os.path.basename(html_path)}">{name}</a></li>\n' for name, html_path in zip(project_names, project_paths)]


# In[14]:


new_project_list


# In[15]:


index_html_lines = index_html_lines[:project_list_index_start] + new_project_list + index_html_lines[project_list_index_end:]


# # Copying CV and Updating Links

# In[16]:


assert shutil.copy(metadata['CV'], f"projects/{os.path.basename(metadata['CV'])}")


# In[17]:


index_html_lines


# In[18]:


tag_dict = {tag: metadata[tag] for tag in ['CV', 'LinkedIn', 'GitHub']}
tag_dict['CV'] = f"projects/{os.path.basename(tag_dict['CV'])}"


# In[19]:


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

# In[20]:


with open(index_html_path, 'w') as outfile:
    outfile.write(''.join(index_html_lines))


# In[21]:


sp.run(f"cd '{os.getcwd()}'; git add .; git commit -m 'Automated Website Update'; git push origin main", shell=True)


# # Updating Python Script

# In[22]:


if hasattr(__builtins__,'__IPYTHON__'):
    sp.run(f"jupyter nbconvert --to script 'update_website.ipynb' --output 'update_website'", shell=True)


# In[ ]:




