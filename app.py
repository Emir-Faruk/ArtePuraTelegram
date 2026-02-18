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
    // Set viewport for better zoom support
    (function() {
        var viewport = document.querySelector('meta[name="viewport"]');
        if (viewport) {
            viewport.setAttribute('content', 'width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes');
        } else {
            // Create viewport meta tag if it doesn't exist
            var meta = document.createElement('meta');
            meta.name = 'viewport';
            meta.content = 'width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes';
            document.head.appendChild(meta);
        }
    })();
    
    window.Telegram.WebApp.ready();
    window.Telegram.WebApp.expand();
    window.Telegram.WebApp.setHeaderColor('#0f0f0f');
    window.Telegram.WebApp.setBackgroundColor('#0f0f0f');
</script>
""", height=0)

# --- TASARIM SİSTEMİ (CSS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=Inter:wght@300;400;600&display=swap');

    /* Genel Tema */
    .stApp {
        background-color: #0f0f0f;
        color: #e0e0e0;
        font-family: 'Inter', sans-serif;
    }
    
    /* Gizlemeler */
    header, footer, .stDeployButton {display:none !important;}
    
    /* Tipografi */
    h1, h2, h3, .serif-font {
        font-family: 'Playfair Display', serif !important;
        color: #e0e0e0 !important;
    }
    
    /* Buton Tasarımı (Listeleme) */
    div.stButton > button {
        background-color: #1a1a1a;
        color: #d4af37;
        border: 1px solid #333;
        border-top: none; 
        border-radius: 0 0 8px 8px;
        width: 100%;
        padding: 10px;
        font-family: 'Inter', sans-serif;
        font-size: 14px;
        transition: all 0.3s;
        text-align: left;
    }
    div.stButton > button:hover {
        background-color: #222;
        border-color: #d4af37;
        color: #fff;
    }

    /* Daha Fazla Keşfet Butonu için özel stil */
    .load-more-btn button {
        background-color: #d4af37 !important;
        color: #000 !important;
        font-weight: bold !important;
        text-align: center !important;
        border-radius: 8px !important;
    }
    
    /* Görsel Kenarları - Responsive */
    div[data-testid="stImage"] img {
        border-radius: 8px 8px 0 0 !important;
        border: 1px solid #333;
        border-bottom: none;
        object-fit: cover;
        width: 100%;
        height: auto;
        max-height: 400px;
        min-height: 200px;
    }
    
    /* Selectbox */
    div[data-baseweb="select"] > div {
        background-color: #1a1a1a;
        border-color: #333;
        color: white;
    }
    
    /* Responsive Design - Media Queries for Zoom/Scale */
    
    /* Large screens and zoomed out (>1200px) */
    @media (min-width: 1200px) {
        div[data-testid="stImage"] img {
            max-height: 450px;
        }
        h1, h2, h3 {
            font-size: calc(1.2rem + 0.5vw);
        }
    }
    
    /* Medium screens and standard zoom (768px - 1199px) */
    @media (min-width: 768px) and (max-width: 1199px) {
        div[data-testid="stImage"] img {
            max-height: 350px;
        }
        div.stButton > button {
            font-size: 13px;
            padding: 8px;
        }
    }
    
    /* Small screens and zoomed in (<768px) */
    @media (max-width: 767px) {
        div[data-testid="stImage"] img {
            max-height: 280px;
            min-height: 180px;
        }
        div.stButton > button {
            font-size: 12px;
            padding: 8px;
        }
        h1, h2, h3 {
            font-size: calc(1rem + 0.3vw);
        }
    }
    
    /* Very small screens and heavily zoomed in (<480px) */
    @media (max-width: 480px) {
        div[data-testid="stImage"] img {
            max-height: 250px;
            min-height: 150px;
        }
        div.stButton > button {
            font-size: 11px;
            padding: 6px;
        }
    }
    
    /* Ensure proper scaling on zoom - limited to layout elements for performance */
    div, img, button, input, select {
        box-sizing: border-box;
    }
    
    /* Smooth transitions for responsive changes - optimized for performance */
    div[data-testid="stImage"] img {
        transition: max-height 0.3s ease, min-height 0.3s ease;
    }
    div.stButton > button {
        transition: font-size 0.3s ease, padding 0.3s ease;
    }
    h1, h2, h3 {
        transition: font-size 0.3s ease;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. API ANAHTARLARI ---
# API anahtarlarını Streamlit secrets'tan veya buradan alın
# Streamlit Cloud kullanıyorsanız: st.secrets["API_KEYS"]["rijksmuseum"] şeklinde erişin
# Yerel test için bu değişkenlere anahtarlarınızı ekleyin

try:
    RIJKS_API_KEY = st.secrets["API_KEYS"]["rijksmuseum"]
except:
    RIJKS_API_KEY = "YOUR_RIJKSMUSEUM_API_KEY_HERE"  # https://data.rijksmuseum.nl/object-metadata/api/

try:
    HARVARD_API_KEY = st.secrets["API_KEYS"]["harvard"]
except:
    HARVARD_API_KEY = "YOUR_HARVARD_API_KEY_HERE"  # https://www.harvardartmuseums.org/collections/api

try:
    SMITHSONIAN_API_KEY = st.secrets["API_KEYS"]["smithsonian"]
except:
    SMITHSONIAN_API_KEY = "YOUR_SMITHSONIAN_API_KEY_HERE"  # https://api.si.edu/openaccess/api/v1.0/

try:
    EUROPEANA_API_KEY = st.secrets["API_KEYS"]["europeana"]
except:
    EUROPEANA_API_KEY = "YOUR_EUROPEANA_API_KEY_HERE"  # https://pro.europeana.eu/page/get-api

try:
    COOPER_HEWITT_API_KEY = st.secrets["API_KEYS"]["cooper_hewitt"]
except:
    COOPER_HEWITT_API_KEY = "YOUR_COOPER_HEWITT_API_KEY_HERE"  # https://collection.cooperhewitt.org/api/

# Brooklyn Museum and V&A do not require API keys for basic access

# --- 3. YARDIMCI FONKSİYONLAR VE STATE ---

# State Başlatma
if 'view' not in st.session_state: st.session_state.view = 'list'
if 'selected_art' not in st.session_state: st.session_state.selected_art = None
if 'query' not in st.session_state: st.session_state.query = "Impressionism"
if 'artworks' not in st.session_state: st.session_state.artworks = []
if 'page' not in st.session_state: st.session_state.page = 1 # Sayfa Sayacı
if 'met_ids' not in st.session_state: st.session_state.met_ids = [] # Met ID Cache

def safe_str(val):
    if val is None: return ""
    if isinstance(val, list): return ", ".join([str(v) for v in val])
    return str(val)

# --- API NORMALİZASYON ---

def normalize_chicago(item):
    if not item.get('image_id'): return None
    iiif = "https://www.artic.edu/iiif/2"
    return {
        'id': f"chi-{item['id']}",
        'source': 'Chicago Art Inst.',
        'title': safe_str(item.get('title')),
        'artist': safe_str(item.get('artist_display', 'Unknown').split('\n')[0]),
        'date': safe_str(item.get('date_display')),
        'thumbnail': f"{iiif}/{item['image_id']}/full/400,/0/default.jpg",
        'high_res': f"{iiif}/{item['image_id']}/full/1686,/0/default.jpg", 
        'link': f"https://www.artic.edu/artworks/{item['id']}"
    }

def normalize_cleveland(item):
    if not item.get('images') or not item.get('images').get('web'): return None
    creators = item.get('creators', [])
    artist = creators[0].get('description', 'Unknown') if creators else 'Unknown'
    
    high_res_url = item['images']['web']['url']
    if 'print' in item['images']: high_res_url = item['images']['print']['url']
    elif 'full' in item['images']: high_res_url = item['images']['full']['url']
         
    return {
        'id': f"cle-{item['id']}",
        'source': 'Cleveland Museum',
        'title': safe_str(item.get('title')),
        'artist': safe_str(artist),
        'date': safe_str(item.get('creation_date')),
        'thumbnail': item['images']['web']['url'],
        'high_res': high_res_url,
        'link': item.get('url', '#')
    }

def normalize_met(item):
    if not item.get('primaryImageSmall'): return None
    return {
        'id': f"met-{item['objectID']}",
        'source': 'The Met (NY)',
        'title': safe_str(item.get('title')),
        'artist': safe_str(item.get('artistDisplayName') or 'Unknown'),
        'date': safe_str(item.get('objectDate')),
        'thumbnail': item['primaryImageSmall'],
        'high_res': item['primaryImage'],
        'link': item.get('objectURL', '#')
    }

def normalize_rijksmuseum(item):
    """Rijksmuseum API normalization"""
    if not item.get('webImage'): return None
    return {
        'id': f"rijks-{item.get('objectNumber', '')}",
        'source': 'Rijksmuseum',
        'title': safe_str(item.get('title')),
        'artist': safe_str(item.get('principalOrFirstMaker', 'Unknown')),
        'date': safe_str(item.get('dating', {}).get('presentingDate', '')),
        'thumbnail': item['webImage']['url'],
        'high_res': item['webImage']['url'].replace('=s0', '=s2048'),  # Higher resolution
        'link': item.get('links', {}).get('web', '#')
    }

def normalize_harvard(item):
    """Harvard Art Museums API normalization"""
    if not item.get('primaryimageurl'): return None
    # Harvard uses IIIF for high-res images
    primary_img = item['primaryimageurl']
    high_res = primary_img
    if 'ids.lib.harvard.edu' in primary_img:
        # Convert to IIIF full quality
        high_res = primary_img.replace('/full/full/0/default.jpg', '/full/!2048,2048/0/default.jpg')
    
    people = item.get('people', [])
    artist = people[0].get('name', 'Unknown') if people else 'Unknown'
    
    return {
        'id': f"harvard-{item['id']}",
        'source': 'Harvard Art Museums',
        'title': safe_str(item.get('title')),
        'artist': safe_str(artist),
        'date': safe_str(item.get('dated', '')),
        'thumbnail': primary_img,
        'high_res': high_res,
        'link': item.get('url', '#')
    }

def normalize_smithsonian(item):
    """Smithsonian Open Access API normalization"""
    content = item.get('content', {})
    descriptive_data = content.get('descriptiveNonRepeating', {})
    indexed_data = content.get('indexedStructured', {})
    
    # Get image URL
    online_media = descriptive_data.get('online_media', {})
    media_list = online_media.get('media', [])
    if not media_list: return None
    
    image_data = media_list[0]
    thumbnail = image_data.get('thumbnail', '')
    # Try to get higher resolution
    resources = image_data.get('resources', [])
    high_res = thumbnail
    if resources:
        # Find largest available
        for res in resources:
            if res.get('url'):
                high_res = res['url']
                break
    
    # Get artist
    name_data = indexed_data.get('name', [])
    artist = name_data[0] if name_data else 'Unknown'
    
    # Get date
    date_data = indexed_data.get('date', [])
    date = date_data[0] if date_data else ''
    
    return {
        'id': f"smithsonian-{item.get('id', '')}",
        'source': 'Smithsonian',
        'title': safe_str(descriptive_data.get('title', {}).get('content', '')),
        'artist': safe_str(artist),
        'date': safe_str(date),
        'thumbnail': thumbnail,
        'high_res': high_res,
        'link': descriptive_data.get('record_link', '#')
    }

def normalize_europeana(item):
    """Europeana REST API normalization"""
    # Europeana has complex structure
    if not item.get('edmPreview'): return None
    
    # Get artist from dcCreator
    creator = item.get('dcCreator', ['Unknown'])
    artist = creator[0] if isinstance(creator, list) else creator
    
    # Get date
    date = item.get('year', [''])
    date_str = date[0] if isinstance(date, list) else date
    
    # Get title
    title = item.get('title', ['Untitled'])
    title_str = title[0] if isinstance(title, list) else title
    
    # For high-res, try edmIsShownBy or use preview
    high_res = item.get('edmIsShownBy', [item['edmPreview']])
    high_res_url = high_res[0] if isinstance(high_res, list) else high_res
    
    return {
        'id': f"europeana-{item.get('id', '')}",
        'source': 'Europeana',
        'title': safe_str(title_str),
        'artist': safe_str(artist),
        'date': safe_str(date_str),
        'thumbnail': item['edmPreview'][0] if isinstance(item['edmPreview'], list) else item['edmPreview'],
        'high_res': high_res_url,
        'link': item.get('guid', '#')
    }

def normalize_cooper_hewitt(item):
    """Cooper Hewitt API normalization"""
    if not item.get('images'): return None
    
    images = item['images']
    if not images: return None
    
    # Get first image
    image = images[0]
    base_url = image.get('b', {}).get('url', '')
    if not base_url: return None
    
    # Cooper Hewitt provides different sizes
    thumbnail = image.get('sq', {}).get('url', base_url)
    high_res = image.get('z', {}).get('url', base_url)  # 'z' is largest
    
    # Get artist
    participants = item.get('participants', [])
    artist = 'Unknown'
    if participants:
        artist = participants[0].get('person_name', 'Unknown')
    
    return {
        'id': f"cooper-{item.get('id', '')}",
        'source': 'Cooper Hewitt',
        'title': safe_str(item.get('title')),
        'artist': safe_str(artist),
        'date': safe_str(item.get('date', '')),
        'thumbnail': thumbnail,
        'high_res': high_res,
        'link': item.get('url', '#')
    }

def normalize_brooklyn(item):
    """Brooklyn Museum API normalization"""
    if not item.get('images'): return None
    
    images = item['images']
    if not images: return None
    
    # Get largest image
    largest = images[0].get('largest_derivative_url', '')
    if not largest: return None
    
    # Get artist
    artists = item.get('artists', [])
    artist = 'Unknown'
    if artists:
        artist = artists[0].get('name', 'Unknown')
    
    return {
        'id': f"brooklyn-{item.get('id', '')}",
        'source': 'Brooklyn Museum',
        'title': safe_str(item.get('title')),
        'artist': safe_str(artist),
        'date': safe_str(item.get('object_date', '')),
        'thumbnail': largest,
        'high_res': largest,
        'link': f"https://www.brooklynmuseum.org/opencollection/objects/{item.get('id', '')}"
    }

def normalize_va(item):
    """Victoria and Albert Museum API normalization"""
    if not item.get('_primaryImageId'): return None
    
    image_id = item['_primaryImageId']
    # V&A IIIF image service
    base_iiif = f"https://framemark.vam.ac.uk/collections/{image_id}"
    
    # Get artist
    artist_name = 'Unknown'
    if item.get('_primaryMaker'):
        artist_name = item['_primaryMaker'].get('name', 'Unknown')
    
    # Get date
    date_str = ''
    if item.get('_primaryDate'):
        date_str = item['_primaryDate']
    
    return {
        'id': f"va-{item.get('systemNumber', '')}",
        'source': 'V&A Museum',
        'title': safe_str(item.get('_primaryTitle', '')),
        'artist': safe_str(artist_name),
        'date': safe_str(date_str),
        'thumbnail': f"{base_iiif}/full/!400,400/0/default.jpg",
        'high_res': f"{base_iiif}/full/!2048,2048/0/default.jpg",
        'link': f"https://collections.vam.ac.uk/item/{item.get('systemNumber', '')}"
    }

# --- GELİŞMİŞ VERİ ÇEKME MOTORU ---

def fetch_met_details(object_id):
    """Tek bir Met objesinin detayını çeker"""
    try:
        r = requests.get(f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{object_id}", timeout=2)
        if r.status_code == 200:
            return normalize_met(r.json())
    except:
        return None

# Met ID'lerini bir kez çekip cache'liyoruz, böylece her sayfa yüklemesinde arama yapmıyoruz
@st.cache_data(ttl=3600)
def search_met_ids_cached(query):
    try:
        search_url = f"https://collectionapi.metmuseum.org/public/collection/v1/search?q={query}&hasImages=true&isPublicDomain=true"
        r = requests.get(search_url, timeout=4).json()
        ids = r.get('objectIDs', [])
        if ids:
            return ids[:300] # En fazla 300 ID saklayalım performans için
    except:
        pass
    return []

def fetch_rijksmuseum(query, limit=2):
    """Fetch artworks from Rijksmuseum"""
    if RIJKS_API_KEY == "YOUR_RIJKSMUSEUM_API_KEY_HERE":
        return []
    try:
        url = f"https://www.rijksmuseum.nl/api/en/collection?key={RIJKS_API_KEY}&q={query}&imgonly=True&ps={limit}"
        r = requests.get(url, timeout=3)
        if r.status_code == 200:
            data = r.json()
            artworks = data.get('artObjects', [])
            return [normalize_rijksmuseum(art) for art in artworks if normalize_rijksmuseum(art)]
    except:
        pass
    return []

def fetch_harvard(query, limit=2):
    """Fetch artworks from Harvard Art Museums"""
    if HARVARD_API_KEY == "YOUR_HARVARD_API_KEY_HERE":
        return []
    try:
        url = f"https://api.harvardartmuseums.org/object?apikey={HARVARD_API_KEY}&q={query}&hasimage=1&size={limit}"
        r = requests.get(url, timeout=3)
        if r.status_code == 200:
            data = r.json()
            records = data.get('records', [])
            return [normalize_harvard(art) for art in records if normalize_harvard(art)]
    except:
        pass
    return []

def fetch_smithsonian(query, limit=2):
    """Fetch artworks from Smithsonian Open Access"""
    if SMITHSONIAN_API_KEY == "YOUR_SMITHSONIAN_API_KEY_HERE":
        return []
    try:
        # Smithsonian uses rows parameter for limit
        url = f"https://api.si.edu/openaccess/api/v1.0/search?q={query}&api_key={SMITHSONIAN_API_KEY}&rows={limit}&online_media_type=Images"
        r = requests.get(url, timeout=3)
        if r.status_code == 200:
            data = r.json()
            response = data.get('response', {})
            rows = response.get('rows', [])
            return [normalize_smithsonian(art) for art in rows if normalize_smithsonian(art)]
    except:
        pass
    return []

def fetch_europeana(query, limit=2):
    """Fetch artworks from Europeana"""
    if EUROPEANA_API_KEY == "YOUR_EUROPEANA_API_KEY_HERE":
        return []
    try:
        url = f"https://api.europeana.eu/record/v2/search.json?wskey={EUROPEANA_API_KEY}&query={query}&media=true&rows={limit}&reusability=open"
        r = requests.get(url, timeout=3)
        if r.status_code == 200:
            data = r.json()
            items = data.get('items', [])
            return [normalize_europeana(art) for art in items if normalize_europeana(art)]
    except:
        pass
    return []

def fetch_cooper_hewitt(query, limit=2):
    """Fetch artworks from Cooper Hewitt"""
    if COOPER_HEWITT_API_KEY == "YOUR_COOPER_HEWITT_API_KEY_HERE":
        return []
    try:
        url = f"https://api.collection.cooperhewitt.org/rest/?method=cooperhewitt.search.collection&access_token={COOPER_HEWITT_API_KEY}&query={query}&has_images=1&per_page={limit}"
        r = requests.get(url, timeout=3)
        if r.status_code == 200:
            data = r.json()
            objects = data.get('objects', [])
            return [normalize_cooper_hewitt(art) for art in objects if normalize_cooper_hewitt(art)]
    except:
        pass
    return []

def fetch_brooklyn(query, limit=2):
    """Fetch artworks from Brooklyn Museum"""
    try:
        url = f"https://www.brooklynmuseum.org/api/v2/object/?q={query}&has_images=1&limit={limit}"
        r = requests.get(url, timeout=3)
        if r.status_code == 200:
            data = r.json()
            objects = data.get('data', [])
            return [normalize_brooklyn(art) for art in objects if normalize_brooklyn(art)]
    except:
        pass
    return []

def fetch_va(query, limit=2):
    """Fetch artworks from Victoria and Albert Museum"""
    try:
        # V&A API search endpoint
        url = f"https://api.vam.ac.uk/v2/objects/search?q={query}&images_exist=1&page_size={limit}"
        r = requests.get(url, timeout=3)
        if r.status_code == 200:
            data = r.json()
            records = data.get('records', [])
            return [normalize_va(art) for art in records if normalize_va(art)]
    except:
        pass
    return []

def fetch_artworks_page(query, page_num):
    """Belirli bir sayfadaki eserleri getirir - Tüm 10 API'den paralel çeker"""
    new_artworks = []
    
    # Define all API fetch tasks
    def fetch_chicago():
        try:
            url = f"https://api.artic.edu/api/v1/artworks/search?q={query}&page={page_num}&limit=1&fields=id,title,image_id,artist_display,date_display&query[term][is_public_domain]=true"
            r = requests.get(url, timeout=3).json()
            return [normalize_chicago(i) for i in r['data'] if normalize_chicago(i)]
        except:
            return []
    
    def fetch_cleveland_page():
        try:
            skip_val = (page_num - 1) * 1
            url = f"https://openaccess-api.clevelandart.org/api/artworks/?q={query}&skip={skip_val}&limit=1&has_image=1"
            r = requests.get(url, timeout=3).json()
            return [normalize_cleveland(i) for i in r['data'] if normalize_cleveland(i)]
        except:
            return []
    
    def fetch_met_page():
        # Eğer Met ID listesi boşsa veya sorgu değiştiyse güncelle
        if not st.session_state.met_ids:
            st.session_state.met_ids = search_met_ids_cached(query)
        
        # Sayfaya göre ID listesinden kesit al
        if st.session_state.met_ids:
            start_idx = (page_num - 1) * 1
            end_idx = start_idx + 1
            
            target_ids = st.session_state.met_ids[start_idx:end_idx]
            
            if target_ids:
                results = []
                for object_id in target_ids:
                    res = fetch_met_details(object_id)
                    if res:
                        results.append(res)
                return results
        return []
    
    # Use ThreadPoolExecutor to fetch from all APIs in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        # Submit all tasks
        futures = {
            executor.submit(fetch_chicago): 'chicago',
            executor.submit(fetch_cleveland_page): 'cleveland',
            executor.submit(fetch_met_page): 'met',
            executor.submit(fetch_rijksmuseum, query, 1): 'rijksmuseum',
            executor.submit(fetch_harvard, query, 1): 'harvard',
            executor.submit(fetch_smithsonian, query, 1): 'smithsonian',
            executor.submit(fetch_europeana, query, 1): 'europeana',
            executor.submit(fetch_cooper_hewitt, query, 1): 'cooper_hewitt',
            executor.submit(fetch_brooklyn, query, 1): 'brooklyn',
            executor.submit(fetch_va, query, 1): 'va'
        }
        
        # Collect results as they complete
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result(timeout=5)  # 5 second max wait per task
                if result:
                    new_artworks.extend(result)
            except Exception as e:
                # Silent fail - continue with other APIs
                pass
    
    random.shuffle(new_artworks)
    return new_artworks

# --- 3. PRO ZOOM BILEŞENI ---
def zoomable_image_pro(src, alt):
    html_code = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <script src="https://unpkg.com/@panzoom/panzoom@4.5.1/dist/panzoom.min.js"></script>
        <style>
            html, body {{ margin: 0; padding: 0; background-color: #000; height: 100vh; width: 100vw; overflow: hidden; }}
            #scene {{ width: 100vw; height: 100vh; display: flex; justify-content: center; align-items: center; }}
            img {{ max-width: 100%; max-height: 100%; object-fit: contain; cursor: grab; }}
            img:active {{ cursor: grabbing; }}
            .controls {{ position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); display: flex; gap: 15px; background: rgba(25, 25, 25, 0.8); padding: 10px 20px; border-radius: 30px; backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1); z-index: 100; }}
            .btn {{ background: transparent; border: none; color: #e0e0e0; cursor: pointer; display: flex; align-items: center; justify-content: center; width: 24px; height: 24px; }}
            .btn:hover {{ color: #d4af37; transform: scale(1.1); }}
            .btn svg {{ width: 20px; height: 20px; fill: currentColor; }}
            .fs-btn {{ position: fixed; bottom: 20px; right: 20px; background: rgba(25, 25, 25, 0.6); width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; border: 1px solid rgba(255, 255, 255, 0.1); color: white; cursor: pointer; backdrop-filter: blur(5px); z-index: 101; }}
            .fs-btn:hover {{ background: #d4af37; color: black; }}
            
            /* Responsive adjustments for controls */
            @media (max-width: 768px) {{
                .controls {{ gap: 10px; padding: 8px 15px; }}
                .btn {{ width: 20px; height: 20px; }}
                .btn svg {{ width: 16px; height: 16px; }}
                .fs-btn {{ width: 35px; height: 35px; }}
            }}
            
            @media (max-width: 480px) {{
                .controls {{ bottom: 10px; gap: 8px; padding: 6px 12px; }}
                .btn {{ width: 18px; height: 18px; }}
                .btn svg {{ width: 14px; height: 14px; }}
                .fs-btn {{ bottom: 10px; right: 10px; width: 32px; height: 32px; }}
            }}
        </style>
    </head>
    <body>
        <div id="scene"><img src="{src}" alt="{alt}" id="target"></div>
        <div class="controls">
            <button class="btn" id="zoom-out"><svg viewBox="0 0 24 24"><path d="M19 13H5v-2h14v2z"/></svg></button>
            <button class="btn" id="reset"><svg viewBox="0 0 24 24"><path d="M12 4V1L8 5l4 4V6c3.31 0 6 2.69 6 6 0 1.01-.25 1.97-.7 2.8l1.46 1.46A7.93 7.93 0 0020 12c0-4.42-3.58-8-7.99-8z"/></svg></button>
            <button class="btn" id="zoom-in"><svg viewBox="0 0 24 24"><path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/></svg></button>
        </div>
        <button class="fs-btn" id="fullscreen"><svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M7 14H5v5h5v-2H7v-3zm-2-4h2V7h3V5H5v5zm12 7h-3v2h5v-5h-2v3zM14 5v2h3v3h2V5h-5z"/></svg></button>
        <script>
            const elem = document.getElementById('target');
            const panzoom = Panzoom(elem, {{ maxScale: 5, minScale: 0.5, contain: false, startScale: 1, animate: true }});
            elem.onload = function() {{ panzoom.reset(); }};
            document.getElementById('scene').addEventListener('wheel', panzoom.zoomWithWheel);
            document.getElementById('zoom-in').addEventListener('click', panzoom.zoomIn);
            document.getElementById('zoom-out').addEventListener('click', panzoom.zoomOut);
            document.getElementById('reset').addEventListener('click', panzoom.reset);
            document.getElementById('fullscreen').addEventListener('click', function() {{ if (!document.fullscreenElement) {{ document.body.requestFullscreen(); }} else {{ document.exitFullscreen(); }} }});
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=650)


# --- 4. ARAYÜZ MANTIĞI ---

# Header
c1, c2 = st.columns([3, 1])
with c1:
    st.markdown('<div style="font-family:Playfair Display; font-size:24px; color:#d4af37;">Arte Pura <span style="font-size:12px; color:#666;">PRO</span></div>', unsafe_allow_html=True)
with c2:
    if st.button("🎲", help="Rastgele Konu"):
        topics = ["Surrealism", "Renaissance", "Ukiyo-e", "Abstract", "Portrait", "Baroque", "Cubism", "Islamic Art", "Modern Art", "Ancient Egypt"]
        new_topic = random.choice(topics)
        st.session_state.query = new_topic
        st.session_state.artworks = [] # Listeyi temizle
        st.session_state.met_ids = [] # Cache temizle
        st.session_state.page = 1 # Sayfayı sıfırla
        st.session_state.view = 'list'
        st.rerun()

# --- DETAY GÖRÜNÜMÜ ---
if st.session_state.view == 'detail' and st.session_state.selected_art:
    art = st.session_state.selected_art
    
    if st.button("← Galeriy Dön", key="back_btn"):
        st.session_state.view = 'list'
        st.rerun()

    zoomable_image_pro(art['high_res'], art['title'])
    
    st.markdown(f"""
    <div style="margin-top:10px; margin-bottom:5px;">
        <h2 style="margin:0; font-size:22px; color:#e0e0e0;">{art['title']}</h2>
        <p style="color:#d4af37; font-family:'Playfair Display',serif; font-style:italic;">{art['artist']}</p>
    </div>
    
    <div style="background:#1a1a1a; padding:15px; border-radius:8px; font-size:13px; color:#aaa; margin-top:20px;">
        <p><strong>Tarih:</strong> {art['date']}</p>
        <p><strong>Müze:</strong> {art['source']}</p>
        <hr style="border-color:#333;">
        <a href="{art['link']}" target="_blank" style="color:#fff; text-decoration:none;">🔗 Müze Kaydına Git</a>
    </div>
    """, unsafe_allow_html=True)

# --- LİSTE GÖRÜNÜMÜ ---
else:
    # Filtreler
    tags = ["Impressionism", "Van Gogh", "Japanese Art", "Sculpture", "Bauhaus", "Modernism", "Islamic Art"]
    filter_choice = st.selectbox("Koleksiyonlar:", ["Kişisel Arama Yap..."] + tags, label_visibility="collapsed")
    
    # Filtre Değişimi Kontrolü
    if filter_choice != "Kişisel Arama Yap..." and filter_choice != st.session_state.query:
        st.session_state.query = filter_choice
        st.session_state.artworks = [] # Yeni arama için listeyi temizle
        st.session_state.met_ids = []
        st.session_state.page = 1
        st.rerun()

    if filter_choice == "Kişisel Arama Yap...":
        search_input = st.text_input("Arama", value="", placeholder="Ressam, dönem...", label_visibility="collapsed")
        if search_input and search_input != st.session_state.query:
            st.session_state.query = search_input
            st.session_state.artworks = []
            st.session_state.met_ids = []
            st.session_state.page = 1
            st.rerun()

    st.markdown(f"<p style='font-size:12px; color:#666; margin-top:5px; margin-bottom:15px;'>Koleksiyon: <span style='color:#d4af37'>{st.session_state.query}</span></p>", unsafe_allow_html=True)

    # İLK YÜKLEME
    if not st.session_state.artworks:
        with st.spinner('Küratör seçimi hazırlanıyor...'):
            initial_batch = fetch_artworks_page(st.session_state.query, 1)
            st.session_state.artworks = initial_batch

    # GRID GÖSTERİMİ
    c1, c2 = st.columns(2)
    for i, art in enumerate(st.session_state.artworks):
        col = c1 if i % 2 == 0 else c2
        with col:
            img_url = art.get('thumbnail', '')
            if img_url:
                st.image(img_url, use_container_width=True)
            
            # Başlık uzunluğunu güvenli şekilde kesme
            display_title = (art['title'][:18] + '..') if len(art.get('title', '')) > 18 else art.get('title', '')
            
            btn_label = f"👁️ {display_title}" 
            if st.button(btn_label, key=f"btn_{art['id']}_{i}"): # Key unique olmalı
                st.session_state.selected_art = art
                st.session_state.view = 'detail'
                st.rerun()
            
            st.markdown("<div style='margin-bottom:25px;'></div>", unsafe_allow_html=True)

    # --- DAHA FAZLA KEŞFET (YENİ MANTIK) ---
    st.markdown("---")
    col_load_1, col_load_2, col_load_3 = st.columns([1, 2, 1])
    with col_load_2:
        st.markdown('<div class="load-more-btn">', unsafe_allow_html=True)
        if st.button("✨ Daha Fazla Eser Getir", use_container_width=True):
            st.session_state.page += 1 # Sayfayı artır
            with st.spinner(f"{st.session_state.page}. salon açılıyor..."):
                new_batch = fetch_artworks_page(st.session_state.query, st.session_state.page)
                if new_batch:
                    st.session_state.artworks.extend(new_batch) # Listeye EKLE
                    st.rerun()
                else:
                    st.warning("Bu koleksiyonda daha fazla eser bulunamadı.")
        st.markdown('</div>', unsafe_allow_html=True)
