from flask import Flask, render_template, request, redirect
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse

app = Flask(__name__)

BASE_URL = "https://otakudesu.cloud/"

@app.route('/', methods=['GET'])
def index():
    url = requests.get(BASE_URL)
    soup = BeautifulSoup(url.content, 'html.parser')

    def extract_anime_data(section_title):
        anime_list = []
        section = soup.find('h1', text=section_title)
        
        if section:
            anime_ul = section.find_next('div', class_='venz')
            if anime_ul:
                anime_items = anime_ul.find_all('li')
                for anime_li in anime_items:
                    title = anime_li.find('h2', class_='jdlflm').text.strip()
                    episode = anime_li.find('div', class_='epz').text.strip()
                    episode_type = anime_li.find('div', class_='epztipe').text.strip()
                    date_new = anime_li.find('div', class_='newnime').text.strip()
                    img = anime_li.find('img')['src']
                    link = anime_li.find('a')['href']

                    parsed_url = urlparse(link)
                    link_path = parsed_url.path.strip('/')
                    
                    anime_list.append({
                        'Judul Film': title,
                        'Episode': episode,
                        'Tipe Episode': episode_type,
                        'Tanggal Baru': date_new,
                        'Gambar': img,
                        'Link': link_path
                    })
        
        return anime_list

    ongoing_anime = extract_anime_data('On-going Anime')
    complete_anime = extract_anime_data('Complete Anime')

    return render_template("index.html", ongoing=ongoing_anime, complete=complete_anime)

@app.route('/ongoing-anime/', methods=['GET'])
@app.route('/ongoing-anime/page/<int:page_id>/', methods=['GET'])
def on_going(page_id=1):
    current_page = page_id

    url = requests.get(f"{BASE_URL}ongoing-anime/page/{page_id}/")
    soup = BeautifulSoup(url.content, 'html.parser')
    detpost_list = soup.find_all('div', class_='detpost')
    
    data_list = []
    for post in detpost_list:
        jdlflm = post.find('h2', class_='jdlflm').text.strip()
        epz = post.find('div', class_='epz').text.strip()
        epztipe = post.find('div', class_='epztipe').text.strip()
        newnime = post.find('div', class_='newnime').text.strip()
        img = post.find('img')['src']

        full_link = post.find('a')['href']
        parsed_url = urlparse(full_link)
        link_path = parsed_url.path.strip('/')

        data_list.append({
            'Judul Film': jdlflm,
            'Episode': epz,
            'Tipe Episode': epztipe,
            'Tanggal Baru': newnime,
            'Gambar': img,
            'Link': link_path
        })

    # Pagination
    pagination_links = soup.find_all(['a', 'span'], class_='page-numbers')
    pagination_data = []
    for link_tag in pagination_links:
        if link_tag.name == 'a':
            link = link_tag['href']
            parsed_url = urlparse(link)
            last_part = parsed_url.path.strip('/').split('/')[-1] 
            text_content = link_tag.text.strip() 
            pagination_data.append({"last_part": last_part, "text": text_content})
        elif link_tag.name == 'span':
            text_content = link_tag.text.strip()
            pagination_data.append({"last_part": None, "text": text_content})


    return render_template("ongoing-anime.html", ongoing=data_list, pgn=pagination_data, current=str(current_page))

@app.route('/complete-anime/', methods=['GET'])
@app.route('/complete-anime/page/<int:page_id>/', methods=['GET'])
def complete(page_id=1):
    current_page = page_id

    url = requests.get(f"{BASE_URL}complete-anime/page/{page_id}/")
    soup = BeautifulSoup(url.content, 'html.parser')
    detpost_list = soup.find_all('div', class_='detpost')
    data_list = []

    for post in detpost_list:
        jdlflm = post.find('h2', class_='jdlflm').text.strip()
        epz = post.find('div', class_='epz').text.strip()
        epztipe = post.find('div', class_='epztipe').text.strip()
        newnime = post.find('div', class_='newnime').text.strip()
        img = post.find('img')['src']

        full_link = post.find('a')['href']
        parsed_url = urlparse(full_link)
        link_path = parsed_url.path.strip('/')

        data_list.append({
            'Judul Film': jdlflm,
            'Episode': epz,
            'Tipe Episode': epztipe,
            'Tanggal Baru': newnime,
            'Gambar': img,
            'Link': link_path
        })

    # Pagination
    pagination_links = soup.find_all(['a', 'span'], class_='page-numbers')
    pagination_data = []
    for link_tag in pagination_links:
        if link_tag.name == 'a':
            link = link_tag['href']
            parsed_url = urlparse(link)
            last_part = parsed_url.path.strip('/').split('/')[-1] 
            text_content = link_tag.text.strip() 
            pagination_data.append({"last_part": last_part, "text": text_content})
        elif link_tag.name == 'span':
            text_content = link_tag.text.strip()
            pagination_data.append({"last_part": None, "text": text_content})

    return render_template("complete-anime.html", complete=data_list, pgn=pagination_data, current=str(current_page))

@app.route('/anime/<anime_id>', methods=['GET'])
def anime_detail(anime_id):
    url = BASE_URL + "anime/" + anime_id
    # payload = { 'api_key': 'e99555cb7689941638eb271577dfbc7e', 'url': url }
    # response = requests.get('https://api.scraperapi.com/', params=payload)
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    fotoanime_div = soup.find('div', class_='fotoanime')
    image_tag = fotoanime_div.find('img')
    image_url = image_tag['src'] if image_tag else None
    infozingle_div = fotoanime_div.find('div', class_='infozingle')
    info_paragraphs = infozingle_div.find_all('p')
    anime_info = {}
    for p in info_paragraphs:
        key = p.find('b').text.strip()
        value = p.get_text(strip=True).split(':', 1)[1].strip()  # Mengambil teks setelah ":"
        anime_info[key] = value
    genre_links = infozingle_div.find_all('a')
    genres = [genre.text for genre in genre_links]
    anime_info['Image_URL'] = image_url
    anime_info['Genres'] = genres
    sinopsis_div = soup.find('div', class_='sinopc')
    sinopsis = " ".join([p.get_text(strip=True) for p in sinopsis_div.find_all('p')]) if sinopsis_div else None
    anime_info['Sinopsis'] = sinopsis

    # Daftar episode   
    episode_lists = soup.find_all('div', class_='episodelist')
    all_episodes_data = []
    for episode_list in episode_lists:
        title_section = episode_list.find('span', class_='monktit')
        section_title = title_section.get_text(strip=True)
        episodes = episode_list.find_all('li')
        for episode in episodes:
            title = episode.find('a').text
                    
            link = episode.find('a')['href']  
            parsed_url = urlparse(link) 
            link_path = parsed_url.path.strip('/').split('/')[-1] 

            date = episode.find('span', class_='zeebr').text
            episode_dict = {
                "section": section_title,  
                "judul": title,
                "link": link_path,
                "tanggal_rilis": date
            }
            all_episodes_data.append(episode_dict)
    return render_template("anime-detail.html",info=anime_info ,episode=all_episodes_data)


@app.route('/episode/<eps_id>', methods=['GET'])
def episode(eps_id):
    url = BASE_URL + "episode/" + eps_id
    respons = requests.get(url)
    soup = BeautifulSoup(respons.content, 'html.parser')

    iframe_tag = soup.find('iframe')
    iframe_url = iframe_tag['src'] if iframe_tag else None

    if iframe_url:
        return redirect(iframe_url)
    
    return "Video tidak ditemukan", 404

# @app.route("/episode/<eps_id>", methods=['GET'])
# def epsiode(eps_id):
#     url = BASE_URL + "episode/" + eps_id
#     response = requests.get(url)
#     soup = BeautifulSoup(response.content, 'html.parser')
#     def get_video_links(resolution_class):
#         video_links = []
#         ul_element = soup.find('ul', class_=resolution_class)
#         if ul_element:
#             links = ul_element.find_all('a')
#             for link in links:
#                 video_links.append({
#                     'provider': link.text.strip(),
#                     'data_content': link['data-content']
#                 })
#         return video_links
    
#     video_360p = get_video_links('m360p')
#     video_480p = get_video_links('m480p')
#     video_720p = get_video_links('m720p')

#     return video_360p
#     # return render_template("episode.html", video_360p=video_360p, video_480p=video_480p, video_720p=video_720p)

app.run(debug=True)