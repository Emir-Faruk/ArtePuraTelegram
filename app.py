import streamlit as st
import requests
import random
import streamlit.components.v1 as components

# --- 1. KONFİGÜRASYON VE TASARIM SİSTEMİ ---
st.set_page_config(
    page_title="Arte Pura",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- TELEGRAM ENTEGRASYONU (JS INJECTION) ---
# Bu blok, uygulamanın Telegram içinde tam ekran açılmasını sağlar
components.html("""
<script src="https://telegram.org/js/telegram-web-app.js"></script>
<script>
    // Telegram WebApp hazır olduğunda çalışır
    window.Telegram.WebApp.ready();
    window.Telegram.WebApp.expand(); // Uygulamayı tam boyuta genişlet
    
    // Tema renklerini ayarla
    window.Telegram.WebApp.setHeaderColor('#0f0f0f');
    window.Telegram.WebApp.setBackgroundColor('#0f0f0f');
</script>
""", height=0)

# "Museum Dark" Teması İçin Özel CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=Inter:wght@300;400;600&display=swap');

    /* Ana Arka Plan ve Telegram Uyumu */
    .stApp {
        background-color: #0f0f0f;
        color: #e0e0e0;
        font-family: 'Inter', sans-serif;
    }

    /* Streamlit'in kendi header ve footer'ını gizle */
    header {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    .stDeployButton {display:none;}
    #MainMenu {visibility: hidden;}

    /* Başlıklar */
    h1, h2, h3 {
        font-family: 'Playfair Display', serif !important;
        color: #e0e0e0 !important;
    }

    /* Görsel Kartları */
    div[data-testid="stImage"] {
        border-radius: 8px;
        overflow: hidden;
        transition: transform 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5);
    }
    
    /* Mobil Uyumlu Butonlar */
    .stButton > button {
        background-color: rgba(255, 255, 255, 0.05);
        color: #e0e0e0;
        border: 1px solid rgba(255, 255, 255, 0.1);
        width: 100%;
        padding: 0.5rem 1rem;
    }
    .stButton > button:active {
        background-color: #d4af37 !important;
        color: black !important;
    }

    /* Input Alanı */
    .stTextInput > div > div > input {
        background-color: #1a1a1a;
        color: white;
        border: 1px solid #333;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. API FONKSİYONLARI ---

def safe_str(val):
    if val is None: return ""
    if isinstance(val, list): return ", ".join([str(v) for v in val])
    return str(val)

def normalize_chicago(item):
    if not item.get('image_id'): return None
    iiif_url = "https://www.artic.edu/iiif/2"
    return {
        'id': f"chi-{item['id']}",
        'source': 'Chicago Art Inst.',
        'title': safe_str(item.get('title')),
        'artist': safe_str(item.get('artist_display', 'Bilinmeyen Sanatçı').split('\n')[0]),
        'date': safe_str(item.get('date_display')),
        'medium': safe_str(item.get('medium_display')),
        'dimensions': safe_str(item.get('dimensions')),
        'credit': safe_str(item.get('credit_line')),
        'thumbnail': f"{iiif_url}/{item['image_id']}/full/400,/0/default.jpg",
        'high_res': f"{iiif_url}/{item['image_id']}/full/843,/0/default.jpg",
        'link': f"https://www.artic.edu/artworks/{item['id']}"
    }

def normalize_cleveland(item):
    images = item.get('images')
    if not images or not images.get('web'): return None
    
    creators = item.get('creators', [])
    artist_name = creators[0].get('description', 'Bilinmeyen Sanatçı') if creators else 'Bilinmeyen Sanatçı'
    
    return {
        'id': f"cle-{item['id']}",
        'source': 'Cleveland Museum',
        'title': safe_str(item.get('title')),
        'artist': safe_str(artist_name),
        'date': safe_str(item.get('creation_date')),
        'medium': safe_str(item.get('technique')),
        'dimensions': safe_str(item.get('dimensions')),
        'credit': safe_str(item.get('creditline')),
        'thumbnail': images['web']['url'],
        'high_res': images['print']['url'] if images.get('print') else images['web']['url'],
        'link': item.get('url', '#')
    }

@st.cache_data(show_spinner=False, ttl=3600)
def fetch_artworks(query, offset=0):
    limit = 10 
    artworks = []
    
    try:
        page = (offset // limit) + 1
        url = f"https://api.artic.edu/api/v1/artworks/search?q={query}&page={page}&limit={limit}&fields=id,title,image_id,artist_display,date_display,medium_display,dimensions,credit_line&query[term][is_public_domain]=true"
        r = requests.get(url, timeout=3)
        if r.status_code == 200:
            data = r.json().get('data', [])
            artworks.extend([normalize_chicago(i) for i in data if normalize_chicago(i)])
    except: pass

    try:
        url = f"https://openaccess-api.clevelandart.org/api/artworks/?q={query}&skip={offset}&limit={limit}&has_image=1"
        r = requests.get(url, timeout=3)
        if r.status_code == 200:
            data = r.json().get('data', [])
            artworks.extend([normalize_cleveland(i) for i in data if normalize_cleveland(i)])
    except: pass

    random.shuffle(artworks)
    return artworks

# --- 3. STATE YÖNETİMİ ---
if 'artworks' not in st.session_state: st.session_state.artworks = []
if 'offset' not in st.session_state: st.session_state.offset = 0
if 'selected_art' not in st.session_state: st.session_state.selected_art = None
if 'query' not in st.session_state: st.session_state.query = "Impressionism"

# --- 4. ARAYÜZ (UI) ---

# Header
st.markdown("""
<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;">
    <div style="font-size:20px; color:#d4af37; font-family:'Playfair Display', serif;">Arte Pura</div>
    <div style="font-size:10px; color:#666;">PY</div>
</div>
""", unsafe_allow_html=True)

# Arama Çubuğu
new_query = st.text_input("Ara", placeholder="Sanatçı veya dönem...", label_visibility="collapsed")
if new_query and new_query != st.session_state.query:
    st.session_state.query = new_query
    st.session_state.offset = 0
    st.session_state.artworks = []
    st.session_state.selected_art = None
    st.rerun()

# Detay Görünümü
if st.session_state.selected_art:
    art = st.session_state.selected_art
    with st.container():
        if st.button("← Listeye Dön"):
            st.session_state.selected_art = None
            st.rerun()
        
        st.image(art['high_res'], use_container_width=True)
        st.markdown(f"""
        <div style="padding:15px; background:#1a1a1a; border-radius:8px; margin-top:10px;">
            <h3 style="color:#d4af37; margin:0;">{art['title']}</h3>
            <p style="color:#aaa; font-size:14px;">{art['artist']}</p>
            <hr style="border-color:#333;">
            <p style="font-size:12px; color:#888;">{art['date']} • {art['source']}</p>
        </div>
        """, unsafe_allow_html=True)
    st.stop() # Detay açıkken listeyi gösterme

# Liste Görünümü
if not st.session_state.artworks:
    with st.spinner('Yükleniyor...'):
        new_items = fetch_artworks(st.session_state.query, st.session_state.offset)
        st.session_state.artworks.extend(new_items)

# Mobil için 2 sütunlu yapı
cols = st.columns(2)
for i, art in enumerate(st.session_state.artworks):
    with cols[i % 2]:
        st.image(art['thumbnail'], use_container_width=True)
        if st.button(f"İncele", key=f"btn_{art['id']}"):
            st.session_state.selected_art = art
            st.rerun()

# Daha Fazla Butonu
st.markdown("<br>", unsafe_allow_html=True)
if st.button("Daha Fazla Göster +"):
    st.session_state.offset += 10
    with st.spinner('Yükleniyor...'):
        new_items = fetch_artworks(st.session_state.query, st.session_state.offset)
        st.session_state.artworks.extend(new_items)
    st.rerun()