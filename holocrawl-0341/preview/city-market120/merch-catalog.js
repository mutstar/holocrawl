(function(root){
const rows=[
 ['acrylic-window','아크릴 진열장','wall','acrylic'],
 ['closed-shutter','닫힌 셔터','wall','closed'],
 ['half-shutter','반쯤 열린 셔터','wall','stock'],
 ['shirt-window','멤버색 티셔츠 진열창','wall','shirts'],
 ['poster-wall','공연 포스터 벽','wall','poster'],
 ['acrylic-rack','아크릴 스탠드 진열대','floor','acrylic'],
 ['shirt-stack','멤버색 티셔츠 더미','floor','shirts'],
 ['hoodie-rack','후드 상품 랙','floor','clothing'],
 ['plush-basket','봉제인형 바구니','floor','merch'],
 ['poster-rolls','포스터 묶음','floor','merch'],
 ['keychain-hooks','키링 걸이','floor','merch'],
 ['badge-trays','캔배지 진열판','floor','merch'],
 ['shopping-bags','굿즈 쇼핑백','floor','merch'],
 ['delivery-boxes','배송 상자 더미','floor','stock'],
 ['open-carton','개봉한 상품 상자','floor','stock'],
 ['delivery-cart','배송 카트','floor','stock'],
 ['folding-crates','접이식 물류 상자','floor','stock'],
 ['trash-bags','쓰레기봉투 더미','floor','trash'],
 ['paper-rubbish','포장지·종이 쓰레기','floor','trash'],
 ['recycling-bins','분리수거함','floor','trash']
];
root.MerchCatalog=rows.map(([id,name,kind,content])=>({id,name,kind,content,width:kind==='wall'?64:32,height:32,file:'../city-market02/assets/props/'+id+'.png'}));
if(typeof module!=='undefined'&&module.exports)module.exports=root.MerchCatalog;
})(typeof globalThis!=='undefined'?globalThis:this);
