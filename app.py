import streamlit as st
import requests
import random
import concurrent.futures
import streamlit.components.v1 as components

# --- 1. KONFİGÜRASYON ---
st.set_page_config(
    page_title="Arte Pura",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- TELEGRAM ENTEGRASYONU ---
components.html("""
<script src="https://telegram.org/js/telegram-web-app.js"></script>
<script>
    (function() {
        var viewport = document.querySelector('meta[name="viewport"]');
        if (viewport) {
            viewport.setAttribute('content', 'width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes');
        } else {
            var meta = document.createElement('meta');
            meta.name = 'viewport';
            meta.content = 'width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes';
            document.head.appendChild(meta);
        }
    })();
    
    window.Telegram.WebApp.ready();
    window.Telegram.WebApp.expand();
    window.Telegram.WebApp.setHeaderColor('#000000');
    window.Telegram.WebApp.setBackgroundColor('#000000');
</script>
""", height=0)

# --- TASARIM SİSTEMİ (ULTIMATE MUSEUM CSS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600&family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=Lato:wght@300;400&display=swap');

    /* Genel Tema */
    .stApp {
        background-color: #050505;
        color: #e0e0e0;
        font-family: 'Lato', sans-serif;
    }
    
    /* Gizlemeler */
    header, footer, .stDeployButton {display:none !important;}
    
    /* Tipografi */
    h1, h2, .big-font {
        font-family: 'Cinzel', serif !important;
        color: #d4af37 !important;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    h3, .serif-font {
        font-family: 'Playfair Display', serif !important;
        font-style: italic;
        color: #cccccc !important;
    }
    
    /* Hero Section */
    .hero-container {
        position: relative;
        width: 100%;
        height: 450px;
        overflow: hidden;
        border-radius: 4px;
        margin-bottom: 50px;
        border: 1px solid #1a1a1a;
        box-shadow: 0 30px 60px rgba(0,0,0,0.9);
    }
    .hero-overlay {
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(to top, #050505 5%, rgba(5,5,5,0.6) 40%, transparent 100%);
        display: flex;
        flex-direction: column;
        justify-content: flex-end;
        padding: 40px;
        z-index: 2;
    }
    .hero-img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        opacity: 0.9;
        transition: transform 15s ease-out;
    }
    .hero-container:hover .hero-img {
        transform: scale(1.05);
    }
    
    /* Galeri Kartları - Spotlight Efekti */
    div[data-testid="stImage"] {
        background: radial-gradient(circle at center, #222 0%, #050505 80%);
        border: 1px solid #151515;
        border-radius: 2px;
        height: 400px;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        position: relative;
        transition: border-color 0.4s ease;
    }
    
    div[data-testid="stImage"]:hover {
        border-color: #333;
    }

    div[data-testid="stImage"] img {
        object-fit: contain !important;
        max-height: 85% !important;
        max-width: 90% !important;
        width: auto !important;
        height: auto !important;
        filter: drop-shadow(0 15px 30px rgba(0,0,0,0.9)); 
        transition: transform 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    }
    
    div[data-testid="stImage"]:hover img {
        transform: scale(1.03) translateY(-5px);
    }
    
    /* Butonlar */
    div.stButton > button {
        background: transparent;
        color: #999;
        border: 1px solid #222;
        font-family: 'Lato', sans-serif;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 12px;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        border-color: #d4af37;
        color: #d4af37;
        background: rgba(212, 175, 55, 0.05);
    }

    /* Modern Link Tasarımı (Hover effect) */
    .art-link {
        color: #e0e0e0; 
        text-decoration: none; 
        border-bottom: 1px solid #444; 
        padding-bottom: 2px; 
        font-size: 13px; 
        letter-spacing: 1px; 
        transition: 0.3s ease;
    }
    .art-link:hover {
        color: #d4af37;
        border-bottom-color: #d4af37;
    }
    .art-link.primary {
        border-bottom-color: #d4af37;
        color: #fff;
    }
    
    /* Selectbox */
    div[data-baseweb="select"] > div, .stTextInput input {
        background-color: #0a0a0a;
        border: 1px solid #333;
        color: #d4af37;
    }

    @media (max-width: 768px) {
        .hero-container { height: 300px; }
        div[data-testid="stImage"] { height: 300px; }
    }
</style>
""", unsafe_allow_html=True)

# --- 2. API CONFIG ---
try: RIJKS_API_KEY = st.secrets["API_KEYS"]["rijksmuseum"]
except: RIJKS_API_KEY = "YOUR_KEY"
try: HARVARD_API_KEY = st.secrets["API_KEYS"]["harvard"]
except: HARVARD_API_KEY = "YOUR_KEY"
try: SMITHSONIAN_API_KEY = st.secrets["API_KEYS"]["smithsonian"]
except: SMITHSONIAN_API_KEY = "YOUR_KEY"
try: EUROPEANA_API_KEY = st.secrets["API_KEYS"]["europeana"]
except: EUROPEANA_API_KEY = "YOUR_KEY"
try: COOPER_HEWITT_API_KEY = st.secrets["API_KEYS"]["cooper_hewitt"]
except: COOPER_HEWITT_API_KEY = "YOUR_KEY"

# --- 3. STATE ---
if 'view' not in st.session_state: st.session_state.view = 'list'
if 'selected_art' not in st.session_state: st.session_state.selected_art = None
if 'query' not in st.session_state: st.session_state.query = "Impressionism"
if 'artworks' not in st.session_state: st.session_state.artworks = []
if 'page' not in st.session_state: st.session_state.page = 1 
if 'met_ids' not in st.session_state: st.session_state.met_ids = [] 
if 'seen_ids' not in st.session_state: st.session_state.seen_ids = set()

def safe_str(val):
    if val is None: return ""
    if isinstance(val, list): return ", ".join([str(v) for v in val])
    return str(val)

# --- 4. GÜVENLİ NORMALİZASYON FONKSİYONLARI ---
def normalize_chicago(item):
    if not item.get('image_id'): return None
    iiif = "https://www.artic.edu/iiif/2"
    return {
        'id': f"chi-{item['id']}", 'source': 'Chicago Art Inst.',
        'title': safe_str(item.get('title')), 
        'artist': safe_str(item.get('artist_display', 'Unknown').split('\n')[0]),
        'date': safe_str(item.get('date_display')), 
        'thumbnail': f"{iiif}/{item['image_id']}/full/400,/0/default.jpg",
        'high_res': f"{iiif}/{item['image_id']}/full/1686,/0/default.jpg", 
        'link': f"https://www.artic.edu/artworks/{item['id']}",
        'iiif_manifest': f"{iiif}/{item['image_id']}/info.json", 
        'colors': [], 'dimensions': safe_str(item.get('dimensions', ''))
    }

def normalize_cleveland(item):
    web_img = item.get('images', {}).get('web', {}).get('url')
    if not web_img: return None
    creators = item.get('creators', [])
    artist = creators[0].get('description', 'Unknown') if creators else 'Unknown'
    high_res = web_img
    if item.get('images', {}).get('print', {}).get('url'):
        high_res = item['images']['print']['url']
    elif item.get('images', {}).get('full', {}).get('url'):
        high_res = item['images']['full']['url']
    colors = []
    if isinstance(item.get('colour'), dict):
        colors = list(item['colour'].keys())[:5]
    return {
        'id': f"cle-{item['id']}", 'source': 'Cleveland Museum',
        'title': safe_str(item.get('title')), 'artist': safe_str(artist),
        'date': safe_str(item.get('creation_date')), 'thumbnail': web_img,
        'high_res': high_res, 'link': item.get('url', '#'), 'iiif_manifest': None,
        'colors': colors, 'dimensions': safe_str(item.get('measurements', ''))
    }

def normalize_met(item):
    if not item.get('primaryImageSmall'): return None
    return {
        'id': f"met-{item['objectID']}", 'source': 'The Met (NY)',
        'title': safe_str(item.get('title')), 
        'artist': safe_str(item.get('artistDisplayName') or 'Unknown'),
        'date': safe_str(item.get('objectDate')), 
        'thumbnail': item['primaryImageSmall'],
        'high_res': item.get('primaryImage', item['primaryImageSmall']), 
        'link': item.get('objectURL', '#'), 'iiif_manifest': None,
        'colors': [], 'dimensions': safe_str(item.get('dimensions', ''))
    }

def normalize_rijksmuseum(item):
    if not item.get('webImage'): return None
    url = item['webImage']['url']
    return {
        'id': f"rijks-{item.get('objectNumber', '')}", 'source': 'Rijksmuseum',
        'title': safe_str(item.get('title')), 
        'artist': safe_str(item.get('principalOrFirstMaker', 'Unknown')),
        'date': safe_str(item.get('dating', {}).get('presentingDate', '')), 
        'thumbnail': url,
        'high_res': url.replace('=s0', '=s2048'), 
        'link': item.get('links', {}).get('web', '#'),
        'iiif_manifest': None, 'colors': [], 'dimensions': ''
    }

def normalize_harvard(item):
    if not item.get('primaryimageurl'): return None
    url = item['primaryimageurl']
    iiif = None
    high = url
    if 'ids.lib.harvard.edu' in url:
        high = url.replace('full/full', 'full/!2048,2048')
        iiif = url.replace('/full/full/0/default.jpg', '/info.json')
    people = item.get('people', [])
    artist = people[0].get('name', 'Unknown') if people else 'Unknown'
    return {
        'id': f"harv-{item['id']}", 'source': 'Harvard Art Museums',
        'title': safe_str(item.get('title')), 'artist': safe_str(artist),
        'date': safe_str(item.get('dated', '')), 'thumbnail': url,
        'high_res': high, 'link': item.get('url', '#'), 'iiif_manifest': iiif,
        'colors': [], 'dimensions': ''
    }

def normalize_smithsonian(item):
    try:
        content = item.get('content', {})
        media = content.get('descriptiveNonRepeating', {}).get('online_media', {}).get('media', [])
        if not media: return None
        thumb = media[0].get('thumbnail')
        if not thumb: return None
        high = thumb
        for res in media[0].get('resources', []):
            if res.get('url'): high = res['url']; break
        artist = content.get('indexedStructured', {}).get('name', ['Unknown'])[0]
        title = content.get('descriptiveNonRepeating', {}).get('title', {}).get('content', '')
        return {
            'id': f"smith-{item.get('id')}", 'source': 'Smithsonian',
            'title': safe_str(title), 'artist': safe_str(artist),
            'date': '', 'thumbnail': thumb, 'high_res': high,
            'link': content.get('descriptiveNonRepeating', {}).get('record_link', '#'),
            'iiif_manifest': None, 'colors': [], 'dimensions': ''
        }
    except: return None

def normalize_europeana(item):
    if not item.get('edmPreview'): return None
    try:
        return {
            'id': f"eur-{item['id']}", 'source': 'Europeana',
            'title': safe_str(item.get('title', ['Untitled'])[0]),
            'artist': safe_str(item.get('dcCreator', ['Unknown'])[0]),
            'date': safe_str(item.get('year', [''])[0]),
            'thumbnail': item['edmPreview'][0],
            'high_res': item.get('edmIsShownBy', [item['edmPreview'][0]])[0],
            'link': item.get('guid', '#'), 'iiif_manifest': None, 'colors': [], 'dimensions': ''
        }
    except: return None

def normalize_cooper_hewitt(item):
    if not item.get('images'): return None
    try:
        img = item['images'][0]
        base = img.get('b', {}).get('url')
        if not base: return None
        return {
            'id': f"coop-{item.get('id')}", 'source': 'Cooper Hewitt',
            'title': safe_str(item.get('title')),
            'artist': safe_str(item.get('participants', [{}])[0].get('person_name', 'Unknown')),
            'date': safe_str(item.get('date', '')),
            'thumbnail': img.get('sq', {}).get('url', base),
            'high_res': img.get('z', {}).get('url', base),
            'link': item.get('url', '#'), 'iiif_manifest': None, 'colors': [], 'dimensions': ''
        }
    except: return None

def normalize_brooklyn(item):
    if not item.get('images'): return None
    try:
        img = item['images'][0].get('largest_derivative_url')
        if not img: return None
        return {
            'id': f"brk-{item['id']}", 'source': 'Brooklyn Museum',
            'title': safe_str(item.get('title')),
            'artist': safe_str(item.get('artists', [{}])[0].get('name', 'Unknown')),
            'date': safe_str(item.get('object_date', '')),
            'thumbnail': img, 'high_res': img,
            'link': f"https://www.brooklynmuseum.org/opencollection/objects/{item['id']}",
            'iiif_manifest': None, 'colors': [], 'dimensions': ''
        }
    except: return None

def normalize_va(item):
    if not item.get('_primaryImageId'): return None
    img_id = item['_primaryImageId']
    base = f"https://framemark.vam.ac.uk/collections/{img_id}"
    return {
        'id': f"va-{item.get('systemNumber')}", 'source': 'V&A Museum',
        'title': safe_str(item.get('_primaryTitle', '')),
        'artist': safe_str(item.get('_primaryMaker', {}).get('name', 'Unknown')),
        'date': safe_str(item.get('_primaryDate', '')),
        'thumbnail': f"{base}/full/!400,400/0/default.jpg",
        'high_res': f"{base}/full/!2048,2048/0/default.jpg",
        'link': f"https://collections.vam.ac.uk/item/{item.get('systemNumber')}",
        'iiif_manifest': f"{base}/info.json", 'colors': [], 'dimensions': ''
    }

def normalize_getty(item):
    if not item.get('_label'): return None
    try:
        rep = item.get('representation', [{}])
        if isinstance(rep, dict): rep = [rep]
        if not rep or not rep[0].get('id'): return None
        base = rep[0]['id']
        iiif = base.replace('/full/full/0/default.jpg', '/info.json') if 'iiif' in base else None
        artist = 'Unknown'
        prod = item.get('produced_by', {})
        if prod and 'carried_out_by' in prod:
            makers = prod['carried_out_by']
            if isinstance(makers, list): artist = makers[0].get('_label', 'Unknown')
            elif isinstance(makers, dict): artist = makers.get('_label', 'Unknown')
        return {
            'id': f"getty-{item.get('id', '').split('/')[-1]}", 'source': 'The Getty',
            'title': safe_str(item.get('_label')), 'artist': safe_str(artist),
            'date': '', 'thumbnail': base, 'high_res': base,
            'link': item.get('id', '#'), 'iiif_manifest': iiif, 'colors': [], 'dimensions': ''
        }
    except: return None

def normalize_nga(item):
    if not item.get('iiifthumburl'): return None
    url = item['iiifthumburl']
    iiif = None
    high = url
    if 'iiif' in url:
        base = url.split('/full/')[0]
        iiif = f"{base}/info.json"
        high = f"{base}/full/!2048,2048/0/default.jpg"
    return {
        'id': f"nga-{item.get('objectid')}", 'source': 'National Gallery (US)',
        'title': safe_str(item.get('title')), 'artist': safe_str(item.get('attribution', 'Unknown')),
        'date': safe_str(item.get('displaydate', '')), 'thumbnail': url, 'high_res': high,
        'link': f"https://www.nga.gov/collection/art-object-page.{item.get('objectid')}.html",
        'iiif_manifest': iiif, 'colors': [], 'dimensions': ''
    }

# --- 5. FETCH ENGINE ---
@st.cache_data(ttl=3600, show_spinner=False)
def search_met_ids_cached(query):
    try:
        r = requests.get(f"https://collectionapi.metmuseum.org/public/collection/v1/search?q={query}&hasImages=true&isPublicDomain=true", timeout=4)
        return r.json().get('objectIDs', [])[:300]
    except: return []

def fetch_met_details(oid):
    try:
        r = requests.get(f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{oid}", timeout=2)
        if r.status_code == 200: return normalize_met(r.json())
    except: return None

def fetch_rijks(q, limit, page):
    if "YOUR_KEY" in RIJKS_API_KEY: return []
    try:
        r = requests.get(f"https://www.rijksmuseum.nl/api/en/collection?key={RIJKS_API_KEY}&q={q}&imgonly=True&ps={limit}&p={page}", timeout=3)
        return [normalize_rijksmuseum(x) for x in r.json().get('artObjects', []) if normalize_rijksmuseum(x)]
    except: return []

def fetch_harvard(q, limit, page):
    if "YOUR_KEY" in HARVARD_API_KEY: return []
    try:
        off = (page-1)*limit
        r = requests.get(f"https://api.harvardartmuseums.org/object?apikey={HARVARD_API_KEY}&q={q}&hasimage=1&size={limit}&from={off}", timeout=3)
        return [normalize_harvard(x) for x in r.json().get('records', []) if normalize_harvard(x)]
    except: return []

def fetch_smithsonian(q, limit, page):
    if "YOUR_KEY" in SMITHSONIAN_API_KEY: return []
    try:
        start = (page-1)*limit
        r = requests.get(f"https://api.si.edu/openaccess/api/v1.0/search?q={q}&api_key={SMITHSONIAN_API_KEY}&rows={limit}&start={start}&online_media_type=Images", timeout=3)
        return [normalize_smithsonian(x) for x in r.json().get('response', {}).get('rows', []) if normalize_smithsonian(x)]
    except: return []

def fetch_europeana(q, limit, page):
    if "YOUR_KEY" in EUROPEANA_API_KEY: return []
    try:
        start = (page-1)*limit + 1
        r = requests.get(f"https://api.europeana.eu/record/v2/search.json?wskey={EUROPEANA_API_KEY}&query={q}&media=true&rows={limit}&start={start}&reusability=open", timeout=3)
        return [normalize_europeana(x) for x in r.json().get('items', []) if normalize_europeana(x)]
    except: return []

def fetch_cooper(q, limit, page):
    if "YOUR_KEY" in COOPER_HEWITT_API_KEY: return []
    try:
        r = requests.get(f"https://api.collection.cooperhewitt.org/rest/?method=cooperhewitt.search.collection&access_token={COOPER_HEWITT_API_KEY}&query={q}&has_images=1&per_page={limit}&page={page}", timeout=3)
        return [normalize_cooper_hewitt(x) for x in r.json().get('objects', []) if normalize_cooper_hewitt(x)]
    except: return []

def fetch_brooklyn(q, limit, page):
    try:
        off = (page-1)*limit
        r = requests.get(f"https://www.brooklynmuseum.org/api/v2/object/?q={q}&has_images=1&limit={limit}&offset={off}", timeout=3)
        return [normalize_brooklyn(x) for x in r.json().get('data', []) if normalize_brooklyn(x)]
    except: return []

def fetch_va(q, limit, page):
    try:
        r = requests.get(f"https://api.vam.ac.uk/v2/objects/search?q={q}&images_exist=1&page_size={limit}&page={page}", timeout=3)
        return [normalize_va(x) for x in r.json().get('records', []) if normalize_va(x)]
    except: return []

def fetch_getty(q, limit, page):
    try:
        off = (page-1)*limit
        r = requests.get(f"https://data.getty.edu/museum/collection/object/search?q={q}&limit={limit}&offset={off}", timeout=3)
        items = r.json().get('orderedItems', [])
        return [normalize_getty(x) for x in items if normalize_getty(x)]
    except: return []

def fetch_nga(q, limit, page):
    try:
        skip = (page-1)*limit
        r = requests.get(f"https://api.nga.gov/art?q={q}&limit={limit}&skip={skip}", timeout=3)
        return [normalize_nga(x) for x in r.json().get('data', []) if normalize_nga(x)]
    except: return []

def fetch_artworks_page(query, page_num):
    results = []
    def _chi():
        try:
            r = requests.get(f"https://api.artic.edu/api/v1/artworks/search?q={query}&page={page_num}&limit=4&fields=id,title,image_id,artist_display,date_display&query[term][is_public_domain]=true", timeout=3)
            return [normalize_chicago(x) for x in r.json()['data'] if normalize_chicago(x)]
        except: return []

    def _cle():
        try:
            r = requests.get(f"https://openaccess-api.clevelandart.org/api/artworks/?q={query}&skip={(page_num-1)*4}&limit=4&has_image=1", timeout=3)
            return [normalize_cleveland(x) for x in r.json()['data'] if normalize_cleveland(x)]
        except: return []

    def _met():
        ids = st.session_state.met_ids
        if not ids:
            ids = search_met_ids_cached(query)
            st.session_state.met_ids = ids
        start, end = (page_num-1)*4, (page_num-1)*4 + 4
        target_ids = ids[start:end]
        if not target_ids: return []
        with concurrent.futures.ThreadPoolExecutor() as ex:
            return [res for res in ex.map(fetch_met_details, target_ids) if res]

    def safe_exec(func, *args):
        try: return func(*args)
        except: return []

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {
            executor.submit(safe_exec, _chi): 'chi',
            executor.submit(safe_exec, _cle): 'cle',
            executor.submit(safe_exec, _met): 'met',
            executor.submit(safe_exec, fetch_rijks, query, 2, page_num): 'rijks',
            executor.submit(safe_exec, fetch_harvard, query, 2, page_num): 'harv',
            executor.submit(safe_exec, fetch_smithsonian, query, 2, page_num): 'smith',
            executor.submit(safe_exec, fetch_europeana, query, 2, page_num): 'eur',
            executor.submit(safe_exec, fetch_cooper, query, 2, page_num): 'coop',
            executor.submit(safe_exec, fetch_brooklyn, query, 2, page_num): 'brk',
            executor.submit(safe_exec, fetch_va, query, 2, page_num): 'va',
            executor.submit(safe_exec, fetch_getty, query, 2, page_num): 'getty',
            executor.submit(safe_exec, fetch_nga, query, 2, page_num): 'nga'
        }
        for f in concurrent.futures.as_completed(futures):
            res = f.result()
            if res: results.extend(res)
            
    random.shuffle(results)
    return results

# --- 6. UI ---

# BÜYÜTÜCÜ VE YENİ SEKME BUTONU EKLENDİ
def zoomable_image_pro(src, alt, iiif=None):
    # Sağ üst köşeye YENİ SEKMEDE AÇ ikonu/butonu eklendi.
    ext_btn_html = f'<a href="{src}" target="_blank" style="position:absolute; top:15px; right:15px; z-index:9999; background:rgba(20,20,20,0.8); color:#d4af37; border:1px solid #d4af37; padding:8px 15px; border-radius:4px; font-family:sans-serif; font-size:11px; text-decoration:none; letter-spacing:1px; transition:0.3s; box-shadow:0 4px 10px rgba(0,0,0,0.5);" onmouseover="this.style.background=\'#d4af37\'; this.style.color=\'#000\'" onmouseout="this.style.background=\'rgba(20,20,20,0.8)\'; this.style.color=\'#d4af37\'">YENİ SEKMEDE AÇ ↗</a>'
    
    if iiif:
        html = f"""<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1.0"><script src="https://cdn.jsdelivr.net/npm/openseadragon@4.1.0/build/openseadragon/openseadragon.min.js"></script><style>body{{margin:0;background:#050505;height:100vh;overflow:hidden}}#osd{{width:100%;height:100%}}</style></head><body>{ext_btn_html}<div id="osd"></div><script>OpenSeadragon({{id:"osd",prefixUrl:"https://cdn.jsdelivr.net/npm/openseadragon@4.1.0/build/openseadragon/images/",tileSources:"{iiif}",showNavigationControl:true,gestureSettingsMouse:{{clickToZoom:false}} }});</script></body></html>"""
    else:
        html = f"""<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1.0"><script src="https://unpkg.com/@panzoom/panzoom@4.5.1/dist/panzoom.min.js"></script><style>body{{margin:0;background:#050505;height:100vh;display:flex;align-items:center;justify-content:center;overflow:hidden}}img{{max-width:100%;max-height:100%;object-fit:contain}}</style></head><body>{ext_btn_html}<div id="sc"><img src="{src}" id="tg"></div><script>const e=document.getElementById('tg');const p=Panzoom(e,{{maxScale:5,minScale:0.5,contain:'outside'}});e.parentElement.addEventListener('wheel',p.zoomWithWheel);</script></body></html>"""
    components.html(html, height=600)

# Header
c1, c2 = st.columns([3, 1])
with c1:
    st.markdown('<div style="font-family:Cinzel; font-size:32px; color:#d4af37; letter-spacing:3px;">ARTE PURA <span style="font-size:12px; color:#666; vertical-align:middle;">MUSEUM</span></div>', unsafe_allow_html=True)
with c2:
    if st.button("🎲 KEŞFET", use_container_width=True):
        st.session_state.query = random.choice(["Surrealism", "Renaissance", "Ukiyo-e", "Abstract", "Portrait", "Baroque", "Cubism", "Islamic Art", "Gothic", "Ancient Egypt"])
        st.session_state.artworks = []
        st.session_state.seen_ids = set()
        st.session_state.page = 1
        st.session_state.view = 'list'
        st.rerun()

if st.session_state.view == 'detail' and st.session_state.selected_art:
    art = st.session_state.selected_art
    if st.button("← KOLEKSİYONA DÖN"):
        st.session_state.view = 'list'
        st.rerun()
        
    st.markdown(f"<h2 style='text-align:center;'>{art['title']}</h2>", unsafe_allow_html=True)
    zoomable_image_pro(art['high_res'], art['title'], art.get('iiif_manifest'))
    
    # Detay Bilgileri ve Ekstra Linkler eklendi
    st.markdown(f"""
    <div style="text-align:center; margin-top:20px; color:#888;">
        <p style="font-family:'Playfair Display'; font-size:24px; color:#d4af37; margin-bottom:5px;">{art['artist']}</p>
        <p style="font-size:14px;">{art['date']} • {art['source']}</p>
        
        <div style="display:flex; justify-content:center; gap:25px; margin-top:25px;">
            <a href="{art['high_res']}" target="_blank" class="art-link primary">🔍 TAM BOYUT AÇ</a>
            <a href="{art['link']}" target="_blank" class="art-link">🏛️ MÜZE KAYDI ↗</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

else:
    # Arama
    q = st.text_input("ARAMA", placeholder="Dönem, sanatçı veya akım...", label_visibility="collapsed")
    if q and q != st.session_state.query:
        st.session_state.query = q
        st.session_state.artworks = []
        st.session_state.seen_ids = set()
        st.session_state.page = 1
        st.rerun()

    st.markdown(f"<div style='text-align:center; font-size:12px; color:#555; margin:15px 0;'>KOLEKSİYON: <span style='color:#d4af37'>{st.session_state.query.upper()}</span></div>", unsafe_allow_html=True)

    if not st.session_state.artworks:
        with st.spinner('Eserler toplanıyor...'):
            batch = fetch_artworks_page(st.session_state.query, 1)
            for x in batch:
                if x['id'] not in st.session_state.seen_ids:
                    st.session_state.artworks.append(x)
                    st.session_state.seen_ids.add(x['id'])
    
    if st.session_state.artworks:
        hero = st.session_state.artworks[0]
        st.markdown(f"""
        <div class="hero-container">
            <img src="{hero['high_res']}" class="hero-img">
            <div class="hero-overlay">
                <div style="font-family:'Cinzel'; color:#d4af37; font-size:12px; letter-spacing:2px;">ÖNE ÇIKAN</div>
                <div style="font-family:'Playfair Display'; font-size:32px; color:#fff;">{hero['title']}</div>
                <div style="font-family:'Lato'; font-size:16px; color:#ccc;">{hero['artist']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    items = st.session_state.artworks[1:]
    for i, art in enumerate(items):
        col = c1 if i % 2 == 0 else c2
        with col:
            if art.get('thumbnail'):
                st.image(art['thumbnail'], use_container_width=True)
            if st.button(f"{art['title'][:30]}...", key=f"btn_{art['id']}"):
                st.session_state.selected_art = art
                st.session_state.view = 'detail'
                st.rerun()
            st.markdown("<div style='margin-bottom:40px;'></div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown('<div class="load-more-btn">', unsafe_allow_html=True)
        if st.button("DAHA FAZLA KEŞFET", use_container_width=True):
            st.session_state.page += 1
            with st.spinner("Yeni salon açılıyor..."):
                batch = fetch_artworks_page(st.session_state.query, st.session_state.page)
                found = False
                for x in batch:
                    if x['id'] not in st.session_state.seen_ids:
                        st.session_state.artworks.append(x)
                        st.session_state.seen_ids.add(x['id'])
                        found = True
                if found: st.rerun()
                else: st.warning("Başka eser bulunamadı.")
        st.markdown('</div>', unsafe_allow_html=True)
