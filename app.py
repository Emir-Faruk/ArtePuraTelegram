import streamlit as st
import requests
import random
from PIL import Image
from io import BytesIO
import streamlit.components.v1 as components

# --- 1. KONFİGÜRASYON ---
st.set_page_config(
    page_title="Arte Pura",
    page_icon="🎨",
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

# --- CSS / TASARIM SİSTEMİ ---
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
    
    /* Etiket Butonları (Pills) */
    div.stButton > button.pill-btn {
        border-radius: 20px;
        border: 1px solid #333;
        background: #1a1a1a;
        color: #aaa;
        font-size: 12px;
        padding: 4px 12px;
    }
    div.stButton > button.pill-btn:hover {
        border-color: #d4af37;
        color: #d4af37;
    }

    /* Renk Paleti Kutuları */
    .color-box {
        width: 100%;
        height: 40px;
        border-radius: 4px;
        margin-bottom: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        transition: transform 0.2s;
    }
    .color-box:hover { transform: scale(1.05); }

    /* Ana Butonlar */
    .stButton > button {
        background-color: rgba(255, 255, 255, 0.05);
        color: #e0e0e0;
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: all 0.3s;
    }
    .stButton > button:hover {
        border-color: #d4af37;
        color: #d4af37;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. YARDIMCI FONKSİYONLAR ---

def safe_str(val):
    if val is None: return ""
    if isinstance(val, list): return ", ".join([str(v) for v in val])
    return str(val)

# Renk Paleti Çıkarıcı (Basit ve Hızlı)
@st.cache_data(show_spinner=False)
def extract_palette(image_url, num_colors=5):
    try:
        response = requests.get(image_url, timeout=5)
        img = Image.open(BytesIO(response.content))
        img = img.resize((150, 150)) # Hız için küçült
        result = img.convert('P', palette=Image.ADAPTIVE, colors=num_colors)
        result.putalpha(0)
        colors = result.getcolors(150*150)
        # Renkleri sıklığa göre sırala ve hex koduna çevir
        hex_colors = []
        for count, col in sorted(colors, reverse=True):
            hex_colors.append('#{:02x}{:02x}{:02x}'.format(col[0], col[1], col[2]))
        return hex_colors
    except:
        return []

# API Normalizasyon (Önceki koddan)
def normalize_chicago(item):
    if not item.get('image_id'): return None
    iiif = "https://www.artic.edu/iiif/2"
    return {
        'id': f"chi-{item['id']}",
        'source': 'Chicago Art Inst.',
        'title': safe_str(item.get('title')),
        'artist': safe_str(item.get('artist_display', 'Unknown').split('\n')[0]),
        'date': safe_str(item.get('date_display')),
        'thumb': f"{iiif}/{item['image_id']}/full/400,/0/default.jpg",
        'high_res': f"{iiif}/{item['image_id']}/full/843,/0/default.jpg",
        'link': f"https://www.artic.edu/artworks/{item['id']}"
    }

def normalize_cleveland(item):
    if not item.get('images') or not item.get('images').get('web'): return None
    creators = item.get('creators', [])
    artist = creators[0].get('description', 'Unknown') if creators else 'Unknown'
    return {
        'id': f"cle-{item['id']}",
        'source': 'Cleveland Museum',
        'title': safe_str(item.get('title')),
        'artist': safe_str(artist),
        'date': safe_str(item.get('creation_date')),
        'thumb': item['images']['web']['url'],
        'high_res': item['images']['print']['url'] if item['images'].get('print') else item['images']['web']['url'],
        'link': item.get('url', '#')
    }

@st.cache_data(show_spinner=False, ttl=3600)
def fetch_artworks(query):
    artworks = []
    # Chicago
    try:
        url = f"https://api.artic.edu/api/v1/artworks/search?q={query}&limit=8&fields=id,title,image_id,artist_display,date_display&query[term][is_public_domain]=true"
        r = requests.get(url, timeout=2).json()
        artworks.extend([normalize_chicago(i) for i in r['data'] if normalize_chicago(i)])
    except: pass
    # Cleveland
    try:
        url = f"https://openaccess-api.clevelandart.org/api/artworks/?q={query}&limit=8&has_image=1"
        r = requests.get(url, timeout=2).json()
        artworks.extend([normalize_cleveland(i) for i in r['data'] if normalize_cleveland(i)])
    except: pass
    
    random.shuffle(artworks)
    return artworks

# --- 3. STATE ---
if 'view' not in st.session_state: st.session_state.view = 'list'
if 'selected_art' not in st.session_state: st.session_state.selected_art = None
if 'query' not in st.session_state: st.session_state.query = "Impressionism"
if 'artworks' not in st.session_state: st.session_state.artworks = []

# --- 4. ARAYÜZ ---

# Header (Logo & Rastgele Keşif)
c1, c2 = st.columns([3, 1])
with c1:
    st.markdown('<div style="font-family:Playfair Display; font-size:24px; color:#d4af37;">Arte Pura <span style="font-size:12px; color:#666;">PRO</span></div>', unsafe_allow_html=True)
with c2:
    if st.button("🎲", help="Rastgele Eser"):
        topics = ["Surrealism", "Renaissance", "Ukiyo-e", "Abstract", "Portrait", "Landscape", "Baroque"]
        st.session_state.query = random.choice(topics)
        st.session_state.artworks = [] # Reset to force fetch
        st.session_state.view = 'list'
        st.rerun()

# --- DETAY GÖRÜNÜMÜ ---
if st.session_state.view == 'detail' and st.session_state.selected_art:
    art = st.session_state.selected_art
    
    # Geri Dön Butonu (Üstte, soluk)
    if st.button("← Galeriy Dön", key="back_btn"):
        st.session_state.view = 'list'
        st.rerun()

    # Görsel ve Bilgi
    st.image(art['high_res'], use_container_width=True)
    
    st.markdown(f"""
    <div style="margin-top:15px; margin-bottom:5px;">
        <h2 style="margin:0; font-size:22px; color:#e0e0e0;">{art['title']}</h2>
        <p style="color:#d4af37; font-family:'Playfair Display',serif; font-style:italic;">{art['artist']}</p>
    </div>
    """, unsafe_allow_html=True)

    # Sekmeler (Tabs) ile Düzenli Bilgi
    tab1, tab2 = st.tabs(["🎨 Renk DNA'sı", "ℹ️ Detaylar"])
    
    with tab1:
        st.caption("Yapay zeka bu eserin baskın renklerini analiz ediyor...")
        palette = extract_palette(art['thumb']) # Küçük resimden hızlı analiz
        if palette:
            cols = st.columns(5)
            for i, color in enumerate(palette):
                with cols[i]:
                    st.markdown(f'<div class="color-box" style="background-color:{color};"></div>', unsafe_allow_html=True)
                    st.caption(f"{color}")
        else:
            st.warning("Renk analizi yapılamadı.")

    with tab2:
        st.markdown(f"""
        <div style="background:#1a1a1a; padding:15px; border-radius:8px; font-size:13px; color:#aaa;">
            <p><strong>Dönem:</strong> {art['date']}</p>
            <p><strong>Kaynak:</strong> {art['source']}</p>
            <hr style="border-color:#333;">
            <a href="{art['link']}" target="_blank" style="color:#fff; text-decoration:none;">🔗 Müze Arşivine Git</a>
        </div>
        """, unsafe_allow_html=True)
        
    # İndirme Butonu (Wallpaper için)
    st.markdown("<br>", unsafe_allow_html=True)
    try:
        # İndirme butonu için binary veriyi çekiyoruz
        img_data = requests.get(art['high_res']).content
        st.download_button(
            label="Duvar Kağıdı Olarak İndir (HD)",
            data=img_data,
            file_name=f"arte_pura_{art['id']}.jpg",
            mime="image/jpeg",
            use_container_width=True
        )
    except:
        pass

# --- LİSTE GÖRÜNÜMÜ ---
else:
    # Akıllı Filtreler (Pills)
    tags = ["Impressionism", "Van Gogh", "Japanese Art", "Sculpture", "Bauhaus", "Modernism"]
    cols_tags = st.columns(len(tags))
    # Yatay scroll yerine grid buton mantığı
    selected_tag = None
    
    st.markdown('<div style="display:flex; gap:10px; overflow-x:auto; padding-bottom:10px;">', unsafe_allow_html=True)
    # Streamlit'te yan yana buton zor olduğu için columns kullandık
    # Ancak mobil için selectbox daha iyi olabilir
    
    filter_choice = st.selectbox("Küratör Seçkileri:", ["Kişisel Arama Yap..."] + tags, label_visibility="collapsed")
    
    if filter_choice != "Kişisel Arama Yap..." and filter_choice != st.session_state.query:
        st.session_state.query = filter_choice
        st.session_state.artworks = []
        st.rerun()

    # Arama
    if filter_choice == "Kişisel Arama Yap...":
        search_input = st.text_input("Özel Arama", value="", placeholder="Örn: The Kiss, Klimt...", label_visibility="collapsed")
        if search_input and search_input != st.session_state.query:
            st.session_state.query = search_input
            st.session_state.artworks = []
            st.rerun()

    st.markdown(f"<p style='font-size:12px; color:#666; margin-top:10px;'>Şu an gösteriliyor: <span style='color:#d4af37'>{st.session_state.query}</span></p>", unsafe_allow_html=True)

    # Veri Yükleme
    if not st.session_state.artworks:
        with st.spinner('Sanat eserleri taranıyor...'):
            st.session_state.artworks = fetch_artworks(st.session_state.query)

    # Masonry Grid (2 Sütun Mobil İçin İdeal)
    c1, c2 = st.columns(2)
    for i, art in enumerate(st.session_state.artworks):
        col = c1 if i % 2 == 0 else c2
        with col:
            with st.container():
                st.image(art['thumb'], use_container_width=True)
                if st.button(f"{art['title'][:20]}...", key=f"list_{art['id']}"):
                    st.session_state.selected_art = art
                    st.session_state.view = 'detail'
                    st.rerun()
                st.markdown("<div style='margin-bottom:20px;'></div>", unsafe_allow_html=True)

    if st.button("Daha Fazla Keşfet", use_container_width=True):
        st.session_state.artworks = [] # Basitçe yenile (pagination yerine shuffle discovery)
        st.rerun()
