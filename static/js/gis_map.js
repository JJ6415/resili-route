/**
 * ResiliRoute Real-time GIS Leaflet Map Engine (Tokyo Metro GIS)
 * Localized in Japanese.
 * Visualizes:
 * 1. Normal mode: Tokyo <-> Shin-Osaka Tokaido Shinkansen route
 * 2. Disaster mode: Shinjuku Station bottleneck red hazard radius & 3 Crowd Balancing corridors
 * 3. Stranded rescue: Roppongi Hills 300m turn-by-turn walking evacuation polyline
 */
class GisMap {
  constructor(containerId) {
    this.containerId = containerId;
    this.map = null;
    this.layerGroup = null;
    this.initMap();
  }

  initMap() {
    const el = document.getElementById(this.containerId);
    if (!el || typeof L === 'undefined') return;

    // Center on Tokyo metropolitan area
    this.map = L.map(this.containerId, {
      zoomControl: true,
      attributionControl: false
    }).setView([35.6812, 139.7671], 12);

    // CartoDB Dark Matter Tile Layer (Cyberpunk / Night Dark Theme)
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      maxZoom: 19,
      subdomains: 'abcd'
    }).addTo(this.map);

    this.layerGroup = L.layerGroup().addTo(this.map);
    this.renderNormalShinkansen();
  }

  clear() {
    if (this.layerGroup) {
      this.layerGroup.clearLayers();
    }
  }

  // 1. Normal Mode: Shinkansen Route
  renderNormalShinkansen() {
    if (!this.map || !this.layerGroup) return;
    this.clear();

    this.map.setView([35.25, 137.6], 7);

    const tokyo = [35.6812, 139.7671];
    const nagoya = [35.1709, 136.8815];
    const shinosaka = [35.7330, 135.5003];

    // Tokaido Shinkansen Path
    const shinkansenPath = [
      tokyo,
      [35.5300, 139.6969], // Shinagawa / Yokohama
      [35.1030, 139.0780], // Atami
      [34.9717, 138.3890], // Shizuoka
      [34.7037, 137.7347], // Hamamatsu
      nagoya,
      [35.3157, 136.2905], // Maibara
      [34.9858, 135.7588], // Kyoto
      shinosaka
    ];

    const polyline = L.polyline(shinkansenPath, {
      color: '#10b981',
      weight: 4,
      opacity: 0.85,
      dashArray: '8, 6'
    }).addTo(this.layerGroup);

    // Station Markers
    const createMarker = (latlng, title, desc, color = '#10b981') => {
      const circle = L.circleMarker(latlng, {
        radius: 7,
        fillColor: color,
        color: '#fff',
        weight: 2,
        opacity: 1,
        fillOpacity: 0.9
      }).addTo(this.layerGroup);
      circle.bindPopup(`<b style="color:${color};">${title}</b><br><span style="font-size:11px;">${desc}</span>`);
    };

    createMarker(tokyo, '東京駅 (Tokyo Station)', '出発駅: 新幹線「のぞみ」普通車指定席');
    createMarker(nagoya, '名古屋駅 (Nagoya Station)', '主要停車拠点');
    createMarker(shinosaka, '新大阪駅 (Shin-Osaka Station)', '到着駅: 4,470円 (23.1%) 経費削減決裁完了');
  }

  // 2. Disaster Mode: Shinjuku 0.92 Bottleneck & 3 Evacuation Corridors
  renderDisasterShinjuku(bottleneckIndex = 0.92) {
    if (!this.map || !this.layerGroup) return;
    this.clear();

    const shinjukuStation = [35.6900, 139.7005];
    this.map.setView(shinjukuStation, 14);

    // 1) Pulsing Danger Zone around Shinjuku Station
    L.circle(shinjukuStation, {
      radius: 450,
      color: '#ef4444',
      fillColor: '#ef4444',
      fillOpacity: 0.35,
      weight: 2,
      dashArray: '6, 6'
    }).addTo(this.layerGroup).bindPopup(
      `<b style="color:#ef4444;">🚨 新宿駅拠点ボトルネック指数: ${bottleneckIndex}</b><br>` +
      `<span style="color:#f87171; font-size:11px;">群衆事故危険限界値 (0.70) 超過のため駅構内進入全面遮断 (SHUTDOWN)</span>`
    ).openPopup();

    // 2) Headquarters Location
    const hqLocation = [35.6925, 139.6970];
    L.circleMarker(hqLocation, {
      radius: 8,
      fillColor: '#38bdf8',
      color: '#fff',
      weight: 2,
      fillOpacity: 1
    }).addTo(this.layerGroup).bindPopup('<b>🏢 新宿本社ビル (社員120名 避難開始地点)</b>');

    // 3) Corridor A: Meiji Jingu Green Belt (Group A - 40 people)
    const meijiJingu = [35.6764, 139.6993];
    const pathA = [hqLocation, [35.6850, 139.6980], [35.6810, 139.6990], meijiJingu];
    L.polyline(pathA, {
      color: '#10b981',
      weight: 5,
      opacity: 0.9
    }).addTo(this.layerGroup);

    L.circleMarker(meijiJingu, {
      radius: 8,
      fillColor: '#10b981',
      color: '#fff',
      weight: 2,
      fillOpacity: 1
    }).addTo(this.layerGroup).bindPopup(
      '<b style="color:#10b981;">🌲 グループA避難所: 明治神宮北門 安心緑地帯</b><br>' +
      '<span style="font-size:11px;">東京西部社員40名割当 | 歩行混雑88.5%回避</span>'
    );

    // 4) Corridor B: Hatsudai Emergency Bus Stop (Group B - 40 people)
    const hatsudai = [35.6811, 139.6865];
    const pathB = [hqLocation, [35.6880, 139.6930], [35.6835, 139.6890], hatsudai];
    L.polyline(pathB, {
      color: '#06b6d4',
      weight: 5,
      opacity: 0.9
    }).addTo(this.layerGroup);

    L.circleMarker(hatsudai, {
      radius: 8,
      fillColor: '#06b6d4',
      color: '#fff',
      weight: 2,
      fillOpacity: 1
    }).addTo(this.layerGroup).bindPopup(
      '<b style="color:#06b6d4;">🚌 グループB避難所: 初台 緊急モビリティ・バスゾーン</b><br>' +
      '<span style="font-size:11px;">東京東部社員40名割当 | 緊急シャトルバス連携</span>'
    );

    // 5) Corridor C: In-House 4F Bunker (Group C - 40 people)
    L.circleMarker([35.6925, 139.6970], {
      radius: 12,
      color: '#f59e0b',
      fillColor: '#f59e0b',
      fillOpacity: 0.4,
      weight: 3
    }).addTo(this.layerGroup).bindPopup(
      '<b style="color:#f59e0b;">🛡️ グループC避難所: 本社4F セーフティバンカーゾーン</b><br>' +
      '<span style="font-size:11px;">遠距離社員40名社内残留 | 非常食・通信回線確保</span>'
    );
  }

  // 3. Stranded Mode: Roppongi Hills Rescue & 300m Turn-by-Turn Path
  renderStrandedRoppongi() {
    if (!this.map || !this.layerGroup) return;
    this.clear();

    const satoLocation = [35.6605, 139.7290];
    const moriTowerShelter = [35.6628, 139.7292];

    this.map.setView([35.6616, 139.7291], 16);

    // Sato Location Marker (Red Pin)
    L.circleMarker(satoLocation, {
      radius: 9,
      fillColor: '#ef4444',
      color: '#fff',
      weight: 2,
      fillOpacity: 1
    }).addTo(this.layerGroup).bindPopup(
      '<b style="color:#ef4444;">📍 佐藤課長 孤立位置</b><br>' +
      '<span style="font-size:11px;">六本木ヒルズ付近 鉄道全面運休による道路孤立</span>'
    ).openPopup();

    // Mori Tower Shelter (Purple Shield / Safe Zone)
    L.circleMarker(moriTowerShelter, {
      radius: 11,
      fillColor: '#8b5cf6',
      color: '#fff',
      weight: 2,
      fillOpacity: 1
    }).addTo(this.layerGroup).bindPopup(
      '<b style="color:#8b5cf6;">🏢 六本木ヒルズ 森タワー 3F防災センター</b><br>' +
      '<span style="font-size:11px;">企業提携 特等級耐震BCP避難所 | モバイル入館QR認証発行</span>'
    );

    // 300m Turn-by-Turn Walking Path
    const walkingRoute = [
      satoLocation,
      [35.6613, 139.7288],
      [35.6620, 139.7290],
      moriTowerShelter
    ];

    L.polyline(walkingRoute, {
      color: '#38bdf8',
      weight: 6,
      opacity: 0.9,
      dashArray: '10, 8'
    }).addTo(this.layerGroup);
  }

  invalidateSize() {
    if (this.map) {
      setTimeout(() => this.map.invalidateSize(), 150);
    }
  }
}

window.GisMap = GisMap;
