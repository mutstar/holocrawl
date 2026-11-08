"""Frozen concrete92 material renderer for new native map previews."""
import numpy as np

def near(a,dx,dy):
    out=np.zeros_like(a);h,w=a.shape;x0,x1=max(0,-dx),min(w,w-dx);y0,y1=max(0,-dy),min(h,h-dy)
    out[y0:y1,x0:x1]=a[y0+dy:y1+dy,x0+dx:x1+dx];return out

def render(base,rows,grain):
    cell=np.array([[c=='#' for c in r] for r in rows]);solid=np.array([[c in '#+G' for c in r] for r in rows])
    up=lambda a:np.repeat(np.repeat(a,32,axis=0),32,axis=1)
    wall=up(cell);e,s,se=[up(near(solid,dx,dy)) for dx,dy in [(1,0),(0,1),(1,1)]]
    yy,xx=np.indices(wall.shape);px,py=xx%32,yy%32
    raw_front=wall&(py>=18)&~s
    # Three-pixel east face, with a diagonal mitre into the bottom14px front.
    # At a convex SE corner its width tapers3,2,1,0 instead of a black post.
    corner=wall&~e&~s&(py>=18)
    cut=29+((py-18)*3//13)
    side=wall&(px>=29)&(~e|((py>=18)&~se))&~(raw_front&e)
    side=np.where(corner,wall&(px>=cut),side)
    front=raw_front&~side
    # A separate west-facing stripe made two adjacent borders. Fold it into
    # the continuous coping footprint instead of adding another strip.
    cap=wall&~front&~side
    assert np.all((cap.astype('uint8')+front+side)[wall]==1)
    tex=grain[yy%grain.shape[0],xx%grain.shape[1]].mean(axis=2)
    noise=tex-tex.mean();a=base.copy()
    for mask,color,factor in [(cap,[31,37,40],.30),(front,[52,62,67],.65),(side,[48,58,64],.52)]:
        rgb=np.array(color)[None,None,:]+noise[:,:,None]*factor
        a[mask,:3]=np.clip(np.rint(rgb[mask]),0,255).astype('uint8')
    n=cap&~near(cap,0,-4);sedge=cap&~near(cap,0,4)
    w=cap&~near(cap,-4,0);edge=cap&~near(cap,4,0);rim=n|sedge|w|edge
    # Cardinal-only bands miss the4x4 square immediately behind an inside
    # corner. A diagonal footprint completes that same-width coping turn.
    diagonal=cap&(~near(cap,-4,-4)|~near(cap,4,-4)|~near(cap,-4,4)|~near(cap,4,4))
    repaired=diagonal&~rim
    rim|=repaired
    for k,c in enumerate([116,125,129]):
        layer=a[:,:,k];layer[rim]=np.clip(c+noise[rim]*.52,0,255).astype('uint8')
    # One joined bevel, with a moderate lighting change between its planes.
    north=cap&~near(cap,0,-1);west=cap&~near(cap,-1,0)
    south=cap&~near(cap,0,1);east=cap&~near(cap,1,0)
    a[north,:3]=[134,144,148];a[west,:3]=[124,136,141]
    a[south,:3]=[90,107,112];a[east,:3]=[87,105,111]
    for dx,dy,color in [(-1,-1,[129,140,145]),(1,-1,[110,125,130]),(-1,1,[107,121,126]),(1,1,[89,106,112])]:
        tip=cap&near(cap,dx,0)&near(cap,0,dy)&~near(cap,dx,dy)
        a[tip,:3]=color
        repaired|=tip
    # The front and side now share material and meet at the sloped corner.
    a[front&near(cap,0,-1),:3]=[49,65,70]
    a[side&near(cap,-1,0),:3]=[60,79,84]
    # Put joints only on straight runs, away from inside/outside turns.
    horizontal=n|sedge;vertical=w|edge
    straight_h=horizontal&near(horizontal,-4,0)&near(horizontal,4,0)
    straight_v=vertical&near(vertical,0,-4)&near(vertical,0,4)
    joints=((xx%48==0)&straight_h)|((yy%48==0)&straight_v)
    a[joints,:3]=(a[joints,:3].astype(float)*.83).astype('uint8')
    construction=front&(xx%64==0)&~near(side,1,0)
    a[construction,:3]=(a[construction,:3].astype(float)*.83).astype('uint8')
    holes=front&(yy%32==24)&(xx%48==14);a[holes,:3]=[41,52,56]
    # Pixel checks concern the repaired corner geometry, not visual preference.
    for y in range(len(rows)):
        for x in range(len(rows[0])):
            if not cell[y,x] or (x+1<len(rows[0]) and solid[y,x+1]) or (y+1<len(rows) and solid[y+1,x]):continue
            widths=side[y*32+18:y*32+32,x*32:(x+1)*32].sum(axis=1)
            assert np.all(widths[:-1]>=widths[1:]) and widths[-1]==0 and widths[0]==3
    assert np.array_equal(a[~wall],base[~wall]) and np.array_equal(a[:,:,3],base[:,:,3])
    return a,wall,repaired

