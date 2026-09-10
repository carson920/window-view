# 嘉湖山莊全座擴展工作表

## 已完成

- 1期樂湖居：第一座，A–H
- 2期賞湖居：第一座，A–H
- 3期翠湖居：第一座，A–H
- 5期麗湖居：第一座，A–H
- 6期美湖居：第一座，A–H
- 7期景湖居：第一座，A–H

## 執行規則

目前公開屋苑資料顯示住宅合共 58 座：1期 14 座、2期 6 座、3期 5 座、5期 7 座、6期 8 座、7期 14 座；第4期為商場／酒店。這個數字會以每期官方 block plan 再核對。

每一座必須獨立保存：

1. 官方 typical floor plan source
2. LandsD Building polygon、CSUID 及 provenance
3. floor-plan similarity transform（rotation、scale、translation、RMSE）
4. 每個 stack 的客廳及可識別房窗線段
5. WGS84 座標、outward heading、vertical confidence

同 layout 只重用 plan template；每座仍然要獨立做 placement registration。

## 批次順序

先完成第1期其餘住宅座數，再處理第2、3、5、6、7期。每批只在官方 polygon 成功取得及 fit check 通過後寫入正式資料；未完成項目保留 `georefVerified:false`。

第4期嘉湖銀座／+WOO／酒店另列商業項目，不混入住宅單位。
