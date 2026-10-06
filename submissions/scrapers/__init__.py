from .tiktok import scrape_tiktok_video
from .instagram import scrape_instagram_reel

def scrape_video_data(url: str, platform: str) -> dict:
    """
    Fungsi pengagih utama scraper:
    Mengambil data tontonan (views), suka (likes), thumbnail, dan kapsyen
    daripada TikTok atau Instagram Reels.
    """
    if platform == 'tiktok':
        return scrape_tiktok_video(url)
    elif platform == 'reels':
        return scrape_instagram_reel(url)
    else:
        return {'success': False, 'error': f'Platform {platform} tidak disokong.'}
