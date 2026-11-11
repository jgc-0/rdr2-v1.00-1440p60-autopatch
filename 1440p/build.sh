#!/bin/sh
# Builds rdr2_1440p60.elf. Needs clang, ld.lld, llvm-objcopy, nm, readelf and python3.
# Put the resident autopatch60.elf (RDR2 1.00 build) in this folder first, then run: sh build.sh
set -e
clang -target x86_64-unknown-freebsd -Oz -fPIE -fno-plt -fno-stack-protector -ffreestanding -fno-builtin -mno-red-zone \
  -fno-asynchronous-unwind-tables -fno-unwind-tables -fomit-frame-pointer -DWITH60 -c pe3.c -o pe1.o
ld.lld -T l.ld --defsym=cmd=0x91b --defsym=expect_success=0x9db --defsym=proc_read=0xa33 --defsym=tlog=0x8bf \
  --defsym=g_sock=0x14000 --defsym=p_send=0xdb58 --defsym=p_snprintf=0xdb50 --defsym=p_usleep=0xdb48 pe1.o -o pe1.elf
python3 mk.py "${1:-autopatch60.elf}"
