"""Use the existing room-side window/clearance QA with fixed South Horizons placements."""
from registerSouthHorizons import *
from PIL import Image,ImageDraw
import ast
# Reuse the existing normal/window projection implementation, without running
# Laguna's orientation search or top-level ingestion side effects.
tree=ast.parse((ROOT/'scripts/processLagunaApproved.py').read_text());functions=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['normal_windows','draw_overlay']];exec(compile(ast.Module(body=functions,type_ignores=[]),'shared-window-geometry','exec'))
reports=[];review=[]
for record in read(JOB/'preparation.json'):
 tower=record['tower'];out=ROOT/f'data/south-horizons-tower-{tower.lower()}';a=read(out/'annotations.json');o=read(out/'official-footprint.json');place=read(out/'placement.json');s=place['transform'];origin,factor,q=en_frame(np.array(o['geometry']['rings'][0]));start=time.perf_counter()
 if not a['rooms']:continue
 windows=normal_windows(a,s,q,origin,factor);errors=[f'{w["flat"]}/{w["id"]}: '+', '.join(w['qaErrors']) for w in windows if w['qaErrors']]
 if s['rmsMetres']>1.5:errors.append('outline RMSE > 1.5m')
 result=dict(tower=tower,buildingCsuid=o['attributes']['BuildingCSUID'],origin=origin.tolist(),transform=s,windows=windows,annotation=a,qa={'pass':not errors,'errors':errors},confidenceDimensions={'planInterpretation':'manual-trace-approved-published-plan','horizontalGeoreferencing':'fixed-approved-orientation-and-official-footprint','windowSemantics':'room-interior-witness','verticalGeometry':'estimated-building-average'},orientationEvidence={'northUp':True,'rotationDegrees':s['rotationDegrees'],'reflected':False,'source':'Approved north-up Centamap screenshots in data/south-horizons-approved-job/orientation','method':'Single screenshot orientation; no alternate angle or reflection optimization'},approvedJob='data/south-horizons-approved-job/approved-job.json')
 save(out/'result.json',result);draw_overlay(out,a,s,q,windows)
 reports.append(dict(tower=tower,windows=len(windows),qaPass=not errors,errors=errors,rmse=s['rmsMetres'],seconds=time.perf_counter()-start))
 print(tower,len(windows),'PASS' if not errors else errors,flush=True)
save(JOB/'validation-summary.json',reports)
