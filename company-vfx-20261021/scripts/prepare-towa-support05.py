from pathlib import Path
root=Path(__file__).resolve().parents[1]
s=(root/'scripts/prepare-towa-support04.py').read_text(encoding='utf-8')
s=s.replace('towa-support04','towa-support05').replace('towa-support03','towa-support04').replace('exec-874d51f5-80e3-4493-9a28-fb2674c65563.png','exec-bf494970-7949-4bcf-abf8-a8d18eb319e1.png').replace('(20,8)','(24,12)')
# Publisher inherits the latest saved script, which already describes purple arrows.
s=s.replace(".replace('은빛 탄두·짧은 자주색 궤적','짧은 보라색 악마 화살')",".replace('짧은 보라색 악마 화살','크고 두꺼운 연보라색 악마 화살')").replace(".replace('은빛탄두+짧은자주색궤적','짧은보라색악마화살')",".replace('짧은보라색악마화살','크고두꺼운연보라색악마화살')")
exec(compile(s,str(__file__),'exec'))
