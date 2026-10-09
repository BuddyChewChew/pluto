
# 📺 Pluto TV Custom Playlists

Automatically updated M3U playlists for Pluto TV with forced HD resolution and country-based grouping.

---

## 🔗 Live Playlists (M3U)

| Region / Type | Direct Raw M3U Link (Copy & Paste) |
| :--- | :--- |
| **🌍 ALL REGIONS (Sorted)** | `https://raw.githubusercontent.com/BuddyChewChew/pluto/main/pluto_all.m3u` |
| **🇺🇸 United States** | `https://raw.githubusercontent.com/BuddyChewChew/pluto/main/pluto_us.m3u` |
| **🇨🇦 Canada** | `https://raw.githubusercontent.com/BuddyChewChew/pluto/main/pluto_ca.m3u` |
| **🇬🇧 United Kingdom** | `https://raw.githubusercontent.com/BuddyChewChew/pluto/main/pluto_gb.m3u` |
| **🇫🇷 France** | `https://raw.githubusercontent.com/BuddyChewChew/pluto/main/pluto_fr.m3u` |
| **🇩🇪 Germany** | `https://raw.githubusercontent.com/BuddyChewChew/pluto/main/pluto_de.m3u` |
| **🇪🇸 Spain** | `https://raw.githubusercontent.com/BuddyChewChew/pluto/main/pluto_es.m3u` |
| **🇮🇹 Italy** | `https://raw.githubusercontent.com/BuddyChewChew/pluto/main/pluto_it.m3u` |
| **🇲🇽 Mexico** | `https://raw.githubusercontent.com/BuddyChewChew/pluto/main/pluto_mx.m3u` |
| **🇧🇷 Brazil** | `https://raw.githubusercontent.com/BuddyChewChew/pluto/main/pluto_br.m3u` |
| **🇦🇷 Argentina** | `https://raw.githubusercontent.com/BuddyChewChew/pluto/main/pluto_ar.m3u` |
| **🇨🇱 Chile** | `https://raw.githubusercontent.com/BuddyChewChew/pluto/main/pluto_cl.m3u` |
| **🇳🇴 Norway** | `https://raw.githubusercontent.com/BuddyChewChew/pluto/main/pluto_no.m3u` |
| **🇸🇪 Sweden** | `https://raw.githubusercontent.com/BuddyChewChew/pluto/main/pluto_se.m3u` |
| **🇩🇰 Denmark** | `https://raw.githubusercontent.com/BuddyChewChew/pluto/main/pluto_dk.m3u` |

---

## 📅 XML TV Guide (EPG)

EPG You shouldn't need it. Epgs load with playlist.

| Type | Link |
| :--- | :--- |
| **EPG URL** | `https://github.com/matthuisman/i.mjh.nz/raw/refs/heads/master/PlutoTV/all.xml.gz` |

---

## ✨ Key Features

* **Forced HD Resolution:** Script mimics a Chrome 133 Desktop client on `x86_64` to force Pluto to serve **720p/1080p** manifests.
* **Stable Commercials:** Uses optimized regional IP headers (`X-Forwarded-For`) to prevent freezing or pausing during ad transitions.
* **Country-Based Grouping:** The **All Regions** playlist ignores standard categories and groups channels strictly by their country.
* **Auto-Update:** Playlists are refreshed every 6 hours via GitHub Actions to ensure streams remain active.

---

## 🛠️ How to Use

1.  **Copy** one of the M3U links from the table above.
2.  **Paste** it into your IPTV player (TiviMate, OTT Navigator, VLC, etc.).
3.  Add the **EPG URL** to the TV Guide section of your app.
4.  **Note:** If you were using the old `pluto_master.m3u` or `pluto_uk.m3u`, please switch to `pluto_all.m3u` and `pluto_gb.m3u` respectively.
