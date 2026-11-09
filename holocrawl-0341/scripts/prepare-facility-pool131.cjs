const fs=require('fs'),path=require('path');
const R=path.resolve(__dirname,'..'),D=path.join(R,'preview/facility-pool131');fs.mkdirSync(D,{recursive:true});
const legacy=JSON.parse(fs.readFileSync(path.join(R,'preview/facility-exteriors124/manifest.json'),'utf8'));
const source='https://seesaawiki.jp/hololivetv/d/DREAMS',extra=[];
function add(group,rows){for(const[id,name,member,affiliation,concept]of rows)extra.push({id,name,member,affiliation,sourceArea:group,status:'planned',eligibleRegions:['JP','ID','EN'],source,concept,geometryStatus:'not-created',artStatus:'not-created',encountersStatus:'deferred'});}
add('harmony-garden',[
 ['promise','프로미스 타워','Promise','EN','시계탑의 중앙 기계실과 돌아가는 계단·연결 복도'],
 ['myth','포춘 네트워크','Myth','EN','네트워크 중계실과 다섯 멤버의 장치가 있는 연결 허브'],
 ['advent','The Cell 리턴즈','Advent','EN','감방·탈출 통로·중앙 보관실이 있는 수용 시설'],
 ['area15','루추추 모빌15','ID 1기생','ID','풍선 판매차와 열린 휴게 공간'],
 ['holoro','토코호로로','ID 2기생','ID','펜라이트 상점과 토스터 장치'],
 ['h3ro','h3ro 비클','ID 3기생','ID','차량 정비 공간과 탐험대 보급 상자']
]);
add('mega-sphere',[
 ['capsule-kong','캡슐 콩','카엘라','ID','대형 캡슐 머신과 캡슐 보관실'],
 ['robo-crane','로보로보 크레인','로보코','JP','크레인 게임기와 경품 창고'],
 ['onigiri-panic','오니기리 패닉','오카유','JP','주먹밥 테마 게임 부스와 경품대'],
 ['phoenix-dance','댄스 댄스 피닉스','키아라','EN','댄스 발판과 피닉스 장식이 있는 오락실'],
 ['korone-fighting','시바키아게 파이팅','코로네','JP','격투 게임기와 작은 대전 공간'],
 ['greed-cards','카드 오브 그리드','시오리','EN','카드 테이블과 책장·금고를 갖춘 카드룸'],
 ['raven-bar','레이븐 BAR','네리사','EN','바 카운터와 피아노·좌석의 술집'],
 ['haachama-lottery','로터리 차마차맥스','하쨔마','JP','복권 판매대와 추첨 장치'],
 ['moon-ace','문 에이스','무나','ID','달 장식 카드룸'],
 ['pekora-derby','페코람블 더비','페코라','JP','작은 타원형 경마장과 관람·발권 공간'],
 ['mega-coaster','메가코스터','공용','mixed','끊어진 롤러코스터 선로와 정비 통로'],
 ['mega-circuit','메가서킷','공용','mixed','장애물 코스와 우회 통로'],
 ['mega-photo','메가프리','공용','mixed','촬영 부스와 대기 공간'],
 ['pokajan','포카쟝','공용','mixed','중앙 게임 테이블과 관전 좌석'],
 ['mega-slot','메가슬롯','공용','mixed','슬롯 머신 열과 교환 카운터'],
 ['mega-exchange','메가스피어 코인 교환소','공용','mixed','교환 창구와 안쪽 보관실']
]);
add('soda-pop-lagoon',[
 ['fish-blue','피시 블루','아오','JP','물가 낚시 데크와 작은 관리소'],
 ['bae-tackle','베즈 비츠 앤드 봅스','벨즈','EN','낚시용품점과 미끼 진열·보관대'],
 ['ririka-lounge','이치조 VIP 라운지','리리카','JP','수상 라운지의 카운터와 좌석·교환 창구'],
 ['koyo-marine','코요라보 해양지부','코요리','JP','해양 실험 장비와 보트 정비 시설'],
 ['lagoon-stage','소다팝 라군 스테이지','공용','mixed','물에 둘러싸인 공연 무대와 연결 데크'],
 ['lamy-dome','라미즈 스노돔','라미','JP','스노돔 안 낚시터와 눈 장식'],
 ['splash-stadium','스플래시 스타디움','공용','mixed','작은 수상 경기장과 관전 데크'],
 ['marine-ship','프린세스 마린호','마린','JP','해적선 갑판·선실·선장실의 서로 다른 동선'],
 ['kobo-beacon','보코보코 비콘','코보','ID','비콘 장치와 물가 낚시터'],
 ['upao-heaven','우파오 헤븐','카나타','JP','라이브 굿즈점과 물총 진열대'],
 ['polka-camp','포포포 해피 캠프','폴카','JP','텐트·모닥불·캠핑 소품이 있는 야외 캠프']
]);
const built=legacy.maps.map(m=>({id:m.facility,name:m.name,member:m.name.split(' ')[0],affiliation:m.facility==='dev'?'DEV_IS':'JP',sourceArea:'harmony-garden',status:'built',eligibleRegions:['JP','ID','EN'],preview:'../facility-exteriors124/'+m.closed,openPreview:'../facility-exteriors124/'+m.open,originalMap:'../city-facilities106/'+m.map,origin:m.origin,geometryStatus:'existing-validated',artStatus:'existing-review-art',encountersStatus:'deferred'}));
const registry={revision:131,policyStatus:'user-approved-browser-planning',nativeIntegrated:false,scope:'기존 JP9종 + 메인 섬 EN/ID6종 + 메가스피어16종 + 소다팝 라군11종. 건물·놀이시설을 고정지형으로 재해석한다. 홀로홈·메모리 스탠드와 일반 소품은 별도.',policy:{regions:['JP','ID','EN'],regionRestriction:false,chancePerEligibleFloor:.5,maxPerFloor:1,uniquenessScope:'entire-campaign',selection:'uniform-without-replacement',persistDecision:true,rerollOnRevisit:false,exhaustion:'no-facility',placementFailure:'retry-layout-with-the-same-facility',eligibleFloors:{JP:'잔향도시1~14층',ID:'진입층·3개 분기의 일반층',EN:'진입층·6개 이계의 일반층'},specialFloors:'권역 보스·공통 최종 던전은 전용 지형을 유지한다.',encountersAndRewards:'match-host-floor; exact monsters/items/numbers deferred',loreAffiliation:'metadata-only; never an eligibility filter'},facilities:[...built,...extra],sources:[{url:source,checked:'2026-11-09',type:'unofficial-facility-list'},{url:'https://www.hololive-dreams.com/news/detail/ydwwnk5rrr1p',checked:'2026-11-09',type:'official-area-announcement'}],nextArtFacility:'promise'};
registry.guaranteedFacilities=[{id:'holohome',name:'홀로홈',status:'browser-prototype-user-review',region:'JP',floorId:'JP-main-1',floor:1,chance:1,count:1,footprint:[13,11],preview:'../holohome136/',art:'../holohome136/home136.png',randomPoolMember:false,artRevision:136,downstairs:{count:1,alwaysInside:true,localCell:[6,2],nativeSize:[32,32],sprite:'../holohome133/assets/stairs-native.png',destination:'JP-main-2',reciprocal:true},placement:'seeded-location-near-start; entrance and staircase connected',nativeIntegrated:false}];
registry.policy.maxPerFloorAppliesTo='random-facilities-only; guaranteed HoloHome is separate';
fs.writeFileSync(path.join(D,'registry.json'),JSON.stringify(registry,null,2)+'\n');
const f=path.join(R,'design/dungeon-route01.json'),route=JSON.parse(fs.readFileSync(f,'utf8'));
route.sharedFacilities={status:'approved-policy-browser-planning',registry:'preview/facility-pool131/registry.json',planner:'preview/facility-pool131/planner131.js',preview:'preview/facility-pool131/',...registry.policy,built:built.length,planned:extra.length,nativeIntegrated:false};
route.jp.main.guaranteedFacilities=registry.guaranteedFacilities;
route.jp.main.facilityPlacement.campaignPolicy='sharedFacilities';route.jp.main.facilityPlacement.nativePolicyStatus='legacy-native107-JP-only; shared regional pool not yet ported';
route.currentArtTask='홀로홈136: 사용자는 기존 아치 입구를 선호한다고 명확히 정정. 기존96x48 입구 도트 그대로 유지, 외벽 면·몰딩만 같은 상아색으로 맞춤. TV 코너96x96→64x64 재제작. 낮은 평문 입구 초안은 미사용.13x11/1층확정/계단왕복·저장,48지도·입구 원본 동일 검사 통과. 사용자 검토 대기·엔진 미적용.';
fs.writeFileSync(f,JSON.stringify(route,null,2)+'\n');console.log(JSON.stringify({built:built.length,planned:extra.length,total:registry.facilities.length}));
