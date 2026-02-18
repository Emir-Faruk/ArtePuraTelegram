# Arte Pura - API Configuration Guide

## Overview

Arte Pura now integrates with **12 world-class museum APIs** to bring you the finest art collections:

### No API Key Required (7):
1. **Chicago Art Institute** - No API key required (IIIF support)
2. **Cleveland Museum of Art** - No API key required (color palette data)
3. **The Met (Metropolitan Museum of Art)** - No API key required
4. **Brooklyn Museum** - No API key required
5. **Victoria and Albert Museum (V&A)** - No API key required (IIIF support)
6. **The Getty Museum** - No API key required (IIIF support)
7. **National Gallery of Art (US)** - No API key required (IIIF support)

### API Key Required (5):
8. **Rijksmuseum** - API key required
9. **Harvard Art Museums** - API key required (IIIF + color data)
10. **Smithsonian Open Access** - API key required
11. **Europeana** - API key required
12. **Cooper Hewitt, Smithsonian Design Museum** - API key required

## API Key Setup

### Method 1: Using Streamlit Secrets (Recommended for Production)

If you're deploying on Streamlit Cloud or using Streamlit locally:

1. Create a `.streamlit/secrets.toml` file in your project root
2. Add your API keys in this format:

```toml
[API_KEYS]
rijksmuseum = "your-rijksmuseum-api-key"
harvard = "your-harvard-api-key"
smithsonian = "your-smithsonian-api-key"
europeana = "your-europeana-api-key"
cooper_hewitt = "your-cooper-hewitt-api-key"
```

3. The app will automatically use these keys from `st.secrets`

### Method 2: Direct Configuration (For Local Development)

Edit the API key section in `app.py` (around line 177-207) and replace the placeholder values:

```python
RIJKS_API_KEY = "your-actual-api-key-here"
HARVARD_API_KEY = "your-actual-api-key-here"
SMITHSONIAN_API_KEY = "your-actual-api-key-here"
EUROPEANA_API_KEY = "your-actual-api-key-here"
COOPER_HEWITT_API_KEY = "your-actual-api-key-here"
```

## How to Get API Keys

### 1. Rijksmuseum API
- **URL**: https://data.rijksmuseum.nl/object-metadata/api/
- **Sign Up**: Create a Rijksmuseum Studio account
- **Free Tier**: 10,000 requests/day
- **Documentation**: https://data.rijksmuseum.nl/object-metadata/api/

### 2. Harvard Art Museums API
- **URL**: https://www.harvardartmuseums.org/collections/api
- **Sign Up**: Request an API key through their form
- **Free Tier**: Available for non-commercial use
- **Documentation**: https://github.com/harvardartmuseums/api-docs

### 3. Smithsonian Open Access API
- **URL**: https://api.si.edu/openaccess/api/v1.0/
- **Sign Up**: Register at https://api.data.gov/signup/
- **Free Tier**: 1,000 requests/hour
- **Documentation**: https://edan.si.edu/openaccess/apidocs/

### 4. Europeana API
- **URL**: https://pro.europeana.eu/page/get-api
- **Sign Up**: Register for a Europeana API key
- **Free Tier**: 10,000 requests/day
- **Documentation**: https://pro.europeana.eu/page/apis

### 5. Cooper Hewitt API
- **URL**: https://collection.cooperhewitt.org/api/
- **Sign Up**: Register for API access
- **Free Tier**: Rate limits apply
- **Documentation**: https://collection.cooperhewitt.org/api/methods/

### 6. Brooklyn Museum API
- **URL**: https://www.brooklynmuseum.org/api/
- **API Key**: Not required for basic access
- **Documentation**: https://www.brooklynmuseum.org/opencollection/api/

### 7. Victoria and Albert Museum API
- **URL**: https://developers.vam.ac.uk/
- **API Key**: Not required for basic access  
- **Documentation**: https://developers.vam.ac.uk/guide/v2/welcome.html

### 8. The Getty Museum API
- **URL**: https://data.getty.edu/museum/collection/
- **API Key**: Not required
- **Features**: Linked Art JSON-LD format, IIIF support
- **Documentation**: https://data.getty.edu/museum/collection/docs/

### 9. National Gallery of Art API
- **URL**: https://api.nga.gov/
- **API Key**: Not required
- **Features**: IIIF support, comprehensive collection
- **Documentation**: https://github.com/NationalGalleryOfArt/opendata

## Features

### Concurrent API Fetching
The app uses `ThreadPoolExecutor` to fetch from all 12 APIs simultaneously, providing fast results:
- Maximum 12 workers (one per API)
- 3-second timeout per API request
- Graceful error handling - if one API fails, others continue

### Data Normalization
Each museum API returns data in a different format. Arte Pura normalizes all responses to a consistent structure:

```python
{
    'id': 'museum-prefix-objectid',
    'source': 'Museum Name',
    'title': 'Artwork Title',
    'artist': 'Artist Name',
    'date': 'Creation Date',
    'thumbnail': 'URL to thumbnail image',
    'high_res': 'URL to high-resolution image',
    'link': 'URL to museum's page for this artwork',
    'iiif_manifest': 'IIIF info.json URL (if available)',
    'colors': ['color1', 'color2', ...],  # Prominent colors
    'dimensions': 'Physical dimensions'
}
```

### High-Resolution Images
The integration prioritizes the highest quality images available:
- **IIIF Protocol**: Used for Chicago, Harvard, V&A, Getty, and NGA with OpenSeadragon deep zoom
- **Maximum Resolution**: Up to 2048px for most museums, unlimited with IIIF tile-based loading
- **Fallback Handling**: Falls back to Panzoom for non-IIIF images

### Advanced Features
- **Deep Zoom**: OpenSeadragon-powered tile-based zooming for IIIF-compatible museums
- **Color Palettes**: Extracted and displayed from Cleveland and Harvard APIs
- **Metadata**: Physical dimensions shown when available

## Testing

Without API keys, the app will still work using 7 museums (Chicago, Cleveland, The Met, Brooklyn, V&A, Getty, and NGA) which don't require keys.

To test with all 12 APIs, you'll need to obtain API keys for the 5 museums listed above.

## Troubleshooting

### "No artworks found"
- Check your API keys are correctly configured
- Some museums have smaller collections for certain search terms
- Try different search queries

### Slow loading
- Initial load fetches from all APIs concurrently (3-5 seconds is normal)
- Check your internet connection
- Some museum APIs may have rate limits

### Images not loading
- Some museums use CORS restrictions
- High-resolution images may take time to load
- Try refreshing the page

## Support

For issues with:
- **Arte Pura app**: Open an issue on GitHub
- **Museum APIs**: Contact the respective museum's API support (links above)

## License

Arte Pura is open source. Museum API usage must comply with each museum's terms of service.
