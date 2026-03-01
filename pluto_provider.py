import requests
import json
import uuid
import os
from datetime import datetime
from typing import List, Dict, Any

# Standalone BaseProvider to ensure GitHub Action compatibility
class BaseProvider:
    def __init__(self, name):
        self.name = name
    def get_user_agent(self):
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    def get_timeout(self):
        return 30

class PlutoProvider(BaseProvider):
    """Provider for Pluto TV with Max Resolution and Primary Audio Fixes"""

    def __init__(self):
        super().__init__("pluto")
        self.device_id = str(uuid.uuid1())
        self.session_token = None
        self.stitcher_params = ""
        self.session_expires_at = 0
        
        # Region and Credentials
        self.region = os.getenv('PLUTO_REGION', 'us_west')
        self.username = os.getenv('PLUTO_USERNAME', '').strip() or None
        self.password = os.getenv('PLUTO_PASSWORD', '').strip() or None
        
        self.x_forward = {
            "local": "",
            "uk": "178.238.11.6",
            "ca": "192.206.151.131", 
            "fr": "193.169.64.141",
            "us_east": "108.82.206.181",
            "us_west": "76.81.9.69",
        }
        
        self.headers = {
            'authority': 'boot.pluto.tv',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'origin': 'https://pluto.tv',
            'referer': 'https://pluto.tv/',
            'user-agent': self.get_user_agent(),
        }
        
        if self.region in self.x_forward and self.x_forward[self.region]:
            self.headers["X-Forwarded-For"] = self.x_forward[self.region]

    def _get_session_token(self) -> str:
        if self.session_token and datetime.now().timestamp() < self.session_expires_at:
            return self.session_token
        try:
            url = 'https://boot.pluto.tv/v4/start'
            params = {
                'appName': 'web',
                'appVersion': '8.0.0',
                'deviceVersion': '122.0.0',
                'deviceModel': 'web',
                'deviceMake': 'chrome',
                'deviceType': 'web',
                'clientID': self.device_id,
                'clientModelNumber': '1.0.0',
                'serverSideAds': 'false',
                'drmCapabilities': 'widevine:L3',
            }
            if self.username and self.password:
                params['username'] = self.username
                params['password'] = self.password
            
            response = requests.get(url, headers=self.headers, params=params, timeout=self.get_timeout())
            data = response.json()
            self.session_token = data.get('sessionToken', '')
            self.stitcher_params = data.get('stitcherParams', '')
            self.session_expires_at = datetime.now().timestamp() + (4 * 3600)
            return self.session_token
        except Exception:
            return ""

    def get_channels(self) -> List[Dict[str, Any]]:
        try:
            token = self._get_session_token()
            if not token: return []
            
            url = "https://service-channels.clusters.pluto.tv/v2/guide/channels"
            headers = self.headers.copy()
            headers['authorization'] = f'Bearer {token}'
            params = {'channelIds': '', 'offset': '0', 'limit': '1000', 'sort': 'number:asc'}
            
            response = requests.get(url, params=params, headers=headers, timeout=self.get_timeout())
            channel_data = response.json().get("data", [])
            categories_list = self._get_categories(headers, params)
            
            processed_channels = []
            for channel in channel_data:
                channel_id = channel.get('id')
                name = channel.get('name')
                if not channel_id or not name:
                    continue
                
                logo = ""
                for image in channel.get('images', []):
                    if image.get('type') == 'colorLogoPNG':
                        logo = image.get('url', '')
                        break
                
                group = categories_list.get(channel_id, 'General')
                sid = str(uuid.uuid4())
                
                # FIXED: Max Resolution (720p) and Primary Audio Logic
                # includeExtendedEvents=true is the key for high-quality manifests
                base_stitcher = "https://cfd-v4-service-channel-stitcher-use1-1.prd.pluto.tv/v2/stitch/hls/channel"
                if self.stitcher_params:
                    stream_url = (f"{base_stitcher}/{channel_id}/master.m3u8?{self.stitcher_params}"
                                  f"&jwt={token}&masterJWTPassthrough=true&includeExtendedEvents=true"
                                  f"&quality=720p&deviceMake=Chrome&deviceType=web&deviceVersion=122.0.0")
                else:
                    stream_url = (f"https://cfd-v4-service-channel-stitcher-use1-1.prd.pluto.tv/stitch/hls/channel/{channel_id}/master.m3u8"
                                  f"?appName=web&appVersion=8.0.0&deviceMake=Chrome&deviceModel=web&deviceType=web"
                                  f"&deviceVersion=122.0.0&includeExtendedEvents=true&sid={sid}&serverSideAds=true&quality=720p")
                
                processed_channels.append({
                    'id': str(channel_id),
                    'name': name,
                    'stream_url': stream_url,
                    'logo': logo,
                    'group': group
                })
            return processed_channels
        except Exception:
            return []

    def _get_categories(self, headers: dict, params: dict) -> dict:
        try:
            url = "https://service-channels.clusters.pluto.tv/v2/guide/categories"
            response = requests.get(url, params=params, headers=headers, timeout=self.get_timeout())
            data = response.json().get("data", [])
            cat_map = {}
            for elem in data:
                cat_name = elem.get('name', 'General')
                for cid in elem.get('channelIDs', []):
                    cat_map[cid] = cat_name
            return cat_map
        except Exception:
            return {}

    def generate_m3u(self, channels, epg_url):
        m3u = f'#EXTM3U x-tvg-url="{epg_url}"\n'
        for ch in channels:
            m3u += f'#EXTINF:-1 tvg-id="{ch["id"]}" tvg-logo="{ch["logo"]}" group-title="{ch["group"]}",{ch["name"]}\n'
            m3u += f'{ch["stream_url"]}\n'
        return m3u

if __name__ == "__main__":
    provider = PlutoProvider()
    channels = provider.get_channels()
    epg_url = "https://github.com/matthuisman/i.mjh.nz/raw/refs/heads/master/PlutoTV/all.xml.gz"
    m3u_content = provider.generate_m3u(channels, epg_url)
    filename = f"pluto_{provider.region}.m3u"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(m3u_content)
    print(f"Generated {filename}")
