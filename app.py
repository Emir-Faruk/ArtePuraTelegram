import streamlit as st
import requests
import random
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
    
    /* Butonları Görselin Parçası Gibi Gösterme */
    div.stButton > button {
        background-color: #1a1a1a;
        color: #d4af37;
        border: 1px solid #333;
        border-top: none; /* Görselle birleşmesi için */
        border-radius: 0 0 8px 8px; /* Sadece alt köşeler oval */
        width: 100%;
        padding: 10px;
        font-family: 'Inter', sans-serif;
        font-size: 14px;
        transition: all 0.3s;
        text-align: left; /* Metni sola hizala */
    }
    div.stButton > button:hover {
        background-color: #222;
        border-color: #d4af37;
        color: #fff;
    }
    
    /* Görsellerin Kenarları */
    div[data-testid="stImage"] img {
        border-radius: 8px 8px 0 0 !important; /* Sadece üst köşeler oval */
        border: 1px solid #333;
        border-bottom: none;
    }
    
    /* Selectbox Stili */
    div[data-baseweb="select"] > div {
        background-color: #1a1a1a;
        border-color: #333;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. YARDIMCI FONKSİYONLAR ---

def safe_str(val):
    if val is None: return ""
    if isinstance(val, list): return ", ".join([str(v) for v in val])
    return str(val)

# API Normalizasyon (Yüksek Kalite Ayarları)
def normalize_chicago(item):
    if not item.get('image_id'): return None
    iiif = "https://www.artic.edu/iiif/2"
    return {
        'id': f"chi-{item['id']}",
        'source': 'Chicago Art Inst.',
        'title': safe_str(item.get('title')),
        'artist': safe_str(item.get('artist_display', 'Unknown').split('\n')[0]),
        'date': safe_str(item.get('date_display')),
        # Listeleme için orta boy
        'thumbnail': f"{iiif}/{item['image_id']}/full/600,/0/default.jpg",
        # Detay için ULTRA HD (1686px veya Full)
        'high_res': f"{iiif}/{item['image_id']}/full/1686,/0/default.jpg", 
        'link': f"https://www.artic.edu/artworks/{item['id']}"
    }

def normalize_cleveland(item):
    if not item.get('images') or not item.get('images').get('web'): return None
    creators = item.get('creators', [])
    artist = creators[0].get('description', 'Unknown') if creators else 'Unknown'
    
    # Cleveland'da en yüksek kaliteyi bulma mantığı
    high_res_url = item['images']['web']['url'] # Fallback
    if 'print' in item['images']:
        high_res_url = item['images']['print']['url']
    elif 'full' in item['images']:
         high_res_url = item['images']['full']['url']
         
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

@st.cache_data(show_spinner=False, ttl=3600)
def fetch_artworks(query):
    artworks = []
    # Chicago
    try:
        url = f"https://api.artic.edu/api/v1/artworks/search?q={query}&limit=12&fields=id,title,image_id,artist_display,date_display&query[term][is_public_domain]=true"
        r = requests.get(url, timeout=3).json()
        artworks.extend([normalize_chicago(i) for i in r['data'] if normalize_chicago(i)])
    except: pass
    # Cleveland
    try:
        url = f"https://openaccess-api.clevelandart.org/api/artworks/?q={query}&limit=12&has_image=1"
        r = requests.get(url, timeout=3).json()
        artworks.extend([normalize_cleveland(i) for i in r['data'] if normalize_cleveland(i)])
    except: pass
    
    random.shuffle(artworks)
    return artworks

# --- 3. ZOOMABLE IMAGE COMPONENT (HTML/JS) ---
# Streamlit'in native image'i zoom desteklemez. Bu yüzden kendi HTML bileşenimizi oluşturuyoruz.
def zoomable_image(src, alt):
    html_code = f"""
    <!DOCTYPE html>
    <html style="height: 100%; margin: 0;">
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes">
        <style>
            body {{
                margin: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                background-color: #0f0f0f;
                height: 100vh;
                overflow: hidden;
            }}
            .image-container {{
                width: 100%;
                height: 100%;
                overflow: auto; /* Scrolla izin ver */
                display: flex;
                justify-content: center;
                align-items: center;
                cursor: grab;
            }}
            img {{
                max-width: 100%;
                max-height: 100%;
                object-fit: contain;
                transition: transform 0.2s ease;
                box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            }}
            /* Zoom Kontrolleri */
            .controls {{
                position: fixed;
                bottom: 20px;
                right: 20px;
                display: flex;
                gap: 10px;
                z-index: 100;
            }}
            .btn {{
                background: rgba(255,255,255,0.1);
                color: white;
                border: 1px solid rgba(255,255,255,0.2);
                padding: 10px 15px;
                border-radius: 50%;
                cursor: pointer;
                font-size: 18px;
                backdrop-filter: blur(5px);
            }}
        </style>
    </head>
    <body>
        <div class="image-container" id="container">
            <img src="{src}" alt="{alt}" id="zoom-img">
        </div>
        
        <div class="controls">
            <button class="btn" onclick="zoomOut()">-</button>
            <button class="btn" onclick="zoomIn()">+</button>
        </div>

        <script>
            let scale = 1;
            const img = document.getElementById('zoom-img');
            const container = document.getElementById('container');
            
            function zoomIn() {{
                scale += 0.5;
                applyZoom();
            }}
            
            function zoomOut() {{
                if (scale > 1) {{
                    scale -= 0.5;
                    applyZoom();
                }}
            }}
            
            function applyZoom() {{
                img.style.transform = `scale(${{scale}})`;
                img.style.cursor = scale > 1 ? 'grab' : 'default';
                
                // Zoom yapıldığında scroll barların çalışması için
                if(scale > 1) {{
                    container.style.alignItems = 'flex-start';
                    container.style.justifyContent = 'flex-start';
                    img.style.maxWidth = 'none';
                    img.style.maxHeight = 'none';
                }} else {{
                    container.style.alignItems = 'center';
                    container.style.justifyContent = 'center';
                    img.style.maxWidth = '100%';
                    img.style.maxHeight = '100%';
                }}
            }}
            
            // Çift tıklama / Dokunma ile Zoom
            let lastTouchEnd = 0;
            container.addEventListener('touchend', function (event) {{
                const now = (new Date()).getTime();
                if (now - lastTouchEnd <= 300) {{
                    event.preventDefault();
                    if(scale === 1) {{ scale = 2.5; }} else {{ scale = 1; }}
                    applyZoom();
                }}
                lastTouchEnd = now;
            }}, false);
            
            container.addEventListener('dblclick', function() {{
                 if(scale === 1) {{ scale = 2.5; }} else {{ scale = 1; }}
                 applyZoom();
            }});
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=500) # Yükseklik ayarlanabilir

# --- 4. STATE ---
if 'view' not in st.session_state: st.session_state.view = 'list'
if 'selected_art' not in st.session_state: st.session_state.selected_art = None
if 'query' not in st.session_state: st.session_state.query = "Impressionism"
if 'artworks' not in st.session_state: st.session_state.artworks = []

# --- 5. ARAYÜZ ---

# Header (Logo & Rastgele Keşif)
c1, c2 = st.columns([3, 1])
with c1:
    st.markdown('<div style="font-family:Playfair Display; font-size:24px; color:#d4af37;">Arte Pura <span style="font-size:12px; color:#666;">HD</span></div>', unsafe_allow_html=True)
with c2:
    if st.button("🎲", help="Rastgele"):
        topics = ["Surrealism", "Renaissance", "Ukiyo-e", "Abstract", "Portrait", "Baroque", "Cubism"]
        st.session_state.query = random.choice(topics)
        st.session_state.artworks = [] 
        st.session_state.view = 'list'
        st.rerun()

# --- DETAY GÖRÜNÜMÜ (ZOOM AKTİF) ---
if st.session_state.view == 'detail' and st.session_state.selected_art:
    art = st.session_state.selected_art
    
    if st.button("← Geri Dön", key="back_btn"):
        st.session_state.view = 'list'
        st.rerun()

    # ÖZEL ZOOM BİLEŞENİ
    # Burası artık statik st.image değil, özel HTML
    zoomable_image(art['high_res'], art['title'])
    
    st.markdown(f"""
    <div style="margin-top:15px; margin-bottom:5px;">
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
        
    st.markdown("<br>", unsafe_allow_html=True)
    try:
        # İndirme Butonu
        img_data = requests.get(art['high_res']).content
        st.download_button(
            label="Eseri HD İndir",
            data=img_data,
            file_name=f"arte_pura_{art['id']}.jpg",
            mime="image/jpeg",
            use_container_width=True
        )
    except:
        pass

# --- LİSTE GÖRÜNÜMÜ ---
else:
    # Filtreler
    tags = ["Impressionism", "Van Gogh", "Japanese Art", "Sculpture", "Bauhaus", "Modernism"]
    filter_choice = st.selectbox("Koleksiyonlar:", ["Kişisel Arama Yap..."] + tags, label_visibility="collapsed")
    
    if filter_choice != "Kişisel Arama Yap..." and filter_choice != st.session_state.query:
        st.session_state.query = filter_choice
        st.session_state.artworks = []
        st.rerun()

    if filter_choice == "Kişisel Arama Yap...":
        search_input = st.text_input("Arama", value="", placeholder="Ressam, dönem...", label_visibility="collapsed")
        if search_input and search_input != st.session_state.query:
            st.session_state.query = search_input
            st.session_state.artworks = []
            st.rerun()

    st.markdown(f"<p style='font-size:12px; color:#666; margin-top:5px; margin-bottom:15px;'>Seçim: <span style='color:#d4af37'>{st.session_state.query}</span></p>", unsafe_allow_html=True)

    if not st.session_state.artworks:
        with st.spinner('Yüksek kaliteli eserler hazırlanıyor...'):
            st.session_state.artworks = fetch_artworks(st.session_state.query)

    # Masonry Grid (Kart Yapısı)
    c1, c2 = st.columns(2)
    for i, art in enumerate(st.session_state.artworks):
        col = c1 if i % 2 == 0 else c2
        with col:
            # Burası "Kart" yapısının oluşturulduğu yer
            # Görsel ve Butonu tek bir blok gibi gösteriyoruz (CSS ile birleşiyorlar)
            img_url = art.get('thumbnail', '')
            if img_url:
                st.image(img_url, use_container_width=True)
            
            # Buton artık görselin hemen altında, görselin açıklaması gibi davranıyor
            # Tıklanınca görsel açılıyor hissi verir
            btn_label = f"👁️ {art['title'][:15]}..." 
            if st.button(btn_label, key=f"btn_{art['id']}"):
                st.session_state.selected_art = art
                st.session_state.view = 'detail'
                st.rerun()
            
            st.markdown("<div style='margin-bottom:15px;'></div>", unsafe_allow_html=True)

    if st.button("Daha Fazla Keşfet", use_container_width=True):
        st.session_state.artworks = []
        st.rerun()
