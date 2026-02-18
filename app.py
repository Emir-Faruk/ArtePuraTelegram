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
    
    /* Görsel Kenarları */
    div[data-testid="stImage"] img {
        border-radius: 8px 8px 0 0 !important;
        border: 1px solid #333;
        border-bottom: none;
        object-fit: cover;
        height: 300px !important; /* Görselleri eşit boyda tutar */
    }
    
    /* Selectbox */
    div[data-baseweb="select"] > div {
        background-color: #1a1a1a;
        border-color: #333;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. YARDIMCI FONKSİYONLAR VE STATE ---

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

def fetch_artworks_page(query, page_num):
    """Belirli bir sayfadaki eserleri getirir"""
    new_artworks = []
    
    # 1. Chicago API (Pagination Destekler)
    try:
        url = f"https://api.artic.edu/api/v1/artworks/search?q={query}&page={page_num}&limit=3&fields=id,title,image_id,artist_display,date_display&query[term][is_public_domain]=true"
        r = requests.get(url, timeout=3).json()
        new_artworks.extend([normalize_chicago(i) for i in r['data'] if normalize_chicago(i)])
    except Exception as e:
        pass # Hata olursa sessizce geç

    # 2. Cleveland API (Skip/Offset Destekler)
    try:
        skip_val = (page_num - 1) * 3
        url = f"https://openaccess-api.clevelandart.org/api/artworks/?q={query}&skip={skip_val}&limit=3&has_image=1"
        r = requests.get(url, timeout=3).json()
        new_artworks.extend([normalize_cleveland(i) for i in r['data'] if normalize_cleveland(i)])
    except:
        pass

    # 3. The Met (Cache'lenmiş ID listesinden dilimleme yapar)
    # Eğer Met ID listesi boşsa veya sorgu değiştiyse güncelle
    if not st.session_state.met_ids:
        st.session_state.met_ids = search_met_ids_cached(query)
    
    # Sayfaya göre ID listesinden kesit al (Örn: Sayfa 1 için 0-3, Sayfa 2 için 3-6)
    if st.session_state.met_ids:
        start_idx = (page_num - 1) * 3
        end_idx = start_idx + 3
        
        target_ids = st.session_state.met_ids[start_idx:end_idx]
        
        if target_ids:
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                results = list(executor.map(fetch_met_details, target_ids))
            new_artworks.extend([res for res in results if res])

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
