# 嘉湖山莊住宅標準層窗位

更新：2026-09-10。六個住宅期共58座，每座 A–H、30個主要客廳／睡房窗 proxy，共1740個。第4期商場酒店不列住宅。

| 期 | 屋苑 | 座數 | 窗 proxy |
|---|---|---|---|
|1|樂湖居|1–14|420|
|2|賞湖居|1–6|180|
|3|翠湖居|1–6|180|
|5|麗湖居|1–10|300|
|6|美湖居|1–8|240|
|7|景湖居|1–14|420|

## 其餘三期來源

`scripts/completeRemainingCourts.py` 使用現有 `phase-{1,6,7}-court-query.raw.json` 的 response.features。按英文 court/block 唯一名稱選取，保存各座 polygon、CSUID、來源 URL。沒有再下載全港 dataset。

公開平面圖索引：https://www.squarefoot.com.hk/estate/detail/嘉湖山莊-4390

六張分組原圖存於 `data/kingswood-plans/locwood-group-{a,b}.jpg`、`maywood-{even,odd}.jpg`、`kenswood-group-{a,b}.jpg`。圖上標題及房間標籤確認：

- 樂湖1–7為一組、8–14反射；翠湖模板 A B C D E F G H 對應樂湖 B A H G F E D C。
- 美湖2、4、6、8同模板手性；1、3、5、7反射。
- 景湖3、5、7、9、11、13、14同模板手性；1、2、4、6、8、10、12反射。

重用已審閱窗台線模板，在 local EN metres 對每座官方輪廓獨立 similarity fit；保存 rotation、scale、translation、RMSE/P95。窗法線由線段及室內點決定；另存窗中點、投影外牆點、鏡頭位置。鏡頭至少1米向外，若官方概化輪廓仍包含鏡頭則沿同一法線移至外牆外0.5米。

`scripts/importRemainingCourts.mjs` 更新 UI 資料；兩個 preview 及全期總覽依選中座數取得獨立 polygon。

## 完成範圍及可信度

完成標準層的模板配準及可選 preview；不是實測玻璃座標。跨期窗 proxy 沿用已確認模板，不能將 outline RMSE 當作窗位測量精度。所有新窗維持 `windowVerified:false`、`georefVerified:false`、`confidence:review`。樓高採 BaseHeight/TopHeight/Storeys 平均模型，標 estimated。景湖頂層複式不套用標準層；未收錄廚廁窗及窗台側邊玻璃。

重跑：先用有 numpy/scipy/Pillow 的 Python 執行 `scripts/completeRemainingCourts.py`，再 `node scripts/importRemainingCourts.mjs`。驗證：`npm test`、`npm run build`。
