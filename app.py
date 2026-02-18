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

# --- TASARIM SİSTEMİ (MUSEUM EDITION CSS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600&family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=Lato:wght@300;400&display=swap');

    /* Genel Tema - Derin Siyah */
    .stApp {
        background-color: #050505;
        color: #e0e0e0;
        font-family: 'Lato', sans-serif;
    }
    
    /* Gizlemeler */
    header, footer, .stDeployButton {display:none !important;}
    
    /* Tipografi - Başlıklar */
    h1, h2, .big-font {
        font-family: 'Cinzel', serif !important;
        color: #d4af37 !important; /* Altın */
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    h3, .serif-font {
        font-family: 'Playfair Display', serif !important;
        font-style: italic;
        color: #cccccc !important;
    }
    
    /* Hero Section Stili */
    .hero-container {
        position: relative;
        width: 100%;
        height: 400px;
        overflow: hidden;
        border-radius: 4px;
        margin-bottom: 40px;
        border: 1px solid #222;
        box-shadow: 0 20px 50px rgba(0,0,0,0.9);
    }
    .hero-overlay {
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        background: linear-gradient(to top, #000 0%, transparent 100%);
        padding: 40px 20px 20px 20px;
        z-index: 2;
    }
    .hero-img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        opacity: 0.8;
        transition: transform 10s ease;
    }
    .hero-img:hover {
        transform: scale(1.05);
    }
    
    /* Buton Tasarımı (Zarif, Minimal) */
    div.stButton > button {
        background-color: transparent;
        color: #aaa;
        border: 1px solid #333;
        border-radius: 2px;
        width: 100%;
        padding: 12px;
        font-family: 'Lato', sans-serif;
        font-size: 13px;
        letter-spacing: 1px;
        transition: all 0.4s ease;
        text-align: center;
        text-transform: uppercase;
    }
    div.stButton > button:hover {
        background-color: #d4af37;
        color: #000;
        border-color: #d4af37;
        box-shadow: 0 0 15px rgba(212, 175, 55, 0.3);
    }

    /* Daha Fazla Keşfet Butonu */
    .load-more-btn button {
        border: 1px solid #d4af37 !important;
        color: #d4af37 !important;
        background: rgba(212, 175, 55, 0.05) !important;
        font-weight: 600 !important;
        margin-top: 30px;
    }
    .load-more-btn button:hover {
        background: #d4af37 !important;
        color: #000 !important;
    }
    
    /* --- SPOT IŞIĞI GALERİSİ (NEW AESTHETIC) --- */
    
    div[data-testid="stImage"] {
        /* Radyal Gradyan: Merkezde parlak, kenarlarda zifiri karanlık */
        background: radial-gradient(circle at center, #2a2a2a 0%, #050505 85%);
        border: 1px solid #1a1a1a;
        border-radius: 4px;
        height: 400px; /* Görkemli yükseklik */
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        position: relative;
        margin-bottom: 0px;
        transition: border-color 0.3s ease;
    }
    
    div[data-testid="stImage"]:hover {
        border-color: #444;
    }

    div[data-testid="stImage"] img {
        object-fit: contain !important; /* Resmi asla kesme */
        max-height: 90% !important;     /* Kenarlardan nefes payı bırak */
        max-width: 90% !important;
        width: auto !important;
        height: auto !important;
        border-radius: 2px !important;
        /* Eserin kendisine derinlik kat */
        filter: drop-shadow(0 10px 20px rgba(0,0,0,0.8)); 
        transition: transform 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    }
    
    div[data-testid="stImage"]:hover img {
        transform: scale(1.02); /* Hafifçe öne gelme hissi */
    }
    
    /* Selectbox ve Input */
    div[data-baseweb="select"] > div, .stTextInput input {
        background-color: #000;
        border: 1px solid #333;
        color: #d4af37;
        font-family: 'Lato', sans-serif;
    }
    
    /* Responsive */
    @media (max-width: 767px) {
        div[data-testid="stImage"] {
            height: 300px;
        }
        .hero-container { height: 250px; }
        h1 { font-size: 20px !important; }
    }
</style>
""", unsafe_allow_html=True)

# --- 2. API ANAHTARLARI (AYNI KALDI) ---
try:
    RIJKS_API_KEY = st.secrets["API_KEYS"]["rijksmuseum"]
except Exception:
    RIJKS_API_KEY = "YOUR_RIJKSMUSEUM_API_KEY_HERE"
try:
    HARVARD_API_KEY = st.secrets["API_KEYS"]["harvard"]
except Exception:
    HARVARD_API_KEY = "YOUR_HARVARD_API_KEY_HERE"
try:
    SMITHSONIAN_API_KEY = st.secrets["API_KEYS"]["smithsonian"]
except Exception:
    SMITHSONIAN_API_KEY = "YOUR_SMITHSONIAN_API_KEY_HERE"
try:
    EUROPEANA_API_KEY = st.secrets["API_KEYS"]["europeana"]
except Exception:
    EUROPEANA_API_KEY = "YOUR_EUROPEANA_API_KEY_HERE"
try:
    COOPER_HEWITT_API_KEY = st.secrets["API_KEYS"]["cooper_hewitt"]
except Exception:
    COOPER_HEWITT_API_KEY = "YOUR_COOPER_HEWITT_API_KEY_HERE"

# --- 3. YARDIMCI FONKSİYONLAR ---
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

# --- API NORMALİZASYON (AYNI KALDI) ---
def normalize_chicago(item):
    if not item.get('image_id'): return None
    iiif = "https://www.artic.edu/iiif/2"
    image_id = item['image_id']
    return {
        'id': f"chi-{item['id']}", 'source': 'Chicago Art Inst.',
        'title': safe_str(item.get('title')), 'artist': safe_str(item.get('artist_display', 'Unknown').split('\n')[0]),
        'date': safe_str(item.get('date_display')), 'thumbnail': f"{iiif}/{image_id}/full/400,/0/default.jpg",
        'high_res': f"{iiif}/{image_id}/full/1686,/0/default.jpg", 'link': f"https://www.artic.edu/artworks/{item['id']}",
        'iiif_manifest': f"{iiif}/{image_id}/info.json", 'colors': [], 'dimensions': safe_str(item.get('dimensions', ''))
    }

def normalize_cleveland(item):
    if not item.get('images') or not item.get('images').get('web'): return None
    creators = item.get('creators', [])
    artist = creators[0].get('description', 'Unknown') if creators else 'Unknown'
    high_res_url = item['images']['web']['url']
    if 'print' in item['images']: high_res_url = item['images']['print']['url']
    elif 'full' in item['images']: high_res_url = item['images']['full']['url']
    colors = []
    if item.get('colour') and isinstance(item['colour'], dict):
        for color_name, percentage in sorted(item['colour'].items(), key=lambda x: x[1], reverse=True)[:5]:
            colors.append(color_name)
    return {
        'id': f"cle-{item['id']}", 'source': 'Cleveland Museum',
        'title': safe_str(item.get('title')), 'artist': safe_str(artist),
        'date': safe_str(item.get('creation_date')), 'thumbnail': item['images']['web']['url'],
        'high_res': high_res_url, 'link': item.get('url', '#'), 'iiif_manifest': None,
        'colors': colors, 'dimensions': safe_str(item.get('measurements', ''))
    }

def normalize_met(item):
    if not item.get('primaryImageSmall'): return None
    return {
        'id': f"met-{item['objectID']}", 'source': 'The Met (NY)',
        'title': safe_str(item.get('title')), 'artist': safe_str(item.get('artistDisplayName') or 'Unknown'),
        'date': safe_str(item.get('objectDate')), 'thumbnail': item['primaryImageSmall'],
        'high_res': item['primaryImage'], 'link': item.get('objectURL', '#'), 'iiif_manifest': None,
        'colors': [], 'dimensions': safe_str(item.get('dimensions', ''))
    }

def normalize_rijksmuseum(item):
    if not item.get('webImage'): return None
    return {
        'id': f"rijks-{item.get('objectNumber', '')}", 'source': 'Rijksmuseum',
        'title': safe_str(item.get('title')), 'artist': safe_str(item.get('principalOrFirstMaker', 'Unknown')),
        'date': safe_str(item.get('dating', {}).get('presentingDate', '')), 'thumbnail': item['webImage']['url'],
        'high_res': item['webImage']['url'].replace('=s0', '=s2048'), 'link': item.get('links', {}).get('web', '#'),
        'iiif_manifest': None, 'colors': [], 'dimensions': ''
    }

def normalize_harvard(item):
    if not item.get('primaryimageurl'): return None
    primary_img = item['primaryimageurl']
    high_res = primary_img
    iiif_manifest = None
    if primary_img.startswith('https://ids.lib.harvard.edu/'):
        high_res = primary_img.replace('/full/full/0/default.jpg', '/full/!2048,2048/0/default.jpg')
        iiif_manifest = primary_img.replace('/full/full/0/default.jpg', '/info.json')
    people = item.get('people', [])
    artist = people[0].get('name', 'Unknown') if people else 'Unknown'
    colors = []
    if item.get('colors') and isinstance(item['colors'], list):
        colors = [c.get('color', '') for c in item['colors'][:5] if c.get('color')]
    return {
        'id': f"harvard-{item['id']}", 'source': 'Harvard Art Museums',
        'title': safe_str(item.get('title')), 'artist': safe_str(artist),
        'date': safe_str(item.get('dated', '')), 'thumbnail': primary_img,
        'high_res': high_res, 'link': item.get('url', '#'), 'iiif_manifest': iiif_manifest,
        'colors': colors, 'dimensions': safe_str(item.get('dimensions', ''))
    }

def normalize_smithsonian(item):
    content = item.get('content', {})
    descriptive_data = content.get('descriptiveNonRepeating', {})
    online_media = descriptive_data.get('online_media', {})
    media_list = online_media.get('media', [])
    if not media_list: return None
    image_data = media_list[0]
    thumbnail = image_data.get('thumbnail', '')
    high_res = thumbnail
    if image_data.get('resources'):
        for res in image_data['resources']:
            if res.get('url'): high_res = res['url']; break
    indexed_data = content.get('indexedStructured', {})
    name_data = indexed_data.get('name', [])
    artist = name_data[0] if name_data else 'Unknown'
    date_data = indexed_data.get('date', [])
    date = date_data[0] if date_data else ''
    return {
        'id': f"smithsonian-{item.get('id', '')}", 'source': 'Smithsonian',
        'title': safe_str(descriptive_data.get('title', {}).get('content', '')),
        'artist': safe_str(artist), 'date': safe_str(date), 'thumbnail': thumbnail,
        'high_res': high_res, 'link': descriptive_data.get('record_link', '#'),
        'iiif_manifest': None, 'colors': [], 'dimensions': ''
    }

def normalize_europeana(item):
    if not item.get('edmPreview'): return None
    creator = item.get('dcCreator', ['Unknown'])
    artist = creator[0] if isinstance(creator, list) else creator
    date = item.get('year', [''])
    date_str = date[0] if isinstance(date, list) else date
    title = item.get('title', ['Untitled'])
    title_str = title[0] if isinstance(title, list) else title
    high_res = item.get('edmIsShownBy', [item['edmPreview']])
    high_res_url = high_res[0] if isinstance(high_res, list) else high_res
    return {
        'id': f"europeana-{item.get('id', '')}", 'source': 'Europeana',
        'title': safe_str(title_str), 'artist': safe_str(artist),
        'date': safe_str(date_str), 'thumbnail': item['edmPreview'][0] if isinstance(item['edmPreview'], list) else item['edmPreview'],
        'high_res': high_res_url, 'link': item.get('guid', '#'), 'iiif_manifest': None, 'colors': [], 'dimensions': ''
    }

def normalize_cooper_hewitt(item):
    if not item.get('images'): return None
    image = item['images'][0]
    base_url = image.get('b', {}).get('url', '')
    if not base_url: return None
    thumbnail = image.get('sq', {}).get('url', base_url)
    high_res = image.get('z', {}).get('url', base_url)
    participants = item.get('participants', [])
    artist = participants[0].get('person_name', 'Unknown') if participants else 'Unknown'
    return {
        'id': f"cooper-{item.get('id', '')}", 'source': 'Cooper Hewitt',
        'title': safe_str(item.get('title')), 'artist': safe_str(artist),
        'date': safe_str(item.get('date', '')), 'thumbnail': thumbnail,
        'high_res': high_res, 'link': item.get('url', '#'), 'iiif_manifest': None, 'colors': [], 'dimensions': ''
    }

def normalize_brooklyn(item):
    if not item.get('images'): return None
    largest = item['images'][0].get('largest_derivative_url', '')
    if not largest: return None
    artists = item.get('artists', [])
    artist = artists[0].get('name', 'Unknown') if artists else 'Unknown'
    return {
        'id': f"brooklyn-{item.get('id', '')}", 'source': 'Brooklyn Museum',
        'title': safe_str(item.get('title')), 'artist': safe_str(artist),
        'date': safe_str(item.get('object_date', '')), 'thumbnail': largest,
        'high_res': largest, 'link': f"https://www.brooklynmuseum.org/opencollection/objects/{item.get('id', '')}",
        'iiif_manifest': None, 'colors': [], 'dimensions': ''
    }

def normalize_va(item):
    if not item.get('_primaryImageId'): return None
    image_id = item['_primaryImageId']
    base_iiif = f"https://framemark.vam.ac.uk/collections/{image_id}"
    artist_name = item.get('_primaryMaker', {}).get('name', 'Unknown') if item.get('_primaryMaker') else 'Unknown'
    return {
        'id': f"va-{item.get('systemNumber', '')}", 'source': 'V&A Museum',
        'title': safe_str(item.get('_primaryTitle', '')), 'artist': safe_str(artist_name),
        'date': safe_str(item.get('_primaryDate', '')), 'thumbnail': f"{base_iiif}/full/!400,400/0/default.jpg",
        'high_res': f"{base_iiif}/full/!2048,2048/0/default.jpg", 'link': f"https://collections.vam.ac.uk/item/{item.get('systemNumber', '')}",
        'iiif_manifest': f"{base_iiif}/info.json", 'colors': [], 'dimensions': ''
    }

def normalize_getty(item):
    if not item.get('_label'): return None
    iiif_manifest = None
    thumbnail = ''
    high_res = ''
    if item.get('representation'):
        reps = item['representation'] if isinstance(item['representation'], list) else [item['representation']]
        if reps and reps[0].get('id'):
            iiif_base = reps[0]['id']
            if 'iiif' in iiif_base:
                iiif_manifest = iiif_base.replace('/full/full/0/default.jpg', '/info.json')
                thumbnail = iiif_base.replace('/full/full/0/default.jpg', '/full/400,/0/default.jpg')
                high_res = iiif_base.replace('/full/full/0/default.jpg', '/full/2048,/0/default.jpg')
            else: thumbnail = high_res = iiif_base
    if not thumbnail: return None
    artist = 'Unknown'
    if item.get('produced_by') and item['produced_by'].get('carried_out_by'):
        creators = item['produced_by']['carried_out_by']
        artist = (creators[0].get('_label', 'Unknown') if isinstance(creators, list) else creators.get('_label', 'Unknown'))
    dims = item.get('dimension', [])
    dimensions = ', '.join([d.get('_label', '') for d in (dims if isinstance(dims, list) else [dims]) if d.get('_label')])
    return {
        'id': f"getty-{item.get('id', '').split('/')[-1]}", 'source': 'The Getty',
        'title': safe_str(item.get('_label')), 'artist': safe_str(artist),
        'date': '', 'thumbnail': thumbnail, 'high_res': high_res, 'link': item.get('id', '#'),
        'iiif_manifest': iiif_manifest, 'colors': [], 'dimensions': dimensions
    }

def normalize_nga(item):
    if not item.get('iiifthumburl'): return None
    thumbnail = item['iiifthumburl']
    iiif_manifest = None
    high_res = thumbnail
    if 'iiif' in thumbnail:
        base_parts = thumbnail.split('/full/')
        if len(base_parts) > 1:
            iiif_base = base_parts[0]
            iiif_manifest = f"{iiif_base}/info.json"
            high_res = f"{iiif_base}/full/!2048,2048/0/default.jpg"
    artist = safe_str(item.get('attribution', 'Unknown'))
    date_str = safe_str(item.get('displaydate')) or (f"{item['beginyear']}-{item['endyear']}" if item.get('beginyear') else '')
    return {
        'id': f"nga-{item.get('objectid', '')}", 'source': 'National Gallery (US)',
        'title': safe_str(item.get('title', 'Untitled')), 'artist': artist,
        'date': date_str, 'thumbnail': thumbnail, 'high_res': high_res,
        'link': f"https://www.nga.gov/collection/art-object-page.{item.get('objectid', '')}.html",
        'iiif_manifest': iiif_manifest, 'colors': [], 'dimensions': safe_str(item.get('dimensions', ''))
    }

# --- VERİ ÇEKME MOTORU ---
def fetch_met_details(object_id):
    try:
        r = requests.get(f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{object_id}", timeout=2)
        if r.status_code == 200: return normalize_met(r.json())
    except: return None

@st.cache_data(ttl=3600, show_spinner=False)
def search_met_ids_cached(query):
    try:
        search_url = f"https://collectionapi.metmuseum.org/public/collection/v1/search?q={query}&hasImages=true&isPublicDomain=true"
        r = requests.get(search_url, timeout=4).json()
        ids = r.get('objectIDs', [])
        if ids: return ids[:300]
    except: pass
    return []

def fetch_artworks_page(query, page_num):
    new_artworks = []
    main_limit = 4
    secondary_limit = 2

    # Wrapper fonksiyonlar
    def _chicago():
        try:
            url = f"https://api.artic.edu/api/v1/artworks/search?q={query}&page={page_num}&limit={main_limit}&fields=id,title,image_id,artist_display,date_display&query[term][is_public_domain]=true"
            return [normalize_chicago(i) for i in requests.get(url, timeout=3).json()['data'] if normalize_chicago(i)]
        except: return []

    def _cleveland():
        try:
            url = f"https://openaccess-api.clevelandart.org/api/artworks/?q={query}&skip={(page_num-1)*main_limit}&limit={main_limit}&has_image=1"
            return [normalize_cleveland(i) for i in requests.get(url, timeout=3).json()['data'] if normalize_cleveland(i)]
        except: return []

    def _met():
        st.session_state.met_ids = search_met_ids_cached(query)
        if st.session_state.met_ids:
            start, end = (page_num - 1) * main_limit, (page_num - 1) * main_limit + main_limit
            ids = st.session_state.met_ids[start:end]
            if ids:
                with concurrent.futures.ThreadPoolExecutor() as ex:
                    return [res for res in ex.map(fetch_met_details, ids) if res]
        return []

    # Diğer API çağrıları basitleştirildi...
    def _generic_fetch(func, *args, **kwargs):
        try: return func(*args, **kwargs)
        except: return []

    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
        futures = {
            executor.submit(_chicago): 'chi', executor.submit(_cleveland): 'cle', executor.submit(_met): 'met',
            executor.submit(_generic_fetch, fetch_rijksmuseum, query, secondary_limit, page_num): 'rijks',
            executor.submit(_generic_fetch, fetch_harvard, query, secondary_limit, page_num): 'harv',
            executor.submit(_generic_fetch, fetch_smithsonian, query, secondary_limit, page_num): 'smith',
            executor.submit(_generic_fetch, fetch_europeana, query, secondary_limit, page_num): 'eur',
            executor.submit(_generic_fetch, fetch_cooper_hewitt, query, secondary_limit, page_num): 'coop',
            executor.submit(_generic_fetch, fetch_brooklyn, query, secondary_limit, page_num): 'brk',
            executor.submit(_generic_fetch, fetch_va, query, secondary_limit, page_num): 'va',
            executor.submit(_generic_fetch, fetch_getty, query, secondary_limit, page_num): 'getty',
            executor.submit(_generic_fetch, fetch_nga, query, secondary_limit, page_num): 'nga'
        }
        for future in concurrent.futures.as_completed(futures):
            try:
                res = future.result(timeout=6)
                if res: new_artworks.extend(res)
            except: pass
            
    random.shuffle(new_artworks)
    return new_artworks

# --- 4. PRO ZOOM BILEŞENI ---
def zoomable_image_pro(src, alt, iiif_manifest=None):
    if iiif_manifest:
        html_code = f"""<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1.0"><script src="https://cdn.jsdelivr.net/npm/openseadragon@4.1.0/build/openseadragon/openseadragon.min.js"></script><style>body{{margin:0;background:#050505;height:100vh;width:100vw;overflow:hidden}}#osd{{width:100vw;height:100vh}}</style></head><body><div id="osd"></div><script>OpenSeadragon({{id:"osd",prefixUrl:"https://cdn.jsdelivr.net/npm/openseadragon@4.1.0/build/openseadragon/images/",tileSources:"{iiif_manifest}",showNavigationControl:true,gestureSettingsMouse:{{clickToZoom:false}} }});</script></body></html>"""
    else:
        html_code = f"""<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1.0"><script src="https://unpkg.com/@panzoom/panzoom@4.5.1/dist/panzoom.min.js"></script><style>body{{margin:0;background:#050505;height:100vh;display:flex;align-items:center;justify-content:center;overflow:hidden}}img{{max-width:100%;max-height:100%;object-fit:contain}}</style></head><body><div id="sc"><img src="{src}" id="tg"></div><script>const e=document.getElementById('tg');const p=Panzoom(e,{{maxScale:5,minScale:0.5,contain:'outside'}});e.parentElement.addEventListener('wheel',p.zoomWithWheel);</script></body></html>"""
    components.html(html_code, height=600)

# --- 5. ARAYÜZ MANTIĞI ---

# Header (Cinzel Font ile Görkemli Başlık)
c1, c2 = st.columns([3, 1])
with c1:
    st.markdown('<div style="font-family:Cinzel; font-size:36px; color:#d4af37; letter-spacing:4px; margin-bottom:10px;">ARTE PURA <span style="font-size:14px; color:#666; vertical-align:middle; letter-spacing:2px;">MUSEUM EDITION</span></div>', unsafe_allow_html=True)
with c2:
    if st.button("🎲 KEŞFET", help="Rastgele bir akım seç"):
        topics = ["Surrealism", "Renaissance", "Ukiyo-e", "Abstract", "Portrait", "Baroque", "Cubism", "Islamic Art", "Gothic", "Ancient Egypt"]
        st.session_state.query = random.choice(topics)
        st.session_state.artworks = []
        st.session_state.seen_ids = set()
        st.session_state.page = 1
        st.session_state.view = 'list'
        st.rerun()

# --- DETAY GÖRÜNÜMÜ ---
if st.session_state.view == 'detail' and st.session_state.selected_art:
    art = st.session_state.selected_art
    if st.button("← KOLEKSİYONA DÖN", key="back_btn"):
        st.session_state.view = 'list'
        st.rerun()
    
    st.markdown(f"<h2 style='text-align:center; margin-bottom:20px;'>{art['title']}</h2>", unsafe_allow_html=True)
    zoomable_image_pro(art['high_res'], art['title'], art.get('iiif_manifest'))
    
    # Detay Kartı
    st.markdown(f"""
    <div style="background:#0a0a0a; border:1px solid #222; padding:30px; margin-top:20px; text-align:center;">
        <p style="font-family:'Playfair Display'; font-size:24px; color:#d4af37; margin-bottom:10px;">{art['artist']}</p>
        <p style="color:#888; letter-spacing:1px; font-size:14px;">{art['date'].upper()} • {art['source'].upper()}</p>
        <br>
        <a href="{art['link']}" target="_blank" style="color:#e0e0e0; text-decoration:none; border-bottom:1px solid #444; padding-bottom:2px; transition:0.3s;">MÜZE KAYDINI İNCELE ↗</a>
    </div>
    """, unsafe_allow_html=True)

# --- LİSTE GÖRÜNÜMÜ ---
else:
    # Arama Alanı
    tags = ["Impressionism", "Van Gogh", "Japanese Art", "Sculpture", "Bauhaus", "Modernism", "Islamic Art", "Romanticism"]
    filter_choice = st.selectbox("KOLEKSİYON SEÇİN", ["Kişisel Arama..."] + tags, label_visibility="collapsed")
    
    new_query = st.session_state.query
    if filter_choice != "Kişisel Arama..." and filter_choice != st.session_state.query:
        new_query = filter_choice
    elif filter_choice == "Kişisel Arama...":
        txt_in = st.text_input("ARAMA", placeholder="Dönem, sanatçı veya akım...", label_visibility="collapsed")
        if txt_in and txt_in != st.session_state.query: new_query = txt_in
            
    if new_query != st.session_state.query:
        st.session_state.query = new_query
        st.session_state.artworks = []
        st.session_state.seen_ids = set()
        st.session_state.page = 1
        st.rerun()

    st.markdown(f"<div style='text-align:center; color:#444; font-size:12px; letter-spacing:2px; margin:20px 0;'>ŞU AN GÖSTERİMDE: <span style='color:#d4af37'>{st.session_state.query.upper()}</span></div>", unsafe_allow_html=True)

    # Veri Yükleme
    if not st.session_state.artworks:
        with st.spinner('Küratör seçimi hazırlanıyor...'):
            batch = fetch_artworks_page(st.session_state.query, 1)
            for x in batch:
                if x['id'] not in st.session_state.seen_ids:
                    st.session_state.artworks.append(x)
                    st.session_state.seen_ids.add(x['id'])

    # HERO SECTION (Günün Eseri)
    if st.session_state.artworks:
        hero = st.session_state.artworks[0] # İlk eseri Hero yap
        st.markdown(f"""
        <div class="hero-container">
            <img src="{hero['high_res']}" class="hero-img">
            <div class="hero-overlay">
                <div style="font-family:'Cinzel'; color:#d4af37; font-size:12px; letter-spacing:2px; margin-bottom:5px;">ÖNE ÇIKAN ESER</div>
                <div style="font-family:'Playfair Display'; font-size:32px; color:#fff;">{hero['title']}</div>
                <div style="font-family:'Lato'; font-size:16px; color:#ccc; margin-top:5px;">{hero['artist']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # GRID GALERİSİ
    c1, c2 = st.columns(2)
    # Hero eseri (index 0) listede tekrar göstermemek için index 1'den başla
    gallery_items = st.session_state.artworks[1:]
    
    for i, art in enumerate(gallery_items):
        col = c1 if i % 2 == 0 else c2
        with col:
            img_url = art.get('thumbnail', '')
            if img_url:
                st.image(img_url, use_container_width=True)
            
            # Eser Bilgisi Butonu
            label = f"{art['title'][:25]}..." if len(art['title']) > 25 else art['title']
            if st.button(f"{label}  •  {art['artist'].split(' ')[-1]}", key=f"btn_{art['id']}_{i}"):
                st.session_state.selected_art = art
                st.session_state.view = 'detail'
                st.rerun()
            
            st.markdown("<div style='margin-bottom:40px;'></div>", unsafe_allow_html=True)

    # DAHA FAZLA BUTONU
    st.markdown("---")
    col_l1, col_l2, col_l3 = st.columns([1, 1, 1])
    with col_l2:
        st.markdown('<div class="load-more-btn">', unsafe_allow_html=True)
        if st.button("DAHA FAZLA KEŞFET", use_container_width=True):
            st.session_state.page += 1
            with st.spinner(f"Salon {st.session_state.page} açılıyor..."):
                new_batch = fetch_artworks_page(st.session_state.query, st.session_state.page)
                found_new = False
                for x in new_batch:
                    if x['id'] not in st.session_state.seen_ids:
                        st.session_state.artworks.append(x)
                        st.session_state.seen_ids.add(x['id'])
                        found_new = True
                if found_new: st.rerun()
                else: st.warning("Bu koleksiyonun sonuna geldiniz.")
        st.markdown('</div>', unsafe_allow_html=True)
