# -*- coding: utf-8 -*-
r"""배포 묶음 (2026-11-14) — 소울칼리버 IV (PS3 아시아판 BLUS30160) 한글 패치
  dist/SoulCalibur4_PS3_KR_<버전>/ = patch\<경로 _ 이름>.xdelta + xdelta.exe + readme.txt + 한글패치_적용.bat + 되돌리기.bat (+ zip)
  xdelta 원본 = work/orig(text·tectext·font — 프로젝트 시작 때 뜬 원본 사본), 새것 = work/build/USRDIR (게임 폴더는 안 믿음 — 시험판이 깔려 있을 수 있음).
  만들고 나서 «원본에 적용 → 새것과 바이트 동일» 전수 되짚기. EBOOT 무수정(데이터 파일만).
  규칙: MD5 대문자 · 한국어 문서·bat CP949(CRLF) · 버전 v0.9 꼴 · bat 의 if 블록 안 echo 에 괄호 금지.
  (틀은 mystara-kr-patch/tools/make_dist.py 를 옮김)
  python tools/make_dist.py"""
import hashlib, os, shutil, subprocess, sys, zipfile
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
R = lambda *p: os.path.join(ROOT, *p)
VER = 'v0.9'
XDELTA = r'C:\claude\utils\xdelta.exe'
TID = 'BLUS30160'
NEW = R('work', 'build', 'USRDIR')
PROBE = r'cdata\text\regtext_u.dtp'          # 게임 폴더 찾기용(USRDIR 아래)


def orig_of(rel):
    """rel = USRDIR 아래 경로(cdata/text/… · cpudata/tectext/… · cdata/texture/…)"""
    d, f = rel.split('/')[-2], rel.split('/')[-1]
    p = R('work', 'orig', 'font' if d == 'texture' else d, f)
    if not os.path.isfile(p):
        raise SystemExit('원본 없음 ' + rel)
    return p


def md5(p):
    h = hashlib.md5()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 22), b''): h.update(b)
    return h.hexdigest().upper()


pname = lambda rel: rel.replace('/', '_')

README = """소울칼리버 IV (SOULCALIBUR IV, PS3) 한글 패치 {ver}
================================================================

아시아판 디스크 (BLUS30160) 용입니다. RPCS3 에서 확인했습니다.
게임 실행 파일(EBOOT)은 건드리지 않고 글·글꼴 데이터 파일만 바꿉니다.
(폴더로 풀어 둔 게임에 적용합니다. 디스크 원본 그대로는 바꿀 수 없습니다)

바꾸는 파일 : {n}개


[ 적용 방법 ]

0. ★원본 게임 파일에 적용합니다.
1. 이 묶음을 아무 폴더에나 풉니다.
2. 「한글패치_적용.bat」 을 실행하고, 게임 폴더를 끌어다 놓거나 경로를 적고 Enter.
   (게임 최상위 폴더, PS3_GAME, USRDIR 어느 것을 줘도 찾아갑니다)
3. 배치가 파일마다
     원본 MD5 확인 → 원본을 이 묶음의 「원본백업」 폴더에 복사 → 패치 → 결과 MD5 확인
   을 하고 덮어씁니다. 이미 한글판인 파일은 건너뜁니다.
4. 게임 언어는 PS3 시스템 언어를 따릅니다. RPCS3 의 시스템 언어를 「한국어」 나 「영어」 로 두세요.
   (이 게임은 한국어·영어 모두 영어 자리 글을 읽고, 그 자리에 한글이 들어갑니다. 일본어로 두면 일본어가 나옵니다)
5. 패치 전에 만든 스테이트(상태 저장)는 쓰지 마세요. 새로 부팅해서 확인하세요.

되돌리기 : 「되돌리기.bat」 → 같은 폴더를 주면 「원본백업」 의 파일로 되돌립니다.
          (「원본백업」 폴더를 지우지 마세요)


[ 바뀌는 것 ]

■ 메뉴·옵션 설명, 시스템 메시지(저장·로드 안내는 PS3 시스템 창도 한글)
■ 스토리·아케이드 대사와 자막, 승리·도발 대사, 데모 자막
■ 캐릭터 크리에이션(파츠·스킬·스타일 설명), 타워 오브 로스트 소울즈
■ 뮤지엄(캐릭터 프로필·일러스트 설명·칭호), 트레이닝, 튜토리얼
■ 모든 캐릭터의 기술표(기술 이름·읽는 법·커맨드 설명)
■ 고해상도 한글 글꼴

[ 알려진 사항 ]

■ 메뉴 큰 제목(STORY·ARCADE 등 장식 글꼴)은 원문 그대로입니다.
■ 일본판에도 영문으로 나오는 곡명·저작권 표기 등은 영문 그대로입니다.


[ 원본 → 한글판 MD5 ]

{table}
"""

BAT = r"""@echo off
setlocal
chcp 949 >nul
cd /d "%~dp0"
set "XD=%~dp0xdelta.exe"
set "BK=%~dp0원본백업"

echo.
echo  ================================================================
echo    SOULCALIBUR IV PS3 Korean Patch {ver}   [{tid}]
echo  ================================================================
echo.

if not exist "%XD%" goto NOXD

set "TARGET=%~1"
if not defined TARGET set /p TARGET=  게임 폴더를 끌어다 놓거나 경로를 적고 Enter:
set "TARGET=%TARGET:"=%"
if "%TARGET:~-1%"=="\" set "TARGET=%TARGET:~0,-1%"

set "DEST="
if exist "%TARGET%\{probe}" set "DEST=%TARGET%"
if exist "%TARGET%\USRDIR\{probe}" set "DEST=%TARGET%\USRDIR"
if exist "%TARGET%\PS3_GAME\USRDIR\{probe}" set "DEST=%TARGET%\PS3_GAME\USRDIR"
if not defined DEST goto NODEST
echo  대상 : "%DEST%"
echo.
if not exist "%BK%" mkdir "%BK%"
set /a DONE=0
set /a SKIP=0
{calls}
echo.
echo  [OK] 끝났습니다. 새로 패치 %DONE%개 · 이미 한글판 %SKIP%개
echo       원본은 "원본백업" 폴더에 있습니다.
echo.
echo  ★ RPCS3 시스템 언어를 한국어나 영어로 두세요. 일본어면 일본어가 나옵니다.
goto END

:DO
set "NAME=%~1"
set "PN=%~2"
set "SRCMD5=%~3"
set "DSTMD5=%~4"
set "XP=patch\%PN%.xdelta"
if not exist "%DEST%\%NAME%" goto MISSING
call :HASH "%DEST%\%NAME%"
if /I "%H%"=="%DSTMD5%" set /a SKIP+=1
if /I "%H%"=="%DSTMD5%" exit /b 0
if /I not "%H%"=="%SRCMD5%" goto WRONG
copy /y "%DEST%\%NAME%" "%BK%\%PN%" >nul
"%XD%" -d -f -s "%DEST%\%NAME%" "%XP%" "%BK%\%PN%.new"
if errorlevel 1 goto XFAIL
call :HASH "%BK%\%PN%.new"
if /I not "%H%"=="%DSTMD5%" goto XFAIL
move /y "%BK%\%PN%.new" "%DEST%\%NAME%" >nul
set /a DONE+=1
echo      %NAME%
exit /b 0

:HASH
set "H="
for /f "skip=1 tokens=* delims=" %%A in ('certutil -hashfile "%~1" MD5') do if not defined H set "H=%%A"
set "H=%H: =%"
exit /b 0

:MISSING
echo  [!] %NAME% 이 대상 폴더에 없습니다. 판이 맞는지 확인하세요 - 이 묶음은 {tid} 용입니다.
goto FAIL
:WRONG
echo  [!] %NAME% 이 원본과 다릅니다. 다른 판이거나 이미 다른 패치가 들어가 있습니다.
echo      이 묶음은 {tid} 용입니다. 원본 MD5 %SRCMD5%
goto FAIL
:XFAIL
echo  [!] %NAME% 패치에 실패했습니다. 원본은 원본백업 폴더에 있습니다.
if exist "%BK%\%PN%.new" del "%BK%\%PN%.new"
goto FAIL
:NOXD
echo  [!] xdelta.exe 가 이 폴더에 없습니다. 묶음을 통째로 푸세요.
goto FAIL
:NODEST
echo  [!] 게임 폴더를 찾지 못했습니다. PS3_GAME 이 있는 폴더를 주세요.
goto FAIL
:FAIL
echo.
pause
exit /b 1
:END
echo.
pause
exit /b 0
"""
UNDO = r"""@echo off
setlocal
chcp 949 >nul
cd /d "%~dp0"
set "BK=%~dp0원본백업"
set "TARGET=%~1"
if not defined TARGET set /p TARGET=  게임 폴더를 끌어다 놓거나 경로를 적고 Enter:
set "TARGET=%TARGET:"=%"
if "%TARGET:~-1%"=="\" set "TARGET=%TARGET:~0,-1%"
set "DEST="
if exist "%TARGET%\{probe}" set "DEST=%TARGET%"
if exist "%TARGET%\USRDIR\{probe}" set "DEST=%TARGET%\USRDIR"
if exist "%TARGET%\PS3_GAME\USRDIR\{probe}" set "DEST=%TARGET%\PS3_GAME\USRDIR"
if not defined DEST goto NODEST
{calls}
echo.
echo  [OK] 원본으로 되돌렸습니다.
goto END
:NODEST
echo  [!] 게임 폴더를 찾지 못했습니다.
:END
echo.
pause
"""


def cp949(path, text):
    open(path, 'w', encoding='cp949', newline='\r\n').write(text)


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    name = 'SoulCalibur4_PS3_KR_' + VER
    od = R('dist', name)
    if os.path.exists(od): shutil.rmtree(od)
    os.makedirs(os.path.join(od, 'patch'))
    shutil.copy(XDELTA, os.path.join(od, 'xdelta.exe'))
    files = sorted(os.path.relpath(os.path.join(r, f), NEW).replace(os.sep, '/') for r, ds, fs in os.walk(NEW) for f in fs)
    rows = []; calls = []; undo = []
    for rel in files:
        src = orig_of(rel); dst = os.path.join(NEW, *rel.split('/')); pn = pname(rel)
        a, b = md5(src), md5(dst)
        assert a != b, ('바뀐 것 없음', rel)
        xd = os.path.join(od, 'patch', pn + '.xdelta')
        subprocess.run([XDELTA, '-e', '-9', '-f', '-s', src, dst, xd], check=True)
        tmp = xd + '.chk'
        subprocess.run([XDELTA, '-d', '-f', '-s', src, xd, tmp], check=True)
        assert md5(tmp) == b, ('되짚기 실패', rel); os.remove(tmp)
        win = rel.replace('/', '\\')
        rows.append('%s\n    %s -> %s' % (win, a, b))
        calls.append('call :DO "%s" "%s" %s %s\nif errorlevel 1 goto FAIL' % (win, pn, a, b))
        undo.append('if exist "%%BK%%\\%s" copy /y "%%BK%%\\%s" "%%DEST%%\\%s" >nul' % (pn, pn, win))
    cp949(os.path.join(od, 'readme.txt'), README.format(ver=VER, n=len(files), table='\n'.join(rows)))
    cp949(os.path.join(od, '한글패치_적용.bat'), BAT.replace('{ver}', VER).replace('{tid}', TID).replace('{probe}', PROBE).replace('{calls}', '\n'.join(calls)))
    cp949(os.path.join(od, '되돌리기.bat'), UNDO.replace('{probe}', PROBE).replace('{calls}', '\n'.join(undo)))
    zp = od + '.zip'
    with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for root, ds, fs in os.walk(od):
            for f in fs:
                p = os.path.join(root, f); z.write(p, os.path.join(name, os.path.relpath(p, od)))
    print('파일 %d개 · 되짚기 전부 일치 · %s' % (len(files), od))
    print('zip %s  %d B  md5 %s' % (zp, os.path.getsize(zp), md5(zp)))


if __name__ == '__main__':
    main()
