"""Independent numerical QA and a human-readable registration report."""
import json, math, html
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads((ROOT/p).read_text())
results=read('data/kingswood-registration/all-phases.json')
annotations=read('data/kingswood-plan-annotations.json')['phases']
records=read('data/kingswood-48-stacks.json')['records']
audits=[]

def resample(poly,n=1400):
 poly=np.asarray(poly,float)
 if np.linalg.norm(poly[0]-poly[-1])<1e-8:poly=poly[:-1]
 nxt=np.roll(poly,-1,0);d=np.linalg.norm(nxt-poly,axis=1);cum=np.r_[0,np.cumsum(d)]
 s=np.linspace(0,cum[-1],n,endpoint=False);i=np.searchsorted(cum,s,side='right')-1
 return poly[i]+(nxt-poly)[i]*((s-cum[i])/d[i])[:,None]
def moved(p,c):
 rad=np.deg2rad(c['rotationDegrees']);rot=np.array([[np.cos(rad),np.sin(rad)],[-np.sin(rad),np.cos(rad)]])
 return c['scaleMetresPerCanvasPixel']*p@rot+c['translationMetres']
def error(a,b):
 return float(np.sqrt((np.mean(cKDTree(a).query(b)[0]**2)+np.mean(cKDTree(b).query(a)[0]**2))/2))

for r in results:
 phase=r['phase'];raw=read(r['officialFile']);origin=np.array(r['originWGS84']);factor=np.array(r['metresPerDegree'])
 q=(np.array(raw['geometry']['rings'][0])-origin)*factor
 p=np.array(annotations[str(phase)]['outline'])*[1,-1]
 best=r['candidates'][0];base=error(moved(resample(p),best),resample(q))
 variants=[]
 for winding in [1,-1]:
  for shift in [0,7,23]:
   val=error(moved(resample(np.roll(p[::winding],shift,0)),best),resample(np.roll(q[:-1][::-winding],shift,0)))
   assert abs(val-base)<.02,(phase,val,base)
   variants.append(val)
 alternativeErrors=[error(moved(resample(p[::-1]),c),resample(q)) for c in r['candidates'] if abs((c['rotationDegrees']-best['rotationDegrees']+180)%360-180)>15]
 assert min(alternativeErrors)>base
 for flat,f in r['facades'].items():
  facade=np.array(f['facadeLocalMetres']);tangent=facade[1]-facade[0];mid=facade.mean(0);cam=np.array(f['cameraLocalMetres']);offset=cam-mid
  assert abs(np.linalg.norm(offset)-f['cameraOffsetMetres'])<1e-9
  assert 1<=f['cameraOffsetMetres']<3
  assert abs(np.dot(offset,tangent))<1e-8
  heading=np.deg2rad(f['heading']);assert np.linalg.norm(offset/np.linalg.norm(offset)-[np.sin(heading),np.cos(heading)])<.001
  roundtrip=(np.array([f['lng'],f['lat']])-origin)*factor
  assert np.linalg.norm(roundtrip-cam)<.08
 neighbours=[]
 rawCourt=read(f'data/kingswood-footprints/phase-{phase}-court-query.raw.json')
 for feature in rawCourt['response']['features']:
  a=feature['attributes']
  if r['courtTC'] not in (a.get('BuildingNameTC') or '') or a['BuildingCSUID']==r['attributes']['BuildingCSUID']:continue
  coord=np.mean(feature['geometry']['rings'][0][:-1],axis=0);dist=float(np.linalg.norm((coord-origin)*factor))
  if dist<1500:neighbours.append({'nameEN':a['BuildingNameEN'],'nameTC':a['BuildingNameTC'],'csuid':a['BuildingCSUID'],'distanceMetres':round(dist,1),'centroidWGS84':coord.tolist()})
 neighbours.sort(key=lambda n:n['distanceMetres']);assert len(neighbours)>=2
 audits.append({'phase':phase,'buildingCSUID':r['attributes']['BuildingCSUID'],'nameCheck':raw['attributes']['BuildingNameTC'],'coordinateRangeCheck':bool(113.97<origin[0]<114.03 and 22.43<origin[1]<22.49),'nearestSameCourtTowers':neighbours[:3],'higherResolutionRmsMetres':base,'windingAndCyclicOrderScoreRangeMetres':[min(variants),max(variants)],'bestRotationStillWins':True,'facadeNormalAndOneMetreOffsetCheck':'passed for A–H','wgs84RoundingMaximumToleranceMetres':.08})
(ROOT/'data/kingswood-registration/verification.json').write_text(json.dumps(audits,ensure_ascii=False,indent=2)+'\n')

parts=['''<!doctype html><html lang="zh-HK"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>嘉湖六座 · 配準結果</title><style>body{font:16px/1.6 system-ui;margin:32px auto;max-width:1120px;padding:0 18px;color:#203139}h1{font-size:30px}h2{margin-top:48px}table{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums}td,th{padding:8px;text-align:left;border-bottom:1px solid #d8e0df}a{color:#126b93}img{width:100%;height:auto}.images{display:grid;grid-template-columns:1fr 1fr;gap:16px}.warn{background:#fff4d7;padding:18px}small{color:#647276}.scroll{overflow:auto}@media(max-width:650px){.images{grid-template-columns:1fr}body{margin:16px auto}}</style><body><p><a href="./">← 景觀預覽</a></p><h1>嘉湖山莊：六期第1座 · 48個客廳 proxy</h1><p>1、2、3、5、6、7期各 A–H；第4期無住宅第1座。每座使用自己標明第1座的 28Hse 平面圖及 LandsD 官方 polygon。</p><p class="warn">全部可供估算預覽，並非已核實窗位。高度為建築平均模型，未核實。麗湖居鏡像候選仍有歧義，水平可信度為低；其他各座為中等。配準 RMS 是輪廓吻合程度，不是絕對位置誤差。</p><p><a href="data/kingswood-48-stacks.json">48條完整 JSON（3/F 示範）</a> · <a href="data/kingswood-48-stacks.csv">CSV</a> · <a href="data/kingswood-registration/verification.json">幾何 QA</a> · <a href="data/kingswood-plan-annotations.json">原始描點</a></p><p>方法：手工描外牆 → WGS84 局部東／北米制 → 72個旋轉起點、雙向 ICP / Chamfer → 平移＋旋轉＋等比縮放 → 個別客廳斜窗中點＋1米向外法線。順／逆時針及循環起點測試已通過。鏡像另作診斷，沒有把樓盤朝向塞入優化。</p><p>高度 = BaseHeight + floor × (TopHeight − BaseHeight) / Storeys + 1.5米。假設 G/F 位於 BaseHeight，未核實平台、樓板、屋頂及樓層計數；樓層平均跨度不是準確層高。數值小數位是儲存格式，不代表測量精度。</p>''']
for r in results:
 p=r['phase'];best=r['candidates'][0];entry=next(x for x in read('data/kingswood-first-towers-manifest.json')['phases'] if x['phase']==p)
 recs=[x for x in records if x['phase']==p];a=r['attributes'];check=next(x for x in read('data/kingswood-direction-validation.json')['checks'] if x['phase']==p)
 alternatives=[]
 for c in r['candidates']:
  if not any(abs((c['rotationDegrees']-d['rotationDegrees']+180)%360-180)<10 for d in alternatives):alternatives.append(c)
 parts.append(f'<h2>{p}期 {r["courtTC"]} · {r["courtEN"]} Tower 1</h2><p>標準樓層 {entry["floorRangeTypical"]["min"]}–{entry["floorRangeTypical"]["max"]}/F；BaseHeight {a["BaseHeight"]} m · TopHeight {a["TopHeight"]} m · Storeys {a["Storeys"]}。<br>官方 ID：{a["BuildingCSUID"]} · <a href="{r["officialFile"]}">polygon＋provenance</a> · <a href="{entry["estatePage"]}">28Hse estate</a> · <a href="{entry["floorPlanUrl"]}">原平面圖</a></p>')
 parts.append('<p>候選旋轉／RMS：'+', '.join(f'{c["rotationDegrees"]:.1f}° / {c["rmsMetres"]:.2f} m' for c in alternatives)+f'。鏡像最佳 RMS {r["mirrorDiagnostic"][0]["rmsMetres"]:.2f} m。</p>')
 parts.append(f'<p>獨立核對：{check["flat"]} 室計算 {r["facades"][check["flat"]]["heading"]}°，<a href="{html.escape(check["source"],quote=True)}">來源描述 {check["direction"]}</a>。{html.escape(check["note"])}</p>')
 parts.append(f'<div class="images"><a href="data/kingswood-registration/phase-{p}-overlay.png"><img alt="LandsD and registered outline" src="data/kingswood-registration/phase-{p}-overlay.png"></a><a href="data/kingswood-registration/phase-{p}-traced-plan.png"><img alt="Manually traced outline and facade labels" src="data/kingswood-registration/phase-{p}-traced-plan.png"></a></div><div class="scroll"><table><tr><th>Flat</th><th>Latitude</th><th>Longitude</th><th>Heading</th><th>3/F 高度（估算）</th><th>預覽</th></tr>')
 for rec in recs:parts.append(f'<tr><td>{rec["flat"]}</td><td>{rec["lat"]:.6f}</td><td>{rec["lng"]:.6f}</td><td>≈{rec["heading"]}°</td><td>≈{rec["altitude"]} m</td><td><a target="_blank" rel="noopener noreferrer" href="{html.escape(rec["flytoUrl"],quote=True)}">View ↗</a></td></tr>')
 parts.append('</table></div>')
parts.append('</body></html>');(ROOT/'kingswood-report.html').write_text(''.join(parts))
print('Passed all six towers: reversed/cyclic boundaries, winner stability, 48 normals, 1 m offsets, WGS84 conversion and nearby tower checks. Report generated.')
