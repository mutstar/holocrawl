(function(root){
 const native=typeof module!=='undefined'&&module.exports,base=native?require('../city-market121/layout115.js'):root.MarketGen,infra=native?require('./infra122.js'):root.WallInfra122;
 function generate(...args){const m=base.generate(...args);m.marketInfra=infra.place(m);return m;}
 const api={...base,generate};root.MarketGen=api;if(native)module.exports=api;
})(globalThis);
