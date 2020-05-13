u(t) is called 60 times per second.
t: Elapsed time in seconds.
S: Shorthand for Math.sin.
C: Shorthand for Math.cos.
T: Shorthand for Math.tan.
R: Function that generates rgba-strings, usage ex.: R(255, 255, 255, 0.5)
c: A 1920x1080 canvas.
x: A 2D context for that canvas.


R(255, 255, 255, 0.5)

rgba(255,255,255,0.5)

c: A 1920x1080 canvas.
x: A 2D context for that canvas.

s=c.width=200;c.height=100
k=()=>s=(8121*s+28411)%2e5
if(!c.S) {
  c.S=[]
  for(i = 0; i < 50;i+) {
    c.S.push(k())
  }
}
c.S.forEach(v=>{
  x.fillRect(v%200,v/200|0,1,1)
})




x.fillRect(0,0,s=c.width=200,c.height=s/2)
x.fillStyle=R(255,255,255)
k=()=>s=(8121*s+28411)%2e5

if(!c.S) {
  c.S=[];
  for(i = 0; i < 800;i++) {
    c.S.push(k())
  }
}
c.S.forEach((v,i)=>{
  x.fillRect(v%200,v/200|0,1,1)
  c.S[i]=(c.S[i]+k()%4+1)%2e5
})


