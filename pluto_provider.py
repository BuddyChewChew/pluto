import requests
import json
import uuid
import os
from datetime import datetime
from typing import List, Dict, Any

# Mocking BaseProvider for standalone execution or integration
class BaseProvider:
    def __init__(self, name):
        self.name = name
    def get_user_agent(self):
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    def get_timeout(self):
        return 30
    def validate_channel(self, channel):
        return True
    def normalize_channel(self, channel):
        return channel

class PlutoProvider(BaseProvider):
    """Provider for Pluto TV channels with Resolution and Audio Fixes"""

    def __init__(self):
        super().__init__("pluto")
        
        self.device_id = str(uuid.uuid1())
        self.session_token = None
        self.stitcher_params = ""
        self.session_expires_at = 0
        
        # Load credentials from environment
        self.username = os.getenv('PLUTO_USERNAME')
        self.password = os.getenv('PLUTO_PASSWORD')
        
        # Get region from environment [cite: 2]
        self.region = os.getenv('PLUTO_REGION', 'us_west')
        
        # Regional IP addresses for geo-spoofing [cite: 2]
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
        
        if self.region in self.x_forward:
            forwarded_ip = self.x_forward[self.region]
            if forwarded_ip:
                self.headers["X-Forwarded-For"] = forwarded_ip

    def _get_session_token(self) -> str:
        """Get or refresh session token [cite: 4]"""
        if self.session_token and datetime.now().timestamp() < self.session_expires_at:
            return self.session_token
        
        try:
            url = 'https://boot.pluto.tv/v4/start'
            params = {
                'appName': 'web',
                'appVersion': '8.0.0-111b2b9dc00bd0bea9030b30662159ed9e7c8bc6',
                'deviceVersion': '122.0.0',
                'deviceModel': 'web',
                'deviceMake': 'chrome',
                'deviceType': 'web',
                'clientID': self.device_id,
                'clientModelNumber': '1.0.0',
                'serverSideAds': 'false',
                'drmCapabilities': 'widevine:L3',
                'notificationVersion': '1',
            }
            
            if self.username and self.password:
                params['username'] = self.username
                params['password'] = self.password
            
            response = requests.get(url, headers=self.headers, params=params, timeout=self.get_timeout())
            response.raise_for_status()
            
            data = response.json()
            self.session_token = data.get('sessionToken')
            self.stitcher_params = data.get('stitcherParams', '') [cite: 7]
            self.session_expires_at = datetime.now().timestamp() + (4 * 3600)
            
            return self.session_token
        except Exception:
            return ""

    def get_channels(self) -> List[Dict[str, Any]]:
        """Get Pluto TV channels [cite: 9]"""
        try:
            token = self._get_session_token()
            if not token:
                return []
            
            url = "https://service-channels.clusters.pluto.tv/v2/guide/channels"
            headers = self.headers.copy()
            headers['authorization'] = f'Bearer {token}' [cite: 11]
            
            params = {'channelIds': '', 'offset': '0', 'limit': '1000', 'sort': 'number:asc'} [cite: 13]
            response = requests.get(url, params=params, headers=headers, timeout=self.get_timeout())
            response.raise_for_status()
            
            channel_data = response.json().get("data", [])
            categories_list = self._get_categories(headers, params)
            
            processed_channels = []
            for channel in channel_data:
                channel_id = channel.get('id') [cite: 15]
                name = channel.get('name') [cite: 15]
                
                if not channel_id or not name:
                    continue
                
                logo = ""
                images = channel.get('images', []) [cite: 17]
                for image in images:
                    if image.get('type') == 'colorLogoPNG': [cite: 17]
                        logo = image.get('url', '') [cite: 17]
                        break
                
                group = categories_list.get(channel_id, 'General') [cite: 18]
                
                # FIX: Force 720p and Primary Audio by defining device parameters 
                if self.stitcher_params:
                    stream_url = (f"https://cfd-v4-service-channel-stitcher-use1-1.prd.pluto.tv/v2/stitch/hls/channel/{channel_id}/master.m3u8"
                                  f"?{self.stitcher_params}&jwt={token}&masterJWTPassthrough=true&includeExtendedEvents=true"
                                  f"&quality=720p&deviceMake=Chrome&deviceType=web&deviceModel=web&deviceVersion=122.0.0")
                else:
                    sid = str(uuid.uuid4()) [cite: 20]
                    stream_url = (f"https://cfd-v4-service-channel-stitcher-use1-1.prd.pluto.tv/stitch/hls/channel/{channel_id}/master.m3u8"
                                  f"?advertisingId=&appName=web&appVersion=8.0.0&deviceId={self.device_id}&deviceMake=Chrome&deviceModel=web"
                                  f"&deviceType=web&deviceVersion=122.0.0&sid={sid}&serverSideAds=true&quality=720p")
                
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
        """Get channel categories for grouping [cite: 27]"""
        try:
            category_url = "https://service-channels.clusters.pluto.tv/v2/guide/categories"
            response = requests.get(category_url, params=params, headers=headers, timeout=self.get_timeout())
            categories_data = response.json().get("data", [])
            categories_list = {}
            for elem in categories_data:
                category = elem.get('name', 'General') [cite: 28]
                channel_ids = elem.get('channelIDs', []) [cite: 28]
                for cid in channel_ids:
                    categories_list[cid] = category
            return categories_list
        except Exception:
            return {}

    def generate_m3u(self, channels, epg_url):
        """Build the M3U content"""
        m3u = f'#EXTM3U x-tvg-url="{epg_url}"\n'
        for ch in channels:
            m3u += f'#EXTINF:-1 tvg-id="{ch["id"]}" tvg-logo="{ch["logo"]}" group-title="{ch["group"]}",{ch["name"]}\n'
            m3u += f'{ch["stream_url"]}\n'
        return m3u

if __name__ == "__main__":
    provider = PlutoProvider()
    channels = provider.get_channels()
    epg_url = "https://github.com/matthuisman/i.mjh.nz/raw/refs/heads/master/PlutoTV/all.xml.gz"
    
    playlist_content = provider.generate_m3u(channels, epg_url)
    filename = f"pluto_{provider.region}.m3u"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(playlist_content)
    print(f"Successfully generated {filename} with {len(channels)} channels.")
