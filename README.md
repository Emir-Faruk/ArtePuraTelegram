# 🎨 Arte Pura

A beautiful Streamlit application that aggregates high-quality art images from 12 world-class museum APIs, optimized for Telegram Mini Apps.

## ✨ Features

- **12 Museum APIs**: Access artworks from Chicago Art Institute, Cleveland Museum, The Met, Rijksmuseum, Harvard Art Museums, Smithsonian, Europeana, Cooper Hewitt, Brooklyn Museum, V&A, The Getty, and National Gallery of Art
- **Deep Zoom with OpenSeadragon**: IIIF-powered tile-based zooming for ultra-high-resolution artwork viewing inspired by the Bosch Project
- **Concurrent Fetching**: Fast loading with parallel API calls using ThreadPoolExecutor (12 workers)
- **High-Resolution Images**: IIIF protocol support with images up to 2048px and beyond
- **Color Palette Display**: View prominent colors extracted from artworks (Cleveland, Harvard)
- **Rich Metadata**: Physical dimensions and detailed artwork information
- **Responsive Design**: Works beautifully on all devices with custom zoom controls
- **Telegram Integration**: Fully optimized for Telegram Mini Apps
- **Smart Zoom**: OpenSeadragon for IIIF images, Panzoom fallback for others

## 🏛️ Supported Museums

### No API Key Required
1. **Chicago Art Institute** - Public domain masterpieces with IIIF support
2. **Cleveland Museum of Art** - Open access collection with color palette data
3. **The Met (NY)** - Metropolitan Museum of Art
4. **Brooklyn Museum** - 500,000+ objects
5. **Victoria and Albert Museum** - Design and decorative arts with IIIF support
6. **The Getty Museum** - J. Paul Getty Museum collection with IIIF support
7. **National Gallery of Art (US)** - NGA collection with IIIF support

### API Key Required
8. **Rijksmuseum** - Dutch Golden Age masterpieces
9. **Harvard Art Museums** - 250,000+ artworks with IIIF and color data
10. **Smithsonian Open Access** - 3+ million items
11. **Europeana** - 50+ million European cultural items
12. **Cooper Hewitt** - Smithsonian Design Museum

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/Emir-Faruk/ArtePuraTelegram.git
cd ArtePuraTelegram

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

### Without API Keys
The app works immediately with 7 museums (Chicago, Cleveland, The Met, Brooklyn, V&A, The Getty, National Gallery of Art).

### With API Keys
For full access to all 12 museums:

1. Obtain API keys (see [API_SETUP.md](API_SETUP.md))
2. Create `.streamlit/secrets.toml`:

```toml
[API_KEYS]
rijksmuseum = "your-key-here"
harvard = "your-key-here"
smithsonian = "your-key-here"
europeana = "your-key-here"
cooper_hewitt = "your-key-here"
```

3. Restart the app

## 📖 Documentation

- **[API_SETUP.md](API_SETUP.md)** - Complete guide for obtaining and configuring API keys
- **[INTEGRATION_SUMMARY.md](INTEGRATION_SUMMARY.md)** - Technical details of the implementation

## 🎯 Usage

1. **Browse**: View curated collections or use the random topic button (🎲)
2. **Search**: Enter your own search terms (artist, period, style, etc.)
3. **View**: Click on any artwork to see it in high resolution with advanced zoom controls
4. **Deep Zoom**: For IIIF-compatible museums, experience tile-based deep zoom powered by OpenSeadragon
5. **Explore**: Load more artworks with the "Daha Fazla Eser Getir" button
6. **Discover**: View color palettes and physical dimensions where available

## 🏗️ Architecture

### Data Flow
```
User Search → fetch_artworks_page() → ThreadPoolExecutor (12 workers)
                                    ↓
                            12 Concurrent API Calls
                                    ↓
                         Normalization Functions
                                    ↓
                    Unified Data Structure (with colors, dimensions, IIIF)
                                    ↓
                          UI Rendering (Grid)
```

### Key Components

- **Normalizers**: Convert diverse API responses to consistent format with metadata extraction
- **Fetchers**: Handle API calls with timeout and error handling
- **ThreadPoolExecutor**: Concurrent fetching for fast loading (12 workers)
- **OpenSeadragon**: Deep zoom with IIIF tile-based loading for supported museums
- **Panzoom**: Fallback zoom component for non-IIIF images
- **Metadata Extraction**: Color palettes and dimensions from Cleveland and Harvard APIs
- **Telegram Integration**: Seamless Mini App experience

## 🛠️ Technical Details

### Performance
- **Concurrent Fetching**: All 12 APIs called in parallel
- **Timeout**: 3 seconds per API, 5 seconds total max
- **Caching**: Met Museum search results cached for 1 hour
- **Load Time**: Typical 3-5 seconds for initial page
- **Deep Zoom**: Tile-based loading for IIIF images ensures smooth performance even at high zoom levels

### Data Structure
All artworks normalized to:
```python
{
    'id': str,              # Unique ID with museum prefix
    'source': str,          # Museum name
    'title': str,           # Artwork title
    'artist': str,          # Artist name
    'date': str,            # Creation date
    'thumbnail': str,       # 400px thumbnail URL
    'high_res': str,        # Up to 2048px image URL
    'link': str,            # Museum's artwork page
    'iiif_manifest': str,   # IIIF info.json URL (if available)
    'colors': list,         # Prominent color codes or names
    'dimensions': str       # Physical dimensions
}
```

### Error Handling
- Graceful degradation on API failures
- Silent error handling to maintain UX
- APIs without keys return empty results

## 🔒 Security

- ✅ CodeQL security scan: 0 alerts
- ✅ API keys via Streamlit secrets
- ✅ Proper URL validation
- ✅ No sensitive data exposure

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Add more museum APIs
- Implement response caching
- Add museum source filters
- Improve search relevance
- Add retry logic for failed calls

## 📝 License

This project is open source. Museum API usage must comply with each museum's terms of service.

## 🙏 Acknowledgments

- Chicago Art Institute for their excellent open access API and IIIF support
- Cleveland Museum of Art for their comprehensive API with color palette data
- The Metropolitan Museum of Art for their public domain collection
- The Getty Museum for their Linked Art API and IIIF implementation
- National Gallery of Art for their public API and IIIF support
- Harvard Art Museums for color data and IIIF support
- All participating museums for making art accessible to everyone
- OpenSeadragon project for enabling deep zoom capabilities
- Bosch Project for inspiring the IIIF deep zoom implementation

## 📊 Stats

- **Total APIs**: 12
- **Lines of Code**: ~1,100
- **Normalizer Functions**: 12
- **Concurrent Workers**: 12
- **Max Image Resolution**: 2048px+ (unlimited with IIIF)
- **Supported Museums**: 12 world-class institutions
- **IIIF-Compatible Museums**: 5 (Chicago, Harvard, V&A, Getty, NGA)
- **Museums with Color Data**: 2 (Cleveland, Harvard)

## 📞 Support

For issues:
- **Arte Pura**: Open an issue on GitHub
- **Museum APIs**: Contact respective museum's API support

---

**Made with ❤️ for art lovers everywhere**
