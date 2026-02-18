# 🎨 Arte Pura

A beautiful Streamlit application that aggregates high-quality art images from 10 world-class museum APIs, optimized for Telegram Mini Apps.

## ✨ Features

- **10 Museum APIs**: Access artworks from Chicago Art Institute, Cleveland Museum, The Met, Rijksmuseum, Harvard Art Museums, Smithsonian, Europeana, Cooper Hewitt, Brooklyn Museum, and V&A
- **Concurrent Fetching**: Fast loading with parallel API calls using ThreadPoolExecutor
- **High-Resolution Images**: IIIF protocol support with images up to 2048px
- **Responsive Design**: Works beautifully on all devices with custom zoom controls
- **Telegram Integration**: Fully optimized for Telegram Mini Apps
- **Custom Panzoom**: Interactive zoom and pan for artwork viewing

## 🏛️ Supported Museums

### No API Key Required
1. **Chicago Art Institute** - Public domain masterpieces
2. **Cleveland Museum of Art** - Open access collection
3. **The Met (NY)** - Metropolitan Museum of Art
4. **Brooklyn Museum** - 500,000+ objects
5. **Victoria and Albert Museum** - Design and decorative arts

### API Key Required
6. **Rijksmuseum** - Dutch Golden Age masterpieces
7. **Harvard Art Museums** - 250,000+ artworks
8. **Smithsonian Open Access** - 3+ million items
9. **Europeana** - 50+ million European cultural items
10. **Cooper Hewitt** - Smithsonian Design Museum

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
The app works immediately with 5 museums (Chicago, Cleveland, The Met, Brooklyn, V&A).

### With API Keys
For full access to all 10 museums:

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
3. **View**: Click on any artwork to see it in high resolution with zoom controls
4. **Explore**: Load more artworks with the "Daha Fazla Eser Getir" button

## 🏗️ Architecture

### Data Flow
```
User Search → fetch_artworks_page() → ThreadPoolExecutor (10 workers)
                                    ↓
                            10 Concurrent API Calls
                                    ↓
                         Normalization Functions
                                    ↓
                          Unified Data Structure
                                    ↓
                          UI Rendering (Grid)
```

### Key Components

- **Normalizers**: Convert diverse API responses to consistent format
- **Fetchers**: Handle API calls with timeout and error handling
- **ThreadPoolExecutor**: Concurrent fetching for fast loading
- **Panzoom**: Custom zoom component for image viewing
- **Telegram Integration**: Seamless Mini App experience

## 🛠️ Technical Details

### Performance
- **Concurrent Fetching**: All 10 APIs called in parallel
- **Timeout**: 3 seconds per API, 5 seconds total max
- **Caching**: Met Museum search results cached for 1 hour
- **Load Time**: Typical 3-5 seconds for initial page

### Data Structure
All artworks normalized to:
```python
{
    'id': str,          # Unique ID with museum prefix
    'source': str,      # Museum name
    'title': str,       # Artwork title
    'artist': str,      # Artist name
    'date': str,        # Creation date
    'thumbnail': str,   # 400px thumbnail URL
    'high_res': str,    # Up to 2048px image URL
    'link': str        # Museum's artwork page
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

- Chicago Art Institute for their excellent open access API
- Cleveland Museum of Art for their comprehensive API
- The Metropolitan Museum of Art for their public domain collection
- All participating museums for making art accessible to everyone

## 📊 Stats

- **Total APIs**: 10
- **Lines of Code**: ~850
- **Normalizer Functions**: 10
- **Concurrent Workers**: 10
- **Max Image Resolution**: 2048px
- **Supported Museums**: 10 world-class institutions

## 📞 Support

For issues:
- **Arte Pura**: Open an issue on GitHub
- **Museum APIs**: Contact respective museum's API support

---

**Made with ❤️ for art lovers everywhere**
