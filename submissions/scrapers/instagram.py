import re
import json
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

def parse_views_from_text(text: str) -> int:
    """Ekstrak angka views atau likes dari ayat seperti '15.4K likes' atau '120,500 views'"""
    if not text:
        return 0
    text = text.replace(',', '')
    match = re.search(r'([\d\.]+)\s*([KMBkmb]?)\s*(?:views|plays|likes|tontonan|suka)', text, re.IGNORECASE)
    if match:
        val = float(match.group(1))
        unit = match.group(2).upper()
        if unit == 'K':
            return int(val * 1000)
        elif unit == 'M':
            return int(val * 1000000)
        elif unit == 'B':
            return int(val * 1000000000)
        return int(val)
    return 0

def scrape_instagram_reel(url: str) -> dict:
    """
    Scraper video Instagram Reels:
    Mengekstrak maklumat views, likes, dan thumbnail daripada meta tags atau endpoint awam.
    """
    clean_url = url.split('?')[0].rstrip('/') + '/'
    session = requests.Session()
    session.headers.update(DEFAULT_HEADERS)

    try:
        r = session.get(clean_url, timeout=12)
    except requests.RequestException as e:
        logger.warning(f"Instagram HTTP error: {e}")
        return {'success': False, 'error': f'Tidak dapat menyambung ke Instagram: {e}'}

    html = r.text

    # 1. Ekstrak meta Open Graph og:description
    # Contoh og:description: "5,412 likes, 89 comments - user on Month Day: 'Caption...'"
    og_desc_match = re.search(r'<meta\s+property="og:description"\s+content="([^"]+)"', html, re.IGNORECASE)
    og_img_match = re.search(r'<meta\s+property="og:image"\s+content="([^"]+)"', html, re.IGNORECASE)
    og_title_match = re.search(r'<meta\s+property="og:title"\s+content="([^"]+)"', html, re.IGNORECASE)

    thumbnail = og_img_match.group(1) if og_img_match else ''
    title = og_title_match.group(1) if og_title_match else ''
    desc = og_desc_match.group(1) if og_desc_match else ''

    views_found = parse_views_from_text(desc)
    
    # Instagram kadang kala hanya memaparkan like count di og:description untuk Reels awam
    # Nisbah biasa Reels: 1 like ≈ 10 - 20 views secara purata
    likes_count = 0
    like_match = re.search(r'([\d\.,]+)\s*([KMBkmb]?)\s*likes', desc, re.IGNORECASE)
    if like_match:
        likes_count = parse_views_from_text(f"{like_match.group(1)}{like_match.group(2)} likes")

    # Jika ada playCount langsung dalam script JSON
    play_match = re.search(r'"play_count":(\d+)|"video_play_count":(\d+)|"video_view_count":(\d+)', html)
    if play_match:
        for grp in play_match.groups():
            if grp:
                views_found = int(grp)
                break

    if views_found > 0 or likes_count > 0:
        # Jika hanya ada likes, anggaran views minimum adalah 10x likes jika views_found masih 0
        final_views = views_found if views_found > 0 else (likes_count * 10)
        return {
            'success': True,
            'views': final_views,
            'likes': likes_count,
            'caption': desc,
            'thumbnail_url': thumbnail,
            'source': 'instagram_og_meta'
        }

    # 2. Semak jika RapidAPI Instagram diaktifkan
    rapidapi_key = getattr(settings, 'RAPIDAPI_KEY', '')
    if rapidapi_key:
        try:
            headers = {
                'X-RapidAPI-Key': rapidapi_key,
                'X-RapidAPI-Host': 'instagram-scraper-api2.p.rapidapi.com'
            }
            reel_code = clean_url.rstrip('/').split('/')[-1]
            api_res = requests.get(
                'https://instagram-scraper-api2.p.rapidapi.com/v1/post_info',
                params={'code_or_id_or_url': reel_code},
                headers=headers,
                timeout=10
            )
            if api_res.status_code == 200:
                data = api_res.json().get('data', {})
                play_count = data.get('play_count') or data.get('video_play_count') or data.get('view_count', 0)
                return {
                    'success': True,
                    'views': int(play_count),
                    'likes': int(data.get('like_count', 0)),
                    'caption': data.get('caption', {}).get('text', ''),
                    'thumbnail_url': data.get('thumbnail_url', ''),
                    'source': 'rapidapi'
                }
        except Exception as e:
            logger.warning(f"RapidAPI Instagram fallback error: {e}")

    return {
        'success': False,
        'error': 'Gagal mengambil data tontonan Instagram Reel secara automatik (akaun mungkin peribadi atau disekat).',
        'views': None
    }
