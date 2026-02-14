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
    
    /* Görsel Kenarları */
    div[data-testid="stImage"] img {
        border-radius: 8px 8px 0 0 !important;
        border: 1px solid #333;
        border-bottom: none;
    }
    
    /* Selectbox */
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

# API Normalizasyon
def normalize_chicago(item):
    if not item.get('image_id'): return None
    iiif = "https://www.artic.edu/iiif/2"
    return {
        'id': f"chi-{item['id']}",
        'source': 'Chicago Art Inst.',
        'title': safe_str(item.get('title')),
        'artist': safe_str(item.get('artist_display', 'Unknown').split('\n')[0]),
        'date': safe_str(item.get('date_display')),
        'thumbnail': f"{iiif}/{item['image_id']}/full/600,/0/default.jpg",
        'high_res': f"{iiif}/{item['image_id']}/full/1686,/0/default.jpg", 
        'link': f"https://www.artic.edu/artworks/{item['id']}"
    }

def normalize_cleveland(item):
    if not item.get('images') or not item.get('images').get('web'): return None
    creators = item.get('creators', [])
    artist = creators[0].get('description', 'Unknown') if creators else 'Unknown'
    
    high_res_url = item['images']['web']['url']
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
    try:
        url = f"https://api.artic.edu/api/v1/artworks/search?q={query}&limit=12&fields=id,title,image_id,artist_display,date_display&query[term][is_public_domain]=true"
        r = requests.get(url, timeout=3).json()
        artworks.extend([normalize_chicago(i) for i in r['data'] if normalize_chicago(i)])
    except: pass
    try:
        url = f"https://openaccess-api.clevelandart.org/api/artworks/?q={query}&limit=12&has_image=1"
        r = requests.get(url, timeout=3).json()
        artworks.extend([normalize_cleveland(i) for i in r['data'] if normalize_cleveland(i)])
    except: pass
    random.shuffle(artworks)
    return artworks

# --- 3. PRO ZOOM & FULLSCREEN BILEŞENI ---
def zoomable_image_pro(src, alt):
    html_code = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <script src="https://unpkg.com/@panzoom/panzoom@4.5.1/dist/panzoom.min.js"></script>
        <style>
            html, body {{
                margin: 0;
                padding: 0;
                background-color: #000;
                height: 100vh;
                width: 100vw;
                overflow: hidden; /* Scrollbarları engelle */
            }}
            #scene {{
                width: 100vw;
                height: 100vh;
                display: flex;
                justify-content: center; /* Yatay Ortala */
                align-items: center;     /* Dikey Ortala */
            }}
            img {{
                max-width: 100%;
                max-height: 100%;
                object-fit: contain; /* Orantılı sığdır */
                transform-origin: center center; /* Zoom merkezden başlasın */
                cursor: grab;
            }}
            img:active {{
                cursor: grabbing;
            }}
            
            /* Kontrol Paneli */
            .controls {{
                position: fixed;
                bottom: 20px;
                left: 50%;
                transform: translateX(-50%);
                display: flex;
                gap: 15px;
                background: rgba(25, 25, 25, 0.8);
                padding: 10px 20px;
                border-radius: 30px;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                z-index: 100;
            }}
            
            .btn {{
                background: transparent;
                border: none;
                color: #e0e0e0;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                width: 24px;
                height: 24px;
                transition: transform 0.2s, color 0.2s;
            }}
            .btn:hover {{ color: #d4af37; transform: scale(1.1); }}
            .btn svg {{ width: 20px; height: 20px; fill: currentColor; }}
            
            /* Fullscreen İkonu Sağ Alta */
            .fs-btn {{
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: rgba(25, 25, 25, 0.6);
                width: 40px;
                height: 40px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                border: 1px solid rgba(255, 255, 255, 0.1);
                color: white;
                cursor: pointer;
                backdrop-filter: blur(5px);
                z-index: 101;
            }}
            .fs-btn:hover {{ background: #d4af37; color: black; }}

        </style>
    </head>
    <body>
        <div id="scene">
            <img src="{src}" alt="{alt}" id="target">
        </div>

        <!-- Şık Kontroller -->
        <div class="controls">
            <button class="btn" id="zoom-out" title="Uzaklaş">
                <svg viewBox="0 0 24 24"><path d="M19 13H5v-2h14v2z"/></svg>
            </button>
            <button class="btn" id="reset" title="Sıfırla">
                <svg viewBox="0 0 24 24"><path d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/></svg>
            </button>
            <button class="btn" id="zoom-in" title="Yakınlaş">
                <svg viewBox="0 0 24 24"><path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/></svg>
            </button>
        </div>

        <!-- Tam Ekran Butonu -->
        <button class="fs-btn" id="fullscreen" title="Tam Ekran">
             <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M7 14H5v5h5v-2H7v-3zm-2-4h2V7h3V5H5v5zm12 7h-3v2h5v-5h-2v3zM14 5v2h3v3h2V5h-5z"/></svg>
        </button>

        <script>
            const elem = document.getElementById('target');
            const scene = document.getElementById('scene');
            
            // Panzoom Başlat
            const panzoom = Panzoom(elem, {{
                maxScale: 5,
                minScale: 0.5,
                contain: false, // Flexbox ortalaması için false yaptık (önceki 'outside' bozuyordu)
                startScale: 1,
                animate: true
            }});

            // Resim tamamen yüklendiğinde ve boyutlandığında tekrar resetle
            // Bu, görselin ilk açılışta ortalanmasını garanti eder
            elem.onload = function() {{
                panzoom.reset();
            }};

            // Mouse Tekerleği
            scene.addEventListener('wheel', panzoom.zoomWithWheel);

            // Buton Bağlantıları
            document.getElementById('zoom-in').addEventListener('click', panzoom.zoomIn);
            document.getElementById('zoom-out').addEventListener('click', panzoom.zoomOut);
            document.getElementById('reset').addEventListener('click', panzoom.reset);

            // Çift Tıklama = Zoom / Reset
            elem.addEventListener('dblclick', function(e) {{
                if(panzoom.getScale() > 1) {{
                    panzoom.reset();
                }} else {{
                    panzoom.zoomToPoint(2, {{ clientX: e.clientX, clientY: e.clientY }});
                }}
            }});

            // Tam Ekran Mantığı
            const fsBtn = document.getElementById('fullscreen');
            fsBtn.addEventListener('click', function() {{
                if (!document.fullscreenElement) {{
                    document.body.requestFullscreen().catch(err => {{
                        console.log(err);
                    }});
                }} else {{
                    document.exitFullscreen();
                }}
            }});
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=650)

# --- 4. STATE ---
if 'view' not in st.session_state: st.session_state.view = 'list'
if 'selected_art' not in st.session_state: st.session_state.selected_art = None
if 'query' not in st.session_state: st.session_state.query = "Impressionism"
if 'artworks' not in st.session_state: st.session_state.artworks = []

# --- 5. ARAYÜZ ---

# Header
c1, c2 = st.columns([3, 1])
with c1:
    st.markdown('<div style="font-family:Playfair Display; font-size:24px; color:#d4af37;">Arte Pura <span style="font-size:12px; color:#666;">ULTIMATE</span></div>', unsafe_allow_html=True)
with c2:
    if st.button("🎲", help="Rastgele"):
        topics = ["Surrealism", "Renaissance", "Ukiyo-e", "Abstract", "Portrait", "Baroque", "Cubism"]
        st.session_state.query = random.choice(topics)
        st.session_state.artworks = [] 
        st.session_state.view = 'list'
        st.rerun()

# --- DETAY GÖRÜNÜMÜ ---
if st.session_state.view == 'detail' and st.session_state.selected_art:
    art = st.session_state.selected_art
    
    if st.button("← Geri Dön", key="back_btn"):
        st.session_state.view = 'list'
        st.rerun()

    # Yeni Pro Zoom Bileşeni
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
        
    st.markdown("<br>", unsafe_allow_html=True)
    try:
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

    # Grid
    c1, c2 = st.columns(2)
    for i, art in enumerate(st.session_state.artworks):
        col = c1 if i % 2 == 0 else c2
        with col:
            img_url = art.get('thumbnail', '')
            if img_url:
                st.image(img_url, use_container_width=True)
            
            btn_label = f"👁️ {art['title'][:15]}..." 
            if st.button(btn_label, key=f"btn_{art['id']}"):
                st.session_state.selected_art = art
                st.session_state.view = 'detail'
                st.rerun()
            
            st.markdown("<div style='margin-bottom:15px;'></div>", unsafe_allow_html=True)

    if st.button("Daha Fazla Keşfet", use_container_width=True):
        st.session_state.artworks = []
        st.rerun()
