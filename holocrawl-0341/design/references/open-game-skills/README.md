# Open Game Skills 참고 자료

홀로죽의 시설 배치, 턴제 연출, 플레이 검증에 참고할 외부 지침 5개를 보관한다. 원본은 jammyfu / PaintingCoder의 Open Game Skills이며 아래 커밋을 기준으로 검토했다. [원본 저장소](https://github.com/jammyfu/open-game-skills/tree/cdd133e8fd71b45fb519c49cd3532b1bed3ec83c) · [MIT 라이선스](LICENSE)

| 문서 | 홀로죽에서 참고할 때 | 고정된 원본 |
| --- | --- | --- |
| [level-design](level-design.md) | 시설 맵의 통로 폭, 출입구, 주요 이동 경로를 도트 작업 전에 검토 | [원본](https://github.com/jammyfu/open-game-skills/blob/cdd133e8fd71b45fb519c49cd3532b1bed3ec83c/skills/disciplines/level-design/SKILL.md) |
| [roguelike-run](roguelike-run.md) | 시드와 룰 버전을 기록하고, 한 판의 상태와 다음 판에 남길 상태를 정의 | [원본](https://github.com/jammyfu/open-game-skills/blob/cdd133e8fd71b45fb519c49cd3532b1bed3ec83c/skills/disciplines/roguelike-run/SKILL.md) |
| [juice-vfx](juice-vfx.md) | 엔진이 판정한 이벤트에 연출을 연결하고, 효과를 켜고 꺼도 판정이 같은지 검사 | [원본](https://github.com/jammyfu/open-game-skills/blob/cdd133e8fd71b45fb519c49cd3532b1bed3ec83c/skills/disciplines/juice-vfx/SKILL.md) |
| [gameplay-validation](gameplay-validation.md) | 자동 조우 결과, 특정 상황 테스트, 실제 플레이 결과 각각의 검증 범위를 기록 | [원본](https://github.com/jammyfu/open-game-skills/blob/cdd133e8fd71b45fb519c49cd3532b1bed3ec83c/skills/disciplines/gameplay-validation/SKILL.md) |
| [asset-pack-intake](asset-pack-intake.md) | 외부 타일셋과 스프라이트 묶음을 가져올 때 파일·크기·아틀라스·해시를 확인 | [원본](https://github.com/jammyfu/open-game-skills/blob/cdd133e8fd71b45fb519c49cd3532b1bed3ec83c/skills/assets/asset-pack-intake/SKILL.md) |

## 검토 범위

- 문서 본문 전체와 라이선스를 확인했다. 포함된 파일은 Markdown 문서와 라이선스다. 원문 지침은 참고 자료로 읽으며, 본문 중 원본 저장소의 상대 링크는 같은 커밋을 가리키는 링크로 바꿨다.
- 원본 설치 스크립트는 소스만 확인했다. 지정한 스킬 경로에 전체 묶음을 복사하거나 심볼릭 링크로 연결하는 방식이다. 이번 보관본은 설치 스크립트·실행 코드·워크플로를 포함하지 않으며 `SKILL.md` 대신 설명용 파일명으로 저장했다. [설치 스크립트 원본](https://github.com/jammyfu/open-game-skills/blob/cdd133e8fd71b45fb519c49cd3532b1bed3ec83c/tools/install.py)
- `asset-pack-intake`에 나오는 검증 스크립트도 참고 링크로만 남겼다. 실행 검사와 전체 묶음에 대한 보안 검토는 별도 범위다. [에셋 검증 스크립트 원본](https://github.com/jammyfu/open-game-skills/blob/cdd133e8fd71b45fb519c49cd3532b1bed3ec83c/skills/assets/asset-pack-intake/scripts/validate_pack.py)
