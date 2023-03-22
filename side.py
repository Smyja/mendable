import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

base_url = 'https://wiki.thrivedx.com'
requests.packages.urllib3.disable_warnings()
response = requests.get(base_url, verify=False)
soupi = BeautifulSoup(response.content, 'html.parser')
toc = soupi.find('div', {'id': 'dw__toc'})
toc.extract()
links = []
list_items = soupi.find_all('li', {'class': 'level1'})
for li in list_items:
    link = li.find('a')
    if link:
        href = link.get('href')
        links.append(urljoin(base_url, href))

output_list = []
for i,link in enumerate(links):
    response = requests.get(link, verify=False)
    # create Beautiful Soup object
    soup = BeautifulSoup(response.text, 'html.parser')

    # find and extract the table of contents section
    toc = soup.find('div', {'id': 'dw__toc'})
    if toc:
        toc.extract()
    else:
        pass

    # Find the main content section and extract its text
    main_content = soup.find('div', {'class': 'page group'})

    # find all images and replace them with markdown
    for img in main_content.find_all('img'):
        img_parent = img.parent
        title= img_parent.get('title', '') 
        img.replace_with(f"![{title}]({base_url}{img.get('src')})")

    # find all links and replace them with markdown
    for a in main_content.find_all('a'):
        if a.find('img'): # skip links that contain an 'img' tag
            continue
        elif a.get('href', '').endswith(('.png', '.jpg', '.jpeg', '.gif')): # skip image links
            continue
        a.replace_with(f"[{a.text}]({a.get('href')})")

    main_content_markdown = str(main_content).strip()

    # get the rest of the text as normal text
    rest_text = soup.get_text().replace(main_content_markdown, '').strip()
    text = re.sub('\s+', ' ', rest_text)
    output_list.append({'id': i+1, 'source': link, 'content': text})

# write the output to a json file
with open('output.json', 'w', encoding='utf-8') as f:
    f.write(str(output_list))
