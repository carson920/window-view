"""Reviewed approved-source traces. Coordinates refer to uniformly resized plan images.
No orientation screenshot pixel is used for geographic scale or position.
"""
import json,copy
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];JOB=ROOT/'data/laguna-approved-job'
def read(p):return json.loads(p.read_text())
sources=read(JOB/'sources/primary-source.json')['items'];templates={}
def add(id,outline,rooms,center,notes):
 im=Image.open(JOB/f'floorplans/full/{id}.jpg');im.thumbnail((1200,1400))
 templates[id]={'canvas':list(im.size),'outline':outline,'rooms':rooms,'core':center,'source':next(x['previewUrl'].replace('estate_small_image','estate_image') for x in sources if x['id']==id),'sourcePage':'https://llam.com.hk/floorplan_detail.php?sno=4','extractionMethod':'Visual tracing of fine glazing lines on approved Primary full-resolution image; largest main pane or existing reviewed corner chord; room-side interior witness chooses outward normal.','reviewNotes':notes,'insetTranslations':{}}
def room(kind,a,b,interior):return [kind,a,b,interior]
# Existing L01 traces are on the exact same approved Primary raster. Keep the
# reviewed inset and standard variants separate, with immutable input copies.
for id,t in [('L01-special',1),('L01',3),('L02',2)]:
 a=read(JOB/f'legacy-input/tower-{t}-annotations.json');templates[id]=copy.deepcopy(a);templates[id]['core']=[696,895] if t!=2 else [947,922]
 templates[id]['reviewNotes']='Approved L01/L02 reinspection: mirrored room adjacency, three lifts, hopper/stair core and exterior recesses agree. B/C special insets remain independent.'
 templates[id]['sourceSheet']='L01' if t!=2 else 'L02'
# G2: separately traced outline and glazing, not G1 dimension substitution.
o3=[[463,317],[571,317],[571,512],[645,512],[645,317],[752,317],[752,352],[833,352],[833,407],[793,448],[901,525],[922,495],[940,512],[1115,512],[1115,682],[828,682],[828,757],[1115,757],[1115,928],[940,928],[922,944],[900,922],[848,962],[796,992],[835,1034],[815,1055],[815,1104],[750,1104],[750,1136],[647,1136],[647,927],[571,927],[571,1136],[470,1136],[470,1105],[400,1105],[400,1055],[382,1035],[420,995],[367,963],[310,923],[296,945],[279,930],[128,930],[128,759],[417,759],[417,684],[128,684],[128,514],[278,514],[296,498],[310,522],[422,447],[382,407],[382,352],[463,352]]
r3={
'A':[room('living',[850,958],[897,916],[840,858]),room('bedroom-1',[911,931],[934,928],[925,895]),room('bedroom-2',[1112,862],[1112,925],[1050,892]),room('master',[1112,763],[1112,824],[1055,794])],
'B':[room('living',[798,996],[846,965],[741,939]),room('bedroom-1',[800,1002],[822,1047],[785,1056]),room('master',[651,1134],[746,1134],[701,1095])],
'C':[room('living',[370,965],[419,996],[480,939]),room('bedroom-1',[412,1002],[391,1047],[434,1056]),room('master',[473,1134],[566,1134],[525,1095])],
'D':[room('living',[314,924],[365,963],[390,852]),room('bedroom-1',[281,929],[306,931],[292,895]),room('bedroom-2',[129,864],[129,926],[174,895]),room('master',[129,765],[129,827],[180,795])],
'E':[room('living',[315,520],[365,480],[390,575]),room('bedroom-1',[282,514],[306,511],[292,550]),room('bedroom-2',[129,516],[129,580],[180,548]),room('master',[129,615],[129,679],[180,647])],
'F':[room('living',[367,475],[419,449],[481,495]),room('bedroom-1',[400,353],[384,406],[422,388]),room('master',[464,320],[464,351],[515,354])],
'G':[room('living',[798,449],[839,480],[735,493]),room('bedroom-1',[815,352],[832,406],[790,390]),room('master',[750,320],[750,351],[710,354])],
'H':[room('living',[844,483],[898,523],[842,575]),room('bedroom-1',[911,510],[935,513],[925,550]),room('bedroom-2',[1112,516],[1112,580],[1050,550]),room('master',[1112,615],[1112,678],[1055,644])]
}
add('L03',o3,r3,[607,719],'B/C 522 sf inset-shaped main rooms; G1 has different wing dimensions. No cross-family deduplication.')
# L04 follows its own raster; mirror relation is visually confirmed for the
# MAIN room topology, but the 25/30 inset must retain standard B/C glazing.
o4=[[450,400],[558,400],[558,570],[628,570],[628,400],[735,400],[735,438],[815,438],[815,493],[776,532],[865,615],[902,578],[919,595],[1068,595],[1068,765],[780,765],[780,840],[1068,840],[1068,1013],[919,1013],[902,1031],[865,1004],[829,1046],[776,1083],[817,1125],[795,1146],[795,1190],[729,1190],[729,1223],[630,1223],[630,1010],[558,1010],[558,1223],[458,1223],[458,1193],[391,1193],[391,1147],[373,1125],[409,1087],[360,1048],[307,1008],[281,1038],[265,1019],[95,1019],[95,847],[401,847],[401,773],[95,773],[95,603],[266,603],[282,582],[307,611],[411,532],[371,494],[371,438],[450,438]]
r4={
'A':[room('living',[309,1008],[358,1046],[359,947]),room('bedroom-1',[266,1018],[291,1021],[280,984]),room('bedroom-2',[96,951],[96,1015],[155,980]),room('master',[96,853],[96,914],[155,881])],
'B':[room('living',[363,1051],[405,1086],[470,1030]),room('bedroom-1',[400,1091],[381,1136],[424,1150]),room('master',[462,1221],[553,1221],[505,1180])],
'C':[room('living',[780,1087],[827,1049],[714,1031]),room('bedroom-1',[785,1090],[807,1137],[760,1150]),room('master',[633,1221],[725,1221],[682,1182])],
'D':[room('living',[831,1041],[862,1003],[806,942]),room('bedroom-1',[891,1017],[915,1014],[902,981]),room('bedroom-2',[1067,945],[1067,1010],[1010,980]),room('master',[1067,845],[1067,907],[1010,880])],
'E':[room('living',[831,564],[862,610],[811,666]),room('bedroom-1',[891,594],[915,596],[902,633]),room('bedroom-2',[1067,598],[1067,662],[1010,630]),room('master',[1067,698],[1067,761],[1010,732])],
'F':[room('living',[780,532],[828,561],[721,579]),room('bedroom-1',[797,441],[814,492],[770,480]),room('master',[732,403],[732,436],[690,440])],
'G':[room('living',[358,561],[406,533],[470,578]),room('bedroom-1',[387,441],[371,492],[415,476]),room('master',[451,403],[451,436],[500,440])],
'H':[room('living',[310,609],[354,567],[364,665]),room('bedroom-1',[268,602],[293,600],[282,635]),room('bedroom-2',[96,607],[96,669],[155,638]),room('master',[96,704],[96,769],[155,740])]
}
add('L04',o4,r4,[593,806],'Reflected G2 main layout; source explicitly identifies different B/C windows for Towers 25 and 30.')
# L05/06 independently measured source coordinates; no assumed interchange
# with G2 because scaled scan, core walls and inset applicability differ.
o5=[[418,265],[507,265],[507,420],[569,420],[569,265],[660,265],[660,294],[727,294],[727,339],[695,373],[783,433],[804,413],[820,428],[966,428],[966,572],[718,572],[718,634],[966,634],[966,778],[820,778],[804,792],[783,770],[740,806],[698,835],[730,866],[730,914],[658,914],[658,943],[571,943],[571,767],[509,767],[509,943],[423,943],[423,913],[352,913],[352,866],[384,835],[338,806],[307,769],[279,792],[264,779],[137,779],[137,636],[377,636],[377,574],[137,574],[137,430],[264,430],[278,416],[305,445],[384,374],[350,340],[350,295],[418,295]]
r5={
'A':[room('living',[742,803],[780,766],[730,718]),room('bedroom-1',[795,779],[816,777],[804,750]),room('bedroom-2',[963,723],[963,774],[915,750]),room('master',[963,638],[963,689],[914,664])],
'B':[room('living',[701,837],[739,807],[644,788]),room('bedroom-1',[727,870],[712,914],[691,885]),room('master',[657,916],[657,940],[620,914])],
'C':[room('living',[340,809],[382,836],[429,787]),room('bedroom-1',[354,870],[370,914],[390,882]),room('master',[423,916],[423,940],[465,914])],
'D':[room('living',[308,772],[336,803],[359,716]),room('bedroom-1',[265,778],[287,780],[277,750]),room('bedroom-2',[139,726],[139,776],[188,751]),room('master',[139,639],[139,692],[188,664])],
'E':[room('living',[307,443],[333,405],[358,487]),room('bedroom-1',[265,430],[287,427],[277,460]),room('bedroom-2',[138,433],[138,486],[188,458]),room('master',[138,515],[138,570],[188,541])],
'F':[room('living',[337,401],[380,374],[435,414]),room('bedroom-1',[365,296],[351,339],[389,320]),room('master',[419,267],[419,293],[462,293])],
'G':[room('living',[698,374],[737,399],[642,413]),room('bedroom-1',[713,295],[726,339],[688,320]),room('master',[658,267],[658,291],[620,296])],
'H':[room('living',[742,400],[780,434],[730,486]),room('bedroom-1',[795,427],[816,429],[804,460]),room('bedroom-2',[963,431],[963,485],[915,458]),room('master',[963,516],[963,569],[915,542])]
}
add('L05',o5,r5,[540,603],'32/34 B/C inset differs from 35/37 standard main rooms; preserve both.')
o6=[[514,278],[595,278],[595,413],[654,413],[654,278],[738,278],[738,306],[805,306],[805,350],[774,380],[847,453],[875,421],[889,435],[1010,435],[1010,572],[780,572],[780,632],[1010,632],[1010,770],[889,770],[875,782],[847,752],[819,791],[776,822],[806,852],[806,899],[737,899],[737,925],[654,925],[654,760],[595,760],[595,925],[514,925],[514,899],[445,899],[445,852],[475,822],[433,791],[391,754],[371,784],[357,769],[216,769],[216,632],[465,632],[465,572],[216,572],[216,435],[357,435],[371,422],[392,444],[475,380],[443,350],[443,306],[514,306]]
r6={
'A':[room('living',[393,756],[430,789],[433,703]),room('bedroom-1',[358,769],[379,769],[368,740]),room('bedroom-2',[218,716],[218,766],[270,741]),room('master',[218,636],[218,687],[269,661])],
'B':[room('living',[435,793],[472,821],[521,780]),room('bedroom-1',[446,855],[461,899],[482,872]),room('master',[514,902],[514,923],[548,900])],
'C':[room('living',[779,822],[816,792],[720,783]),room('bedroom-1',[804,855],[790,898],[770,872]),room('master',[737,902],[737,923],[700,900])],
'D':[room('living',[820,788],[844,754],[810,701]),room('bedroom-1',[867,771],[887,769],[876,740]),room('bedroom-2',[1008,716],[1008,767],[964,742]),room('master',[1008,635],[1008,687],[962,662])],
'E':[room('living',[820,408],[844,448],[810,488]),room('bedroom-1',[867,434],[887,436],[876,464]),room('bedroom-2',[1008,438],[1008,488],[963,462]),room('master',[1008,518],[1008,569],[964,543])],
'F':[room('living',[778,382],[815,405],[720,420]),room('bedroom-1',[791,307],[804,349],[769,331]),room('master',[737,280],[737,304],[699,306])],
'G':[room('living',[433,405],[472,381],[525,420]),room('bedroom-1',[457,307],[444,349],[480,331]),room('master',[515,280],[515,304],[553,306])],
'H':[room('living',[394,443],[430,408],[430,488]),room('bedroom-1',[358,435],[379,434],[368,464]),room('bedroom-2',[218,438],[218,488],[270,461]),room('master',[218,518],[218,569],[270,543])]
}
add('L06',o6,r6,[624,604],'Reflected G3; 33 B/C inset differs from 36 main rooms.')
# 38 is NOT merged: notched B/C master-room ends and living-wall articulation.
o7=[[471,403],[555,403],[555,535],[611,535],[611,403],[695,403],[695,431],[758,431],[758,473],[728,504],[800,568],[827,542],[840,555],[958,555],[958,688],[735,688],[735,746],[958,746],[958,879],[840,879],[827,890],[800,865],[773,903],[759,896],[741,937],[746,958],[746,1016],[694,1016],[694,1040],[653,1040],[653,1029],[637,1029],[622,1043],[616,1030],[615,861],[555,861],[555,1040],[516,1040],[516,1029],[500,1029],[487,1042],[477,1030],[477,1016],[423,1016],[423,956],[429,943],[398,906],[355,867],[336,893],[324,879],[188,879],[188,746],[431,746],[431,690],[188,690],[188,555],[324,555],[339,542],[357,564],[439,504],[408,474],[408,432],[471,432]]
r7={
'A':[room('living',[358,869],[397,903],[399,819]),room('bedroom-1',[326,879],[346,878],[336,850]),room('bedroom-2',[189,826],[189,875],[241,850]),room('master',[189,750],[189,798],[241,776])],
'B':[room('living',[401,906],[428,939],[486,887]),room('bedroom-1',[424,957],[424,1008],[452,987]),room('master',[519,1038],[552,1038],[530,1000])],
'C':[room('living',[744,934],[764,902],[691,886]),room('bedroom-1',[744,961],[744,1008],[719,987]),room('master',[656,1038],[691,1038],[672,1000])],
'D':[room('living',[775,900],[797,866],[762,814]),room('bedroom-1',[819,879],[839,878],[828,850]),room('bedroom-2',[955,828],[955,875],[911,851]),room('master',[955,750],[955,799],[911,775])],
'E':[room('living',[774,532],[796,567],[762,611]),room('bedroom-1',[819,554],[839,556],[828,585]),room('bedroom-2',[955,560],[955,608],[910,585]),room('master',[955,636],[955,684],[910,660])],
'F':[room('living',[731,505],[771,528],[680,544]),room('bedroom-1',[745,432],[757,473],[720,453]),room('master',[694,406],[694,429],[657,431])],
'G':[room('living',[398,529],[436,506],[487,544]),room('bedroom-1',[421,433],[409,473],[445,454]),room('master',[472,406],[472,430],[509,432])],
'H':[room('living',[359,564],[394,532],[400,611]),room('bedroom-1',[326,556],[346,554],[336,585]),room('bedroom-2',[189,560],[189,609],[241,585]),room('master',[189,638],[189,685],[240,661])]
}
for flat,left,right in [('B',426,473),('C',697,743)]:
 r7[flat][1][1:3]=[[left,1015],[right,1015]]
 r7[flat][2][0]='bedroom-2'
add('L07',o7,r7,[583,716],'38 retained separately: notched bottom B/C rooms. Source calls both bedrooms without master designation: bedroom-1 is nearer living and bedroom-2 farther, no invented master label. Bedroom-1 uses thin horizontal sill at bottom, not thick vertical side wall.')
# Tower 9/18: distinct core with three lifts to the right; independent tracing.
o8=[[320,277],[495,277],[495,511],[573,511],[573,277],[750,277],[750,430],[766,449],[747,469],[785,520],[830,563],[854,538],[912,538],[912,622],[945,622],[945,730],[710,730],[710,804],[945,804],[945,912],[911,912],[911,997],[854,997],[831,974],[786,1010],[747,1056],[766,1088],[749,1107],[749,1285],[572,1285],[572,1060],[495,1060],[495,1285],[319,1285],[319,1107],[300,1088],[320,1065],[285,1010],[242,972],[213,996],[154,996],[154,912],[118,912],[118,804],[355,804],[355,730],[118,730],[118,622],[154,622],[154,538],[213,538],[242,563],[285,521],[321,474],[304,448],[320,431]]
r8={
'A':[room('living',[287,1013],[326,1054],[408,996]),room('master',[425,1280],[490,1280],[450,1230]),room('bedroom-2',[322,1280],[388,1280],[355,1230]),room('bedroom-1',[303,1084],[319,1104],[355,1102])],
'B':[room('living',[245,974],[283,1008],[304,906]),room('master',[120,878],[155,909],[165,854]),room('bedroom-1',[157,993],[210,993],[184,949])],
'C':[room('living',[245,561],[283,525],[305,614]),room('master',[120,625],[155,625],[165,678]),room('bedroom-1',[157,541],[210,541],[185,589])],
'D':[room('living',[287,519],[325,478],[409,528]),room('master',[426,279],[491,279],[455,336]),room('bedroom-2',[323,279],[389,279],[355,336]),room('bedroom-1',[306,447],[321,431],[355,449])],
'E':[room('living',[746,477],[782,518],[665,528]),room('master',[577,279],[644,279],[610,333]),room('bedroom-2',[679,279],[746,279],[713,335]),room('bedroom-1',[748,433],[763,447],[718,450])],
'F':[room('living',[786,523],[827,562],[765,614]),room('master',[913,625],[943,625],[905,679]),room('bedroom-1',[858,541],[909,541],[886,587])],
'G':[room('living',[829,975],[787,1008],[765,913]),room('master',[915,909],[943,879],[901,860]),room('bedroom-1',[858,994],[908,994],[884,949])],
'H':[room('living',[783,1013],[744,1055],[665,994]),room('master',[577,1280],[643,1280],[610,1232]),room('bedroom-2',[678,1280],[744,1280],[715,1230]),room('bedroom-1',[763,1087],[747,1103],[717,1102])]
}
for f,x,y1,y2 in [('B',119,809,908),('C',119,626,726),('F',944,626,726),('G',944,809,908)]:
 next(row for row in r8[f] if row[0]=='master')[1:3]=[[x,y1],[x,y2]]
add('L08',o8,r8,[533,781],'Distinct rotated core and plan dimensions. Bedroom identities follow explicit room labels and adjacency, not G1 label order. Master bays use the longest outer pane, excluding short return panes.')
# Towers 10/11/21/22: own dimensions and core, outer main panes traced.
o9=[[424,153],[477,153],[477,163],[498,163],[498,153],[549,153],[549,326],[601,326],[601,153],[654,153],[654,163],[674,163],[674,153],[725,153],[725,260],[737,271],[724,284],[750,322],[779,351],[796,334],[841,334],[841,397],[864,397],[864,470],[701,470],[701,522],[864,522],[864,599],[841,599],[841,660],[798,660],[777,642],[749,670],[719,706],[737,724],[725,736],[725,862],[673,862],[673,851],[653,851],[653,862],[601,862],[601,707],[549,707],[549,862],[495,862],[495,851],[477,851],[477,862],[423,862],[423,736],[410,724],[425,708],[397,670],[371,642],[350,657],[308,657],[308,597],[281,597],[281,521],[447,521],[447,470],[283,470],[283,396],[308,396],[308,334],[350,334],[370,353],[398,322],[427,285],[412,271],[424,257]]
r9={
'A':[room('living',[718,704],[745,673],[665,659]),room('master',[604,859],[650,859],[626,826]),room('bedroom-2',[676,859],[720,859],[695,825]),room('bedroom-1',[723,712],[735,725],[699,736])],
'B':[room('living',[752,668],[775,644],[734,600]),room('master',[841,595],[861,575],[833,552]),room('bedroom-1',[798,657],[837,657],[815,626])],
'C':[room('living',[752,326],[775,350],[733,401]),room('master',[842,400],[862,421],[833,445]),room('bedroom-1',[798,337],[837,337],[815,367])],
'D':[room('living',[719,288],[746,319],[663,333]),room('master',[604,156],[650,156],[626,195]),room('bedroom-2',[677,156],[721,156],[697,193]),room('bedroom-1',[724,260],[735,272],[698,274])],
'E':[room('living',[400,319],[427,288],[482,333]),room('master',[502,156],[545,156],[520,193]),room('bedroom-2',[427,156],[473,156],[450,190]),room('bedroom-1',[414,270],[426,260],[451,274])],
'F':[room('living',[372,352],[396,324],[406,397]),room('master',[286,399],[306,399],[315,435]),room('bedroom-1',[310,337],[346,337],[330,367])],
'G':[room('living',[372,643],[396,666],[409,600]),room('master',[283,576],[307,595],[316,554]),room('bedroom-1',[311,654],[346,654],[330,621])],
'H':[room('living',[400,672],[427,704],[480,658]),room('master',[502,859],[546,859],[520,825]),room('bedroom-2',[427,859],[471,859],[450,825]),room('bedroom-1',[413,724],[426,712],[450,736])]
}
for f,x,y1,y2 in [('B',863,526,594),('C',863,402,467),('F',284,401,467),('G',283,526,593)]:
 next(row for row in r9[f] if row[0]=='master')[1:3]=[[x,y1],[x,y2]]
for f,y1,y2 in [('B',603,654),('C',340,392)]:
 next(row for row in r9[f] if row[0]=='bedroom-1')[1:3]=[[840,y1],[840,y2]]
add('L09',o9,r9,[574,507],'Source explicitly says 11/21/22 arrangements differ; semantic A-H anchors must determine reflection independently per tower.')
# 12/23: B/C have distinct outer shoulder/bedroom geometry; keep separate.
o10=[[432,172],[485,172],[485,181],[507,181],[507,172],[557,172],[557,347],[611,347],[611,172],[662,172],[662,182],[684,182],[684,172],[737,172],[737,279],[749,290],[733,306],[760,339],[792,370],[815,352],[831,365],[868,365],[868,415],[889,415],[889,488],[722,488],[722,543],[889,543],[889,618],[868,618],[868,667],[832,667],[815,682],[792,657],[760,691],[733,728],[749,746],[737,758],[737,884],[685,884],[685,872],[663,872],[663,884],[612,884],[612,728],[559,728],[559,884],[507,884],[507,874],[485,874],[485,884],[433,884],[433,758],[422,746],[435,730],[408,693],[380,663],[359,679],[315,679],[315,619],[290,619],[290,542],[459,542],[459,490],[290,490],[290,415],[315,415],[315,353],[359,353],[379,371],[407,340],[435,307],[422,290],[432,278]]
r10=copy.deepcopy(r9)
# Independent room endpoints on this sheet (not applying a global bbox fit).
r10={
'A':[room('living',[734,725],[757,693],[679,686]),room('master',[615,881],[660,881],[636,844]),room('bedroom-2',[687,881],[732,881],[709,843]),room('bedroom-1',[736,735],[746,747],[709,757])],
'B':[room('living',[763,686],[789,658],[751,616]),room('master',[887,548],[887,614],[856,579]),room('bedroom-1',[835,666],[864,666],[842,642])],
'C':[room('living',[763,343],[788,368],[749,414]),room('master',[887,420],[887,484],[853,451]),room('bedroom-1',[835,367],[864,367],[843,392])],
'D':[room('living',[734,309],[757,336],[674,354]),room('master',[614,175],[659,175],[637,212]),room('bedroom-2',[687,175],[732,175],[709,209]),room('bedroom-1',[737,281],[747,291],[709,292])],
'E':[room('living',[410,337],[434,310],[494,354]),room('master',[511,175],[552,175],[532,214]),room('bedroom-2',[435,175],[482,175],[458,211]),room('bedroom-1',[424,290],[435,279],[458,293])],
'F':[room('living',[382,369],[405,344],[415,414]),room('master',[292,418],[313,418],[324,454]),room('bedroom-1',[318,356],[355,356],[335,388])],
'G':[room('living',[382,664],[405,689],[416,620]),room('master',[292,598],[313,616],[324,575]),room('bedroom-1',[318,676],[356,676],[335,644])],
'H':[room('living',[410,696],[435,725],[493,686]),room('master',[511,881],[554,881],[532,844]),room('bedroom-2',[435,881],[483,881],[459,844]),room('bedroom-1',[424,746],[435,735],[460,757])]
}
for f,x,y1,y2 in [('F',292,419,486),('G',292,547,613)]:
 next(row for row in r10[f] if row[0]=='master')[1:3]=[[x,y1],[x,y2]]
for f,y1,y2 in [('B',623,664),('C',368,411)]:
 next(row for row in r10[f] if row[0]=='bedroom-1')[1:3]=[[866,y1],[866,y2]]
add('L10',o10,r10,[586,526],'B/C different 522sf shoulders and windows vs L09; 23 requires independent reflection semantics.')
# 19/20: D/E reduced bedrooms, separate C/B inset at Tower20.
o11=[[458,158],[537,158],[537,313],[590,313],[590,158],[662,158],[662,180],[720,180],[720,250],[719,261],[704,280],[733,312],[756,335],[768,324],[782,335],[832,335],[832,385],[852,385],[852,452],[696,452],[696,505],[852,505],[852,576],[832,576],[832,626],[780,626],[768,636],[751,615],[730,644],[701,680],[719,699],[709,715],[709,831],[589,831],[589,680],[537,680],[537,831],[419,831],[419,715],[405,699],[421,683],[395,648],[368,616],[347,634],[308,634],[308,576],[283,576],[283,505],[443,505],[443,453],[283,453],[283,383],[308,383],[308,321],[347,321],[368,339],[395,309],[423,280],[409,261],[420,249],[413,249],[413,180],[458,180]]
r11={
'A':[room('living',[702,677],[727,647],[661,641]),room('master',[593,829],[637,829],[614,793]),room('bedroom-2',[661,829],[704,829],[682,793]),room('bedroom-1',[708,688],[718,700],[680,712])],
'B':[room('living',[732,641],[750,618],[720,572]),room('master',[850,509],[850,571],[816,542]),room('bedroom-1',[787,624],[829,624],[806,594])],
'C':[room('living',[735,316],[754,338],[718,385]),room('master',[850,389],[850,448],[815,419]),room('bedroom-1',[787,338],[829,338],[806,365])],
'D':[room('living',[706,282],[731,309],[656,327]),room('master',[594,160],[657,160],[626,198]),room('bedroom-2',[717,184],[717,218],[684,204]),room('bedroom-1',[717,251],[706,265],[680,266])],
'E':[room('living',[397,307],[420,282],[479,327]),room('master',[462,160],[534,160],[506,198]),room('bedroom-2',[414,185],[414,218],[445,202]),room('bedroom-1',[411,251],[422,265],[444,266])],
'F':[room('living',[370,337],[392,312],[403,385]),room('master',[285,385],[306,385],[318,421]),room('bedroom-1',[310,324],[344,324],[330,355])],
'G':[room('living',[370,618],[392,644],[403,570]),room('master',[285,556],[306,574],[318,538]),room('bedroom-1',[310,631],[344,631],[330,600])],
'H':[room('living',[398,650],[421,679],[475,641]),room('master',[477,829],[534,829],[506,793]),room('bedroom-2',[422,829],[465,829],[445,793]),room('bedroom-1',[408,699],[420,688],[447,712])]
}
for f,x,y1,y2 in [('F',285,386,449),('G',285,509,573)]:
 next(row for row in r11[f] if row[0]=='master')[1:3]=[[x,y1],[x,y2]]
for f,y1,y2 in [('B',581,621),('C',340,381)]:
 next(row for row in r11[f] if row[0]=='bedroom-1')[1:3]=[[831,y1],[831,y2]]
add('L11',o11,r11,[565,496],'D/E 661sf differs from 687sf L09; Tower20 C/B inset needs independent glazing transfer. No merge with G5.')
# Explicit inset variants. Main-plan living/core geometry is retained, while
# the independent inset glazing replaces only the affected B/C rooms.
special=copy.deepcopy(templates['L01-special']);native=templates['L02']['sourceCanvasTransform']
def native_point(p):return [-p[0]*native['scale']+native['translation'][0],p[1]*native['scale']+native['translation'][1]]
special['outline']=[native_point(p) for p in special['outline']]
special['core']=native_point(special['core'])
for rows in special['rooms'].values():
 for row in rows:row[1:]=[native_point(p) for p in row[1:]]
special['cornerGlazing']={f:[native_point(p) for p in points] for f,points in special['cornerGlazing'].items()}
special.update(sourceSheet='L02',canvas=templates['L02']['canvas'],source=templates['L02']['source'],sourceCanvasTransform=native,reviewNotes='Tower15 B/C inset confirmed mirrored counterpart of L01 1/13 inset; same bathroom and bedroom adjacency. Uses recorded six-landmark source reflection, not map pixels.')
templates['L02-special']=special
a=copy.deepcopy(templates['L11']);a['sourceSheet']='L11'
a['rooms']['C'][1]=room('master',[866,381],[866,402],[815,419]);a['rooms']['C'][2]=room('bedroom-1',[799,322],[837,322],[806,365])
a['rooms']['B'][1]=room('master',[866,568],[866,591],[815,542]);a['rooms']['B'][2]=room('bedroom-1',[795,645],[836,645],[806,594])
a['insetTranslations']={'C':[20,161],'B':[20,-180]}
a['reviewNotes']='Tower20 B/C labelled insets replace main east-facing small bedroom pane with horizontal top/bottom sill. Match bathroom/door partition vertical and horizontal corners in same image; C source (753,224)-(774,291) to main (773,385)-(794,452); B corresponding partition translation (20,-180). Master uses projecting bay short outer face visible in inset. No estate screenshot scale used.'
templates['L11-special']=a
a=copy.deepcopy(templates['L04']);a['sourceSheet']='L04'
a['rooms']['B'][1]=room('bedroom-1',[376,1133],[376,1187],[418,1157]);a['rooms']['B'][2]=room('master',[457,1185],[490,1220],[502,1180])
a['rooms']['C'][1]=room('bedroom-1',[810,1133],[810,1187],[768,1157]);a['rooms']['C'][2]=room('master',[729,1185],[696,1220],[684,1180])
a['reviewNotes']='25/30 explicit standard B/C insets: bedroom outer vertical pane and master L-corner chord. Aligned to main bathroom partition; special 522sf main B/C excluded.'
a['insetTranslations']={'B':[276,-15],'C':[-283,-14]};templates['L04-standard']=a
a=copy.deepcopy(templates['L05']);a['sourceSheet']='L05'
for f,x in [('B',720),('C',360)]:
 a['rooms'][f][1]=room('bedroom-1',[x,850],[x,884],[x+(-35 if f=='B' else 35),880])
a['rooms']['B'][2]=room('master',[575,950],[655,950],[615,912]);a['rooms']['C'][2]=room('master',[425,950],[505,950],[465,912])
a['reviewNotes']='32/34 special B/C inset: pointed corner glazing and long bottom master pane, not standard vertical master corner.'
a['insetTranslations']={'B':[-232,8],'C':[285,-4]};templates['L05-special']=a
a=copy.deepcopy(templates['L06']);a['sourceSheet']='L06'
a['rooms']['B'][1]=room('bedroom-1',[456,839],[456,872],[488,868]);a['rooms']['C'][1]=room('bedroom-1',[793,839],[793,872],[760,868])
a['rooms']['B'][2]=room('master',[515,930],[592,930],[550,895]);a['rooms']['C'][2]=room('master',[657,930],[734,930],[695,895])
a['reviewNotes']='33 B/C source inset: pointed bedroom corner and full horizontal master glazing; 36 standard rooms excluded.'
a['insetTranslations']={'B':[220,-6],'C':[-220,-6]};templates['L06-special']=a
for id,a in templates.items():
 a['sourceSheet']=a.get('sourceSheet',id);a['planInterpretationConfidence']='visually-traced';a['windowVerified']=False
path=JOB/'templates';path.mkdir(exist_ok=True)
for id,a in templates.items():
 (path/f'{id}.json').write_text(json.dumps(a,indent=2)+'\n')
 im=Image.open(JOB/f"floorplans/full/{a['sourceSheet']}.jpg").resize(tuple(a['canvas']));d=ImageDraw.Draw(im)
 d.line([tuple(p) for p in a['outline']+[a['outline'][0]]],fill='blue',width=2)
 for flat,rows in a['rooms'].items():
  for kind,p,q,inside in rows:
   d.line([tuple(p),tuple(q)],fill='red',width=3);d.ellipse((inside[0]-2,inside[1]-2,inside[0]+2,inside[1]+2),fill='green');d.text(tuple(p),flat+'/'+kind,fill='red')
 im.save(path/f'{id}-traced.png')
print('Saved',len(templates),'separate reviewed source/variant traces')
