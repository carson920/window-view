# 窗外景觀 · Window View

一個雙語網頁工具，讓用家選擇屋苑、座數、樓層、單位及窗，預覽窗戶位置，再開啟地政總署 Open3Dhk 的模擬視角。

Window View is a bilingual Vite app for selecting a property window, previewing its position on an OpenStreetMap view, and opening the calculated camera in LandsD Open3Dhk.

## Features

- 嘉湖山莊及麗港城資料目錄，支援屋苑、座數、樓層、單位及窗選擇。
- 選擇單位後才按需要載入該單位資料；API 不會把整份窗資料送到瀏覽器。
- 03 位置預覽：建築 footprint、所選窗、向外方向及北向箭咀。
- OpenStreetMap 底圖會跟隨所選座數及窗戶座標更新。
- 每隻窗獨立顯示 heading、座標、樓層高度及日照方向分數。
- 05 review mode 可一次檢視同一期各座的所有窗位。
- Node server 保留私有資料及 API；登入及查詢限額可按部署需要啟用。

## Quick start

需要 Node.js 22 或以上：

```sh
npm install
npm run dev
```

開啟 `http://127.0.0.1:5173/`。常用檢查指令：

```sh
npm test
npm run build
npm run preview
```

`npm run dev` 只適合本機開發，唔好直接公開 Vite dev server。

## Production server

先建立前端，再用 Node server 提供 `dist/` 及 `/api/*`：

```sh
npm run build
npm start
```

預設監聽 `127.0.0.1:5173`。正式環境需要 HTTPS origin：

```sh
NODE_ENV=production APP_ORIGIN=https://your.domain npm run start:production
```

亦可用 Docker Compose，由 Caddy 處理 HTTPS：

```sh
DOMAIN=your.domain docker compose up -d --build
```

部署時要帶上 `server/`、`data/`、`dist/`、`package.json`；單靠 GitHub Pages 等 static host 無法執行本 project 的 API。

## Data and API

原始窗資料放在 server-side `data/`，唔會由 `src/` import，亦唔會複製入 `dist/`。前端只會收到：

```text
GET /api/catalog
  屋苑、座數、樓層及單位選項；不含窗座標

GET /api/unit?estate=...&building=...&flat=...
  只回傳指定單位的窗、座標、heading 及 footprint

GET /api/estate-review?estate=...
  回傳 review mode 所需的該屋苑各座窗位摘要
```

資料結構及來源記錄見 [SERVER-DATA.md](SERVER-DATA.md)。窗戶資料包括水平 geometry、heading、垂直高度模型、來源及 confidence；估算高度會明確保留為估算值。

## Authentication and query limits

本機預設不要求登入，方便直接進入 main page。要啟用登入：

```sh
AUTH_REQUIRED=true npm start
```

管理邀請帳戶：

```sh
npm run user:add -- username
npm run user:remove -- username
```

帳戶資料及 quota 存於 `.private/auth.json`，`.private/` 已列入 ignore，唔應提交到 Git。預設每個帳戶每分鐘最多 30 次單位查詢、每日最多 100 次；呢個係降低大量抓取風險，唔係 DRM。

## Updating property data

主要資料檔案係 [data/properties.json](data/properties.json)。新增屋苑、座數、單位或窗時，保留：

- bilingual labels 及穩定的 parent-local IDs
- `floors` 及 `floorModel`
- 每隻窗的 `latitude`、`longitude`、`heading`
- `source`、`research`、`confidence`、`windowVerified`、`georefVerified`

研究及匯入工具位於 `scripts/`，包括 LandsD footprint 取得、平面圖配準、資料匯入及 coverage report。常用指令：

```sh
npm run fetch:kingswood-footprints
npm run fetch:kingswood-plans
npm run register:kingswood
npm run import:kingswood
npm run audit:kingswood
```

## Project layout

```text
src/                 前端選擇流程、預覽、OSM renderer 及樣式
server/              Node API、靜態檔案服務、登入及 quota
data/properties.json 私有屋苑及窗資料
data/                官方 footprint、配準結果、研究 provenance
scripts/             資料取得、配準、匯入及 audit 工具
tests/               API、資料、預覽及 camera 計算測試
dist/                npm run build 產生的公開前端資產
```

## Verification

```sh
npm test
npm run build
```

`npm test` 應通過目前所有測試；`npm run build` 應成功產生 `dist/`。幾何配準的 RMSE 只代表輪廓 fit residual，唔等於測量誤差或 survey-grade accuracy。

## Sources

- LandsD Open3Dhk: <https://3d.map.gov.hk/>
- OpenStreetMap: <https://www.openstreetmap.org/copyright>
- CSDI / LandsD datasets and research links: see the estate-specific reports in this repository.
