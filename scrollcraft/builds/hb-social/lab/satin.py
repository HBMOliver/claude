import numpy as np, sys
from PIL import Image
W,H=2400,1500; seed=int(sys.argv[1]); out=sys.argv[2]
rng=np.random.default_rng(seed)
def field(sx,sy):
    n=rng.standard_normal((H,W))
    fy=np.fft.fftfreq(H)[:,None]; fx=np.fft.fftfreq(W)[None,:]
    g=np.exp(-((fx*sx)**2+(fy*sy)**2))
    f=np.real(np.fft.ifft2(np.fft.fft2(n)*g)); return f/f.std()
y,x=np.mgrid[0:H,0:W].astype(np.float64)
warp=field(700,420)*160
# long diagonal folds: sinusoids along a warped coordinate
u=(x*0.94+y*0.34)+warp
h=0.0
for k,(fr,a,ph) in enumerate([(1/760,1.0,0.3),(1/400,0.42,1.7),(1/230,0.12,2.9)]):
    h=h+a*np.sin(2*np.pi*fr*u+ph+field(1100,700)*0.5)
h=h+0.35*field(900,520)
h*=60
gy,gx=np.gradient(h)
nx,ny,nz=-gx,-gy,np.ones_like(h)
l=np.sqrt(nx**2+ny**2+nz**2); nx/=l; ny/=l; nz/=l
L=np.array([-0.55,-0.45,0.70]); L/=np.linalg.norm(L)
diff=np.clip(nx*L[0]+ny*L[1]+nz*L[2],0,1)
Hv=L+np.array([0,0,1.0]); Hv/=np.linalg.norm(Hv)
spec=np.clip(nx*Hv[0]+ny*Hv[1]+nz*Hv[2],0,1)**38
base=np.array([74,27,32])/255.0
hi=np.array([240,190,176])/255.0
col=base[None,None,:]*(0.25+0.95*diff[...,None])+hi[None,None,:]*0.42*spec[...,None]
# vignette, light from upper left
cx,cy=0.36*W,0.30*H
r=np.sqrt(((x-cx)/W)**2+((y-cy)/H)**2)
vig=np.clip(1.15-1.25*r,0.22,1)[...,None]
col=col*vig
col+= (rng.standard_normal((H,W,1))*0.006)  # dither, kills banding
img=(np.clip(col,0,1)**(1/1.0)*255+0.5).astype(np.uint8)
Image.fromarray(img).save(out,quality=86)
