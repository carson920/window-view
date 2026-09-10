# 嘉湖山莊六期第1座：48個客廳 proxy

已加入 app：1、2、3、5、6、7期每座 A–H，共48個 stack。第4期無住宅第1座。
所有 View 均為明確標示的估算預覽；不是48個已測量／已核實窗位。

開啟 `kingswood-report.html` 可逐座查看原圖描點、北向配準圖、48個3/F示例、来源和 flyto 連結。
完整資料：`data/kingswood-48-stacks.json`；簡表：`data/kingswood-48-stacks.csv`。

|期|第1座|平面圖標示標準樓層|配準 RMS（m）|G 室實算法線|
|---|---|---|---|---|
|1|樂湖居|1–35|0.50|334.7°|
|2|賞湖居|1–35|0.39|335.3°|
|3|翠湖居|1–32|0.95|108.0°|
|5|麗湖居|1–29|0.94|82.7°|
|6|美湖居|1–38|0.41|174.8°|
|7|景湖居|1–31|0.95|267.0°|

## 方法與可信度

每張28Hse圖均明確包含該期第1座；不是拿同一期另一座代替。
手工描外牆輪廓、辨認 A–H 客廳斜窗，保留原始描點及圖像。相鄰 A/B、C/D、E/F、G/H 各共用一條直斜窗外牆；用端點正交最小平方擬合共同直線，減少分隔牆交點描點誤差。各 flat 仍保留自己的獨立中點。
官方 LandsD polygon 以中英文名、第1座、天水圍座標、同苑附近樓宇核對；所有原始查詢、CSUID、URL及取得時間均已保存。
賞湖居英文名稱曾匹配另一區「誠和閣」，已用中文名稱與位置排除。

在 WGS84 橢球局部東／北米制平面進行 72個旋轉起點的雙向 ICP，然後最小化雙向 Chamfer 平方距離；只解平移、旋轉、等比縮放。取客廳窗線中點再沿向外法線加1米。
以更密採樣測試順／逆時針及多個循環頂點起點，最佳旋轉不變。物理鏡像另保存為診斷，並非把多邊形頂點次序反轉。

樓形接近對稱。鏡像有時同樣貼近，甚至誤差較小；採用明確標為該第1座的未鏡像平面圖，並做獨立粗方向核對。
麗湖居 A 朝南的核對不能排除鏡像，其全部 stack 水平可信度標為低；其餘為中等，均未達測量級。
RMS 不是絕對位置精度。輪廓概化、窗台突出／內縮、人工描點及層間差異仍有不確定性。
小數一位角度和六位經緯度只是數值儲存格式，並非準確度聲稱。

翠湖居 G 的108.0°是客廳斜窗法線（共線擬合前107.5°）；之前151.8°只來自未經完整配準挑選的另一段外牆，已撤換。
108.0°在東南象限但較接近東，比八方位「東南」更偏東；樓盤描述只作寬鬆合理性核對，沒有強制改成135°。

## 高度

`BaseHeight + floor × (TopHeight−BaseHeight)/Storeys + eyeHeight`，眼高預設1.5米。
這是假設G/F在BaseHeight的建築平均高度示範模型。未核實樓板、平台、屋頂、樓層計數與垂直基準差異；不能當成準確層高。
所有模型 `verified:false, confidence:estimated, allowEstimated:true`。正式核實樓層資料可日後替換成 lookup，不影響水平資料。
麗湖30/F及景湖32/F複式不套用標準圖。

## 重跑

已完成原始資料取得，使用 app 無需重跑研究。

```sh
npm run fetch:kingswood-footprints
npm run fetch:kingswood-plans
python3 -m venv .venv
.venv/bin/pip install numpy scipy pillow
.venv/bin/python scripts/registerKingswood.py
npm run import:kingswood
.venv/bin/python scripts/auditKingswood.py
npm test
npm run build
```

`data/kingswood-registration/verification.json` 保存近鄰、循環次序、法線垂直、1米偏移及經緯度往返核對。
`data/kingswood-direction-validation.json` 保存獨立粗方向來源；優化腳本不讀取該檔。
