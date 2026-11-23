# 오픈소스 게임 개발 도구 참고 목록

홀로돌죽은 칸 단위로 이동하는 2D 턴제 게임이다. 아래는 도구별 용도와 이 프로젝트에서 검토할 지점을 정리한 목록이다.

| 도구 | 용도 | 홀로돌죽에서의 검토 |
| --- | --- | --- |
| [Jolt Physics](https://github.com/jrouwe/JoltPhysics) | 강체 물리, 충돌 감지 | 칸 단위 이동과 충돌에는 현재 규칙으로 충분하다. |
| [Terrain3D](https://github.com/TokisanGames/Terrain3D) | Godot 4용 3D 지형 편집 | 3D 지형이 필요한 별도 작업용. |
| [Material Maker](https://github.com/RodZill4/material-maker) | 절차적 텍스처 제작, 3D 모델 페인팅 | 우선 비교 후보. 낡은 콘크리트와 닳은 금속의 반복 텍스처를 제작해 기존 도트에 맞춘다. |
| [Effekseer](https://github.com/effekseer/Effekseer) | 파티클 이펙트 편집과 재생 | 혜성 꼬리, 잔광 등 권능 연출 후보. 게임 안에서 재생하려면 런타임 연동을 검토한다. |
| [Voxel Tools](https://github.com/Zylann/godot_voxel) | Godot용 편집 가능한 복셀 지형 | 3D 복셀 지형이 필요한 별도 작업용. |
| [Recast Navigation](https://github.com/recastnavigation/recastnavigation) | 내비게이션 메시 생성, 경로 탐색, 군중 이동 | 현재 맵은 타일의 통행 여부를 기준으로 경로를 확인한다. |
| [ozz-animation](https://github.com/guillaumeblanc/ozz-animation) | 골격 애니메이션 재생과 블렌딩 | 골격을 가진 모델을 쓸 때 검토한다. |
| [The Forge](https://github.com/ConfettiFX/The-Forge) | 멀티플랫폼 그래픽 개발 프레임워크 | 렌더링 기반을 새로 검토할 때 참고한다. |
| [meshoptimizer](https://github.com/zeux/meshoptimizer) | 3D 메시의 용량과 렌더링 최적화 | 3D 모델을 쓸 때 검토한다. |
| [FastNoise2](https://github.com/Auburn/FastNoise2) | 절차적 노이즈 생성 | 같은 시드에서 얼룩·균열이 군데군데 모이는 장식 분포 후보. 방 배치와 통행 판정은 기존 맵 규칙으로 다룬다. |

회사에서 먼저 볼 후보는 Material Maker다. 다음 맵의 초안에서 동선을 걸어 본 뒤, 잔향도시 기존 바닥과 같은 크기·팔레트로 낡은 콘크리트 변형 한 장을 만들어 같은 맵에서 비교한다. 벽·바닥 구분, 같은 타일을 반복했을 때 이음새, 소품 가시성을 확인한다.

현재 상태는 도구 조사 메모다. 도구 채택은 비교 후 결정한다. 맵 설계와 플레이 검증 방법은 [Open Game Skills 참고 문서](open-game-skills/README.md)에 있다.
