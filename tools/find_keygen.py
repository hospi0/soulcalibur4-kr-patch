# -*- coding: utf-8 -*-
"""EBOOT.elf 에서 «(x>>1)*5+1» 꼴 코드를 찾는다.
python tools/find_keygen.py            -> 후보 목록
python tools/find_keygen.py dis <VA hex> [명령 수]   -> 디스어셈블
"""
import os, sys, struct
import capstone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ELF = os.path.join(ROOT, 'work', 'bin', 'upd', 'EBOOT.elf')
CODE_END = 0xA70000   # 세그0 파일 범위(세그1 은 파일 0xA70000 = VA 0xA80000)


def va2off(va):
    return va - 0x10000 if va < 0xA80000 else va - 0xA80000 + 0xA70000


def dis(b, va, n):
    md = capstone.Cs(capstone.CS_ARCH_PPC, capstone.CS_MODE_64 | capstone.CS_MODE_BIG_ENDIAN)
    off = va2off(va)
    for i in range(n):
        w = b[off + i * 4:off + i * 4 + 4]
        ins = list(md.disasm(w, va + i * 4))
        if ins:
            print('%08X  %s  %s %s' % (va + i * 4, w.hex(), ins[0].mnemonic, ins[0].op_str))
        else:
            print('%08X  %s  ??' % (va + i * 4, w.hex()))


def main():
    b = open(ELF, 'rb').read()
    if len(sys.argv) > 1 and sys.argv[1] == 'dis':
        dis(b, int(sys.argv[2], 16), int(sys.argv[3], 0) if len(sys.argv) > 3 else 40)
        return
    ws = struct.unpack('>%dI' % (CODE_END // 4), b[:CODE_END])
    def is_srwi1(w):   # rlwinm rA,rS,31,1,31
        return (w >> 26) == 21 and ((w >> 11) & 31) == 31 and ((w >> 6) & 31) == 1 and ((w >> 1) & 31) == 31
    def is_srdi1(w):   # rldicl rA,rS,63,1
        return (w >> 26) == 30 and ((w >> 2) & 7) == 0 and ((w >> 11) & 31) == 31 and ((w >> 1) & 1) == 1 and ((w >> 5) & 63) == 1
    def is_mul5(w):
        return (w >> 26) == 7 and (w & 0xFFFF) == 5
    def is_slwi2(w):   # rlwinm SH=2,MB=0,ME=29
        return (w >> 26) == 21 and ((w >> 11) & 31) == 2 and ((w >> 6) & 31) == 0 and ((w >> 1) & 31) == 29
    def is_addi1(w):
        return (w >> 26) == 14 and (w & 0xFFFF) == 1 and ((w >> 16) & 31) != 0
    hits = []
    for i, w in enumerate(ws):
        if is_srwi1(w) or is_srdi1(w):
            win = ws[i + 1:i + 8]
            if any(is_mul5(x) or is_slwi2(x) for x in win) and any(is_addi1(x) for x in win):
                hits.append(i * 4 + 0x10000)
    print('후보', len(hits))
    for va in hits[:60]:
        print('---')
        dis(b, va - 8, 12)


if __name__ == '__main__':
    main()
