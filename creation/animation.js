(() => {
  'use strict';
  const canvas=document.getElementById('hands'),story=document.getElementById('story');
  const gl=canvas.getContext('webgl',{alpha:true,antialias:true,premultipliedAlpha:false});
  const ctx=gl?null:canvas.getContext('2d');
  const reduced=matchMedia('(prefers-reduced-motion: reduce)');
  const image=new Image(),W=1536,H=1024;
  const clamp=v=>Math.max(0,Math.min(1,v));
  const smooth=(a,b,v)=>{const t=clamp((v-a)/(b-a));return t*t*(3-2*t);};
  let particles=[],buffer,data,pose=0,target=0,frame=0,ready=false;
  let view={w:1,h:1,scale:1,left:0,top:0,dpr:1};
  let seed=917;
  function random(){seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;}
  function rotate(x,y,cx,cy,a){const dx=x-cx,dy=y-cy,c=Math.cos(a),s=Math.sin(a);return[cx+dx*c-dy*s,cy+dx*s+dy*c];}

  // Each scroll pose articulates both hands. The initial composition leaves
  // the hands visible at either edge, with fingertips roughly a third apart.
  function fingerJoints(x,y,px,py,fingers,amount,indexWeight){
    for(const f of fingers){
      const distance=((x-f.x)**2+(y-f.y-f.length*.55)**2)/(2*f.radius*f.radius);
      const weight=Math.exp(-distance)*smooth(f.y-8,f.y+25,y)*(1-indexWeight);
      const distal=smooth(f.y+f.length*.45,f.y+f.length*.75,y);
      let q=rotate(px,py,f.x,f.y+f.length*.5,f.angle*amount*.6*distal);
      q=rotate(q[0],q[1],f.x,f.y,f.angle*amount);
      px+=(q[0]-px)*weight;py+=(q[1]-py)*weight;
    }
    return[px,py];
  }
  function deform(x,y,p){
    const rest=1-p,travel=smooth(0,1,p),flex=Math.sin(Math.PI*p);
    const opening=smooth(.12,.88,p),curl=1-opening;
    if(x<770){
      const index=smooth(555,605,x)*(1-smooth(501,525,y));
      let q=rotate(x,y,653,477,(.045*rest+.12*flex)*smooth(645,680,x));
      q=rotate(q[0],q[1],560,460,.04*rest+.08*flex);
      let px=x+(q[0]-x)*index,py=y+(q[1]-y)*index;
      [px,py]=fingerJoints(x,y,px,py,[
        {x:618,y:515,length:95,radius:31,angle:.16},
        {x:578,y:538,length:93,radius:24,angle:.18},
        {x:555,y:568,length:61,radius:20,angle:.12},
        {x:510,y:498,length:73,radius:38,angle:-.1}
      ],.55*curl+.6*flex,index);
      q=rotate(px,py,350,455,(.015*rest-.04*flex)*smooth(270,430,x));
      return[q[0]-236*(1-travel)+16.5*travel*smooth(0,350,x),q[1]-1.5*travel];
    }
    const index=(1-smooth(965,1015,x))*(1-smooth(504,530,y));
    let q=rotate(x,y,900,478,-(.035*rest+.10*flex)*(1-smooth(878,923,x)));
    q=rotate(q[0],q[1],987,470,-(.035*rest+.075*flex));
    let px=x+(q[0]-x)*index,py=y+(q[1]-y)*index;
    [px,py]=fingerJoints(x,y,px,py,[
      {x:958,y:530,length:112,radius:30,angle:-.17},
      {x:1014,y:555,length:90,radius:26,angle:-.2},
      {x:1040,y:562,length:72,radius:22,angle:-.14},
      {x:1072,y:523,length:69,radius:34,angle:.11}
    ],.5*curl+.7*flex,index);
    const wrist=rotate(px,py,1210,470,(-.012*rest+.035*flex)*(1-smooth(1170,1340,x)));
    return[wrist[0]+236*(1-travel)-16.5*travel*(1-smooth(1190,1536,x)),wrist[1]+1.5*travel];
  }
  function shader(type,source){const s=gl.createShader(type);gl.shaderSource(s,source);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(s));return s;}
  function setup(){
    // Sample the anatomy once, then render actual separated dots, with no
    // sketch lines or image texture in the displayed scene. Stable sampling
    // prevents the dots flickering as their joints move in either direction.
    const sampler=document.createElement('canvas');sampler.width=W;sampler.height=H;
    const sample=sampler.getContext('2d',{willReadFrequently:true});sample.drawImage(image,0,0);
    const pixels=sample.getImageData(0,0,W,H).data;
    for(let y=330;y<710;y+=4.2)for(let x=0;x<W;x+=4.2){
      const sx=Math.max(0,Math.min(W-1,Math.round(x+(random()-.5)*2.8)));
      const sy=Math.round(y+(random()-.5)*2.8),i=(sy*W+sx)*4;
      const alpha=pixels[i+3]/255;if(alpha<.78)continue;
      const dark=1-(pixels[i]+pixels[i+1]+pixels[i+2])/(3*255);
      if(random()>.26+.74*Math.pow(dark,.7))continue;
      particles.push({x:sx,y:sy,r:.78+dark*.88,alpha:.38+dark*.55});
    }
    data=new Float32Array(particles.length*4);
    if(gl){
      const program=gl.createProgram();
      gl.attachShader(program,shader(gl.VERTEX_SHADER,'attribute vec4 dot;varying float opacity;void main(){gl_Position=vec4(dot.xy,0.,1.);gl_PointSize=dot.z;opacity=dot.w;}'));
      gl.attachShader(program,shader(gl.FRAGMENT_SHADER,'precision mediump float;varying float opacity;void main(){float d=length(gl_PointCoord-vec2(.5));float a=(1.-smoothstep(.36,.5,d))*opacity;gl_FragColor=vec4(.19,.21,.19,a);}'));
      gl.linkProgram(program);if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw Error(gl.getProgramInfoLog(program));gl.useProgram(program);
      buffer=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,buffer);gl.bufferData(gl.ARRAY_BUFFER,data,gl.DYNAMIC_DRAW);
      const a=gl.getAttribLocation(program,'dot');gl.enableVertexAttribArray(a);gl.vertexAttribPointer(a,4,gl.FLOAT,false,0,0);
      gl.enable(gl.BLEND);gl.blendFuncSeparate(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA,gl.ONE,gl.ONE_MINUS_SRC_ALPHA);gl.clearColor(0,0,0,0);
    }
    canvas.dataset.dots=particles.length;ready=true;resize();
  }
  function resize(){
    const w=canvas.clientWidth,h=canvas.clientHeight,dpr=Math.min(devicePixelRatio||1,2);
    canvas.width=Math.round(w*dpr);canvas.height=Math.round(h*dpr);
    // One desktop composition, spanning the window. No mobile-specific layout.
    view={w,h,dpr,scale:w/W,left:0,top:h*.5-487/W*w};
    if(gl)gl.viewport(0,0,canvas.width,canvas.height);else ctx.setTransform(dpr,0,0,dpr,0,0);
    readScroll();
  }
  function draw(){
    frame=0;if(!ready)return;
    pose=reduced.matches?target:pose+(target-pose)*.2;if(Math.abs(target-pose)<.0001)pose=target;
    if(ctx)ctx.clearRect(0,0,view.w,view.h);
    for(let i=0;i<particles.length;i++){
      const dot=particles[i],q=deform(dot.x,dot.y,pose),x=q[0]*view.scale,y=view.top+q[1]*view.scale,r=dot.r*view.scale;
      if(gl){data[i*4]=x/view.w*2-1;data[i*4+1]=1-y/view.h*2;data[i*4+2]=Math.max(1.2,r*2*view.dpr);data[i*4+3]=dot.alpha;}
      else{ctx.fillStyle=`rgba(48,54,48,${dot.alpha})`;ctx.beginPath();ctx.arc(x,y,Math.max(.35,r),0,Math.PI*2);ctx.fill();}
    }
    if(gl){gl.clear(gl.COLOR_BUFFER_BIT);gl.bindBuffer(gl.ARRAY_BUFFER,buffer);gl.bufferSubData(gl.ARRAY_BUFFER,0,data);gl.drawArrays(gl.POINTS,0,particles.length);}
    canvas.dataset.pose=pose.toFixed(4);if(pose!==target)requestDraw();
  }
  function requestDraw(){if(!frame)frame=requestAnimationFrame(draw);}
  function readScroll(){target=clamp(-story.getBoundingClientRect().top/Math.max(1,story.offsetHeight-innerHeight)/.98);requestDraw();}
  addEventListener('scroll',readScroll,{passive:true});addEventListener('resize',resize);reduced.addEventListener('change',requestDraw);
  image.onload=setup;image.src='assets/human-machine.png';
})();
