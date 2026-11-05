(function(root){
'use strict';
const patches=[[270,150,32,32],[285,153,32,32],[160,300,32,32],[260,300,32,32]];
function index(seed,mix,x,y){
 let h=2166136261;
 for(const c of String(seed)+':floor:'+mix)h=Math.imul(h^c.charCodeAt(0),16777619);
 h=Math.imul(h^x,0x85ebca6b);h=Math.imul(h^y,0xc2b2ae35);h^=h>>>16;
 h=Math.imul(h,0x7feb352d);h^=h>>>15;h=Math.imul(h,0x846ca68b);h^=h>>>16;
 return(h>>>0)%16;
}
function variants(source){
 const result=[];
 for(let base=0;base<4;base++)for(let rotation=0;rotation<4;rotation++){
   const canvas=document.createElement('canvas');canvas.width=canvas.height=32;
   const ctx=canvas.getContext('2d');ctx.imageSmoothingEnabled=false;
   ctx.translate(16,16);ctx.rotate(rotation*Math.PI/2);
   ctx.drawImage(source,...patches[base],-16,-16,32,32);result.push(canvas);
 }
 return result;
}
function showSwatches(tiles,container){
 container.replaceChildren();tiles.forEach((tile,i)=>{const figure=document.createElement('figure'),copy=document.createElement('canvas'),caption=document.createElement('figcaption');copy.width=copy.height=32;copy.getContext('2d').drawImage(tile,0,0);caption.textContent=String.fromCharCode(65+Math.floor(i/4))+' '+(i%4*90)+'°';figure.append(copy,caption);container.append(figure);});
}
const api={index,variants,showSwatches};root.RandomFloor=api;
if(typeof module!=='undefined'&&module.exports)module.exports=api;
})(typeof globalThis!=='undefined'?globalThis:this);
