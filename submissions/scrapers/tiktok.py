import re
import json
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9,ms;q=0.8',
    'Referer': 'https://www.tiktok.com/',
}

def extract_numbers_from_text(text: str) -> int:
    """Tukar format teks seperti 12.5K atau 1.2M kepada integer"""
    if not text:
        return 0
    text = text.upper().strip()
    try:
        if 'K' in text:
            return int(float(text.replace('K', '')) * 1000)
        elif 'M' in text:
            return int(float(text.replace('M', '')) * 1000000)
        elif 'B' in text:
            return int(float(text.replace('B', '')) * 1000000000)
        return int(re.sub(r'[^\d]', '', text) or 0)
    except Exception:
        return 0

def scrape_tiktok_video(url: str) -> dict:
    """
    Scraper video TikTok:
    Mengekstrak jumlah tontonan (playCount), likes, komen, thumbnail, dan teks kapsyen.
    """
    clean_url = url.strip()
    session = requests.Session()
    session.headers.update(DEFAULT_HEADERS)

    # 1. Resolusi URL pendek (contoh: vt.tiktok.com / vm.tiktok.com)
    try:
        r = session.get(clean_url, timeout=12, allow_redirects=True)
    except requests.RequestException as e:
        logger.warning(f"TikTok HTTP request error: {e}")
        return {'success': False, 'error': f'Tidak dapat menyambung ke TikTok: {e}'}

    final_url = r.url
    html = r.text

    # 2. Cuba ekstrak daripada skrip __UNIVERSAL_DATA_FOR_REHYDRATION__
    match = re.search(r'<script\s+id="__UNIVERSAL_DATA_FOR_REHYDRATION__"\s+type="application/json">([\s\S]*?)<\/script>', html)
    if match:
        try:
            data = json.loads(match.group(1))
            scope = data.get('__DEFAULT_SCOPE__', {})
            detail = scope.get('webapp.videoDetail', {})
            item_struct = detail.get('itemInfo', {}).get('itemStruct', {})
            
            if item_struct:
                stats = item_struct.get('stats', {})
                play_count = int(stats.get('playCount', 0))
                digg_count = int(stats.get('diggCount', 0))
                author = item_struct.get('author', {}).get('uniqueId', '')
                desc = item_struct.get('desc', '')
                video_info = item_struct.get('video', {})
                cover = video_info.get('cover', '') or video_info.get('originCover', '')

                return {
                    'success': True,
                    'views': play_count,
                    'likes': digg_count,
                    'comments': int(stats.get('commentCount', 0)),
                    'shares': int(stats.get('shareCount', 0)),
                    'author': f"@{author}" if author else '',
                    'caption': desc,
                    'thumbnail_url': cover,
                    'canonical_url': final_url,
                    'source': 'direct_html_universal_data'
                }
        except Exception as e:
            logger.debug(f"Parsing __UNIVERSAL_DATA_FOR_REHYDRATION__ gagal: {e}")

    # 3. Cuba ekstrak daripada SIGI_STATE (Format lama TikTok)
    sigi_match = re.search(r'<script\s+id="SIGI_STATE"\s+type="application/json">([\s\S]*?)<\/script>', html)
    if sigi_match:
        try:
            sigi_data = json.loads(sigi_match.group(1))
            item_module = sigi_data.get('ItemModule', {})
            for key, item in item_module.items():
                stats = item.get('stats', {})
                play_count = int(stats.get('playCount', 0))
                if play_count > 0:
                    return {
                        'success': True,
                        'views': play_count,
                        'likes': int(stats.get('diggCount', 0)),
                        'author': f"@{item.get('author', '')}",
                        'caption': item.get('desc', ''),
                        'thumbnail_url': item.get('video', {}).get('cover', ''),
                        'canonical_url': final_url,
                        'source': 'sigi_state'
                    }
        except Exception as e:
            logger.debug(f"Parsing SIGI_STATE gagal: {e}")

    # 4. Alternatif: Semak jika RapidAPI TikTok dikonfigurasi dalam .env
    rapidapi_key = getattr(settings, 'RAPIDAPI_KEY', '')
    if rapidapi_key:
        try:
            headers = {
                'X-RapidAPI-Key': rapidapi_key,
                'X-RapidAPI-Host': 'tiktok-all-in-one.p.rapidapi.com'
            }
            api_res = requests.get(
                'https://tiktok-all-in-one.p.rapidapi.com/video/info',
                params={'url': clean_url},
                headers=headers,
                timeout=10
            )
            if api_res.status_code == 200:
                json_res = api_res.json()
                play_count = json_res.get('data', {}).get('play_count', 0)
                return {
                    'success': True,
                    'views': int(play_count),
                    'likes': int(json_res.get('data', {}).get('digg_count', 0)),
                    'caption': json_res.get('data', {}).get('title', ''),
                    'thumbnail_url': json_res.get('data', {}).get('cover', ''),
                    'source': 'rapidapi'
                }
        except Exception as e:
            logger.warning(f"RapidAPI fallback gagal: {e}")

    return {
        'success': False,
        'error': 'Gagal mengekstrak metadata TikTok secara automatik (mungkin disekat bot/captcha).',
        'views': None
    }
