# 📺 Pluto TV Custom Playlists

Automatically updated M3U playlists for Pluto TV with forced HD resolution and country-based grouping.

---

## 🔗 Live Playlists (M3U)

| Region / Type | Direct Raw M3U Link (Copy & Paste) |
| :--- | :--- |
| **🌍 Master (All Regions Sorted)** | `https://raw.githubusercontent.com/BuddyChewChew/pluto/main/pluto_master.m3u` |
| **🇺🇸 United States East** | `https://raw.githubusercontent.com/BuddyChewChew/pluto/main/pluto_us_east.m3u` |
| **🇺🇸 United States West** | `https://raw.githubusercontent.com/BuddyChewChew/pluto/main/pluto_us_west.m3u` |
| **🇨🇦 Canada** | `https://raw.githubusercontent.com/BuddyChewChew/pluto/main/pluto_ca.m3u` |
| **🇬🇧 United Kingdom** | `https://raw.githubusercontent.com/BuddyChewChew/pluto/main/pluto_uk.m3u` |
| **🇫🇷 France** | `https://raw.githubusercontent.com/BuddyChewChew/pluto/main/pluto_fr.m3u` |

---

## 📅 XML TV Guide (EPG)

Fallback EPG link for your IPTV player. You shouldn't need it.

| Type | Link |
| :--- | :--- |
| **EPG URL** | `https://github.com/matthuisman/i.mjh.nz/raw/refs/heads/master/PlutoTV/all.xml.gz` |

---

## ✨ Key Features

* **Forced HD Resolution:** The script mimics a Chrome 133 Desktop client on `x86_64` architecture to force Pluto to serve **720p/1080p** manifests instead of mobile-capped 480p.
* **Country-Based Grouping:** The **Master** playlist removes standard categories (Kids, Movies, etc.) and groups channels strictly by their country/region for a cleaner experience.
* **Audio Fix:** Configured to prioritize the primary stereo audio track, removing unwanted "Audio Description" or commentary tracks.
* **Auto-Update:** Playlists are refreshed every 6 hours via GitHub Actions to ensure tokens and streams remain active.

---

## 🛠️ How to Use

1.  **Copy** one of the M3U links from the table above.
2.  **Paste** it into your favorite IPTV player (TiviMate, OTT Navigator, VLC, Apple TV, etc.).
3.  Add the **EPG URL** to the EPG/TV Guide section of your app settings.
4.  Enjoy high-quality Pluto TV!
