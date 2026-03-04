import requests
import json
import uuid
import os
import glob
import sys
import re
from datetime import datetime
from typing import List, Dict, Any

class BaseProvider:
    def __init__(self, name):
        self.name = name
    def get_user_agent(self):
        # Forced Chrome 133 to ensure HD resolution manifests are served
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
    def get_timeout(self):
        return 30

class PlutoProvider(BaseProvider):
    """Provider for Pluto TV with HD Resolution and Country-based Grouping"""

    def __init__(self):
        super().__init__("pluto")
        self.device_id = str(uuid.uuid1())
        self.session_token = None
        self.stitcher_params = ""
        self.session_expires_at = 0
        
        # Configuration from environment (e.g., 'us', 'gb', 'ca')
        self.region = os.getenv('PLUTO_REGION', 'us').lower()
        
        # IP Addresses extracted from official source to fix freezing/commercial issues
        self.x_forward = {
            "us": "185.236.200.172", # USA
            "gb": "84.17.50.173",    # United Kingdom
            "ca": "192.206.151.131", # Canada
            "fr": "176.31.84.249",   # France
            "de": "217.94.184.66",   # Germany
            "es": "88.26.241.248",   # Spain
            "it": "131.114.130.239", # Italy
            "br": "177.192.255.38",  # Brazil
            "mx": "200.68.128.83",   # Mexico
            "ar": "168.226.232.228", # Argentina
            "cl": "181.200.138.240", # Chile
            "no": "78.26.38.103",    # Norway
            "se": "185.6.8.2",       # Sweden
            "dk": "192.36.27.7",     # Denmark
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
            self.headers["X-Forwarded-For"] = self.x_forward[self.region]

    def _get_session_token(self) -> str:
        if self.session_token and datetime.now().timestamp() < self.session_expires_at:
            return self.session_token
        try:
            url = 'https://boot.pluto.tv/v4/start'
            params = {
                'appName': 'web', 'appVersion': '8.1.0', 'deviceVersion': '133.0.0',
                'deviceModel': 'web', 'deviceMake': 'chrome', 'deviceType': 'web',
                'clientID': self.device_id, 'clientModelNumber': '1.0.0', 'serverSideAds': 'false',
                'architecture': 'x86_64', 'buildVersion': '1.0.0', 'drmCapabilities': 'widevine:L3'
            }
            response = requests.get(url, headers=self.headers, params=params, timeout=self.get_timeout())
            data = response.json()
            self.session_token = data.get('sessionToken', '')
            self.stitcher_params = data.get('stitcherParams', '')
            self.session_expires_at = datetime.now().timestamp() + (4 * 3600)
            return self.session_token
        except Exception: return ""

    def get_channels(self) -> List[Dict[str, Any]]:
        try:
            token = self._get_session_token()
            if not token: return []
            
            url = "https://service-channels.clusters.pluto.tv/v2/guide/channels"
            headers = self.headers.copy()
            headers['authorization'] = f'Bearer {token}'
            
            response = requests.get(url, params={'limit': '1000'}, headers=headers, timeout=self.get_timeout())
            channel_data = response.json().get("data", [])
            
            processed_channels = []
            for channel in channel_data:
                channel_id, name = channel.get('id'), channel.get('name')
                if not channel_id or not name: continue
                
                logo = next((img.get('url') for img in channel.get('images', []) if img.get('type') == 'colorLogoPNG'), "")
                
                sid = str(uuid.uuid4())
                quality_suffix = (f"&quality=720p&deviceMake=chrome&deviceType=web&deviceModel=web"
                                  f"&deviceVersion=133.0.0&architecture=x86_64&buildVersion=1.0.0"
                                  f"&includeExtendedEvents=true&masterJWTPassthrough=true")

                if self.stitcher_params:
                    stream_url = (f"https://cfd-v4-service-channel-stitcher-use1-1.prd.pluto.tv/v2/stitch/hls/channel/{channel_id}/master.m3u8"
                                  f"?{self.stitcher_params}&jwt={token}{quality_suffix}")
                else:
                    stream_url = (f"https://cfd-v4-service-channel-stitcher-use1-1.prd.pluto.tv/stitch/hls/channel/{channel_id}/master.m3u8"
                                  f"?appName=web&appVersion=8.1.0&sid={sid}&serverSideAds=true{quality_suffix}")
                
                processed_channels.append({'id': str(channel_id), 'name': name, 'stream_url': stream_url, 'logo': logo})
            return processed_channels
        except Exception: return []

    def generate_m3u(self, channels, epg_url):
        m3u = f'#EXTM3U x-tvg-url="{epg_url}"\n'
        for ch in channels:
            m3u += f'#EXTINF:-1 tvg-id="{ch["id"]}" tvg-logo="{ch["logo"]}" group-title="Pluto TV",{ch["name"]}\n'
            m3u += f'{ch["stream_url"]}\n'
        return m3u

def merge_master_playlist(epg_url):
    """Combines regional files and Replaces Pluto categories with Country Names"""
    sort_config = {
        "us": {"priority": 1, "label": "United States"},
        "ca": {"priority": 2, "label": "Canada"},
        "gb": {"priority": 3, "label": "United Kingdom"},
        "fr": {"priority": 4, "label": "France"},
        "de": {"priority": 5, "label": "Germany"},
        "es": {"priority": 6, "label": "Spain"},
        "it": {"priority": 7, "label": "Italy"},
        "mx": {"priority": 8, "label": "Mexico"},
        "br": {"priority": 9, "label": "Brazil"},
        "ar": {"priority": 10, "label": "Argentina"},
        "cl": {"priority": 11, "label": "Chile"},
        "no": {"priority": 12, "label": "Norway"},
        "se": {"priority": 13, "label": "Sweden"},
        "dk": {"priority": 14, "label": "Denmark"},
    }

    # Gather regional files, excluding both 'all.m3u' and the old 'master.m3u'
    files = [f for f in glob.glob("pluto_*.m3u") if "all.m3u" not in f and "master.m3u" not in f]
    sorted_files = sorted(files, key=lambda x: sort_config.get(x.replace("pluto_", "").replace(".m3u", ""), {}).get("priority", 99))
    
    master_content = f'#EXTM3U x-tvg-url="{epg_url}"\n'
    for file in sorted_files:
        region_key = file.replace("pluto_", "").replace(".m3u", "")
        country_label = sort_config.get(region_key, {}).get("label", region_key.upper())
        
        if os.path.exists(file):
            with open(file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("#EXTINF"):
                        # Force grouping by Country Name ONLY
                        line = re.sub(r'group-title="[^"]*"', f'group-title="{country_label}"', line)
                        master_content += line
                    elif not line.startswith("#EXTM3U") and line.strip():
                        master_content += line
                    
    with open("pluto_all.m3u", "w", encoding="utf-8") as f:
        f.write(master_content)

if __name__ == "__main__":
    epg = "https://github.com/matthuisman/i.mjh.nz/raw/refs/heads/master/PlutoTV/all.xml.gz"
    if len(sys.argv) > 1 and sys.argv[1] == "--merge":
        merge_master_playlist(epg)
    else:
        provider = PlutoProvider()
        channels = provider.get_channels()
        with open(f"pluto_{provider.region}.m3u", "w", encoding="utf-8") as f:
            f.write(provider.generate_m3u(channels, epg))
