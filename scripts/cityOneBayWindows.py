"""v6.2 additions transcribed from each canonical plan, in its reference canvas.
The approved samples establish the bay symbol; these endpoints come from the tower
source, never from sample coordinates or government geometry. Shared projecting
faces are split at the actual separating room wall.
"""
def extend_traces(traces):
    def add(t,f,r,p,q,side,kind='bay-window-face'):
        delta={'E':(45,0),'W':(-45,0),'N':(0,-45),'S':(0,45)}[side]
        witness=[(p[i]+q[i])/2+delta[i] for i in range(2)]
        traces[t]=[w for w in traces[t] if (w['flat'],w['id'])!=(f,r)]
        traces[t].append(dict(flat=f,id=r,p1=p,p2=q,interiorWitness=witness,
          representationClass=kind,recognitionEvidence='builtin-city-one-bay-closeup' if kind!='sill-line' else 'u-1789321451497-a6z0fr',
          sourceExtentRole='primary viewing face of approved repeated bay module' if kind!='sill-line' else 'visible glazing line'))
    def h(t,f,r,y,x1,x2,s):add(t,f,r,[x1,y],[x2,y],s)
    def v(t,f,r,x,y1,y2,s):add(t,f,r,[x,y1],[x,y2],s)
    # Four-wing A-D source: narrow secondary living glazing is retained separately.
    for f,y,x1,x2,s in [('C',75,367,407,'S'),('D',75,810,849,'S'),('B',754,371,410,'N'),('A',754,809,849,'N')]:h(4,f,'living',y,x1,x2,s)
    for f,y,x1,x2,s in [('C',94,129,156,'S'),('D',94,1058,1084,'S'),('B',747,130,157,'N'),('A',747,1051,1079,'N')]:h(4,f,'bedroom-2',y,x1,x2,s)
    for f,y,x1,x2,s in [('C',94,284,310,'S'),('D',94,905,931,'S'),('B',747,283,310,'N'),('A',747,902,930,'N')]:h(4,f,'bedroom-3',y,x1,x2,s)
    # Purple first-type: paired bedrooms share one projected straight face.
    for f,x,a,m,b,s in [('E',365,612,665,708,'E'),('F',924,613,665,709,'W'),('B',368,1429,1475,1530,'E'),('A',927,1429,1475,1530,'W')]:
        v(16,f,'bedroom-1',x,a,m-3,s);v(16,f,'bedroom-2',x,m+3,b,s)
    # Inner south rooms have a small glazing interruption facing the lightwell.
    for f,x,s in [('B',587,'W'),('A',708,'E')]:add(16,f,'bedroom-3',[x,1468],[x,1491],s,'sill-line')
    # Six-flat second-type: every large projection is a bay, not a service ledge.
    for f,x,a,m,b,s in [('D',335,685,733,778,'E'),('E',948,681,730,775,'W'),('B',338,1388,1436,1483,'E'),('A',952,1387,1433,1478,'W')]:
        v(18,f,'bedroom-1',x,a,m-3,s);v(18,f,'bedroom-2',x,m+3,b,s)
    for f,x,a,b,s in [('D',336,874,923,'E'),('E',948,871,919,'W'),('B',338,1270,1307,'E'),('A',951,1268,1302,'W')]:v(18,f,'living',x,a,b,s)
    for f,y,x1,x2,s in [('C',1262,309,334,'N'),('F',1255,952,979,'N')]:h(18,f,'living',y,x1,x2,s)
    for f,y,x1,x2,s in [('C',1262,186,227,'N'),('F',1254,1072,1106,'N')]:h(18,f,'bedroom-2',y,x1,x2,s)
    # C/F other bedrooms use narrow visible openings, not the adjacent AC rectangle.
    for f,p,q,s in [('C',[151,1015],[195,1015],'S'),('F',[1095,1007],[1140,1007],'S')]:add(18,f,'bedroom-1',p,q,s,'sill-line')
    for f,p,q,s in [('C',[364,981],[364,1008],'E'),('F',[919,978],[919,1005],'W')]:add(18,f,'bedroom-3',p,q,s,'sill-line')
    # Black/white variants: explicit label remap, both canonical images inspected.
    for t,fs in [(19,'ABFE'),(30,'EFBA')]:
        for f,x,a,m,b,s in zip(fs,[224,825,227,828],[99,97,931,930],[148,147,979,978],[196,192,1027,1025],['E','W','E','W']):
            v(t,f,'bedroom-1',x,a,m-3,s);v(t,f,'bedroom-2',x,m+3,b,s)
    # Four flats in 25 and 27: dominant straight face of each trapezoid.
    for t in [25,27]:
        for f,y,x1,x2,s in [('C',132,331,378,'S'),('D',128,732,773,'S'),('B',750,330,378,'N'),('A',746,731,773,'N')]:h(t,f,'living',y,x1,x2,s)
        for f,x,a,b,s in [('C',34,266,313,'E'),('D',1074,264,309,'W'),('B',34,570,610,'E'),('A',1074,567,607,'W')]:v(t,f,'bedroom-1',x,a,b,s)
        for f,y,x1,x2,s in [('C',120,103,169,'S'),('D',113,934,1001,'S'),('B',764,103,169,'N'),('A',758,934,1001,'N')]:h(t,f,'bedroom-2',y,x1,x2,s)
        for f,y,x1,x2,s in [('C',132,244,282,'S'),('D',128,821,859,'S'),('B',750,244,282,'N'),('A',746,821,859,'N')]:h(t,f,'bedroom-3',y,x1,x2,s)
    # Rectangular projected window modules; primary outer straight face only.
    for t,flats in [(37,dict(nw='G',ne='H',wu='F',eu='A',wl='E',el='B',sw='D',se='C')),
                    (42,dict(nw='C',ne='D',wu='B',eu='E',wl='A',el='F',sw='H',se='G'))]:
        for pos,y,s in [('nw',89,'S'),('ne',89,'S'),('sw',1152,'N'),('se',1152,'N')]:
            xs=[(300,369),(418,478)] if pos in ['nw','sw'] else [(619,678),(728,797)]
            for i,(x1,x2) in enumerate(xs):h(t,flats[pos],f'bedroom-{i+1}',y,x1,x2,s)
        for pos,x,ys,s in [('wu',84,[(379,443),(494,555)],'E'),('eu',1012,[(379,443),(494,555)],'W'),('wl',84,[(686,748),(797,861)],'E'),('el',1012,[(686,748),(797,861)],'W')]:
            for i,(a,b) in enumerate(ys):v(t,flats[pos],f'bedroom-{i+1}',x,a,b,s)
        for pos,y,x1,x2,s in [('wu',343,205,275,'S'),('eu',343,823,892,'S'),('wl',897,205,275,'N'),('el',897,823,892,'N')]:h(t,flats[pos],'living',y,x1,x2,s)
    # Tower 34/35: inner bedroom's main bay and the outer bedroom/living modules.
    for f,y,x1,x2,s in [('B',53,365,395,'S'),('C',53,648,678,'S'),('A',1119,366,395,'N'),('D',1119,648,678,'N')]:h(34,f,'bedroom-3',y,x1,x2,s)
    for f,x,ys,s in [('B',166,[(109,164),(239,277)],'E'),('C',874,[(109,164),(239,277)],'W'),('A',166,[(896,933),(997,1059)],'E'),('D',874,[(896,933),(997,1059)],'W')]:
        for i,(a,b) in enumerate(ys):v(34,f,f'bedroom-{i+1}',x,a,b,s)
    for f,x,a,b,s in [('B',165,344,390,'E'),('C',875,344,390,'W'),('A',165,779,825,'E'),('D',875,779,825,'W')]:v(34,f,'living',x,a,b,s)
    # Tower 36: two rectangular outer bedroom modules per wing.
    for f,x,ys,s in [('A',269,[(132,185),(239,290)],'E'),('B',829,[(132,185),(239,290)],'W'),('F',269,[(965,1017),(1070,1120)],'E'),('E',829,[(965,1017),(1070,1120)],'W'),('H',76,[(401,451),(503,552)],'E'),('C',1022,[(401,451),(503,552)],'W'),('G',76,[(699,749),(799,850)],'E'),('D',1022,[(699,749),(799,850)],'W')]:
        for i,(a,b) in enumerate(ys):v(36,f,f'bedroom-{i+1}',x,a,b,s)
    for rows in traces.values():
        for w in rows:
            w.setdefault('representationClass','sill-line')
            w.setdefault('recognitionEvidence','u-1789321451497-a6z0fr')
