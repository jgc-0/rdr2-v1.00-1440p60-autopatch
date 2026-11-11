# 1440p add-on

Builds `rdr2_1440p60.elf` from the resident `autopatch60.elf` (the RDR2 1.00 build, not the one-shot in `src/`).

- `pe3.c`: the added `patch_entry`: writes render size 2560x1440 (block at VA 0x960ef2), turns the checkerboard flag off
  (0x961106), plus a few related code/global tweaks, then the original 60 fps patch.
- `l.ld`: linker script placing the code in the payload's free space.
- `ctx.bin`: tiny helper blob dropped into the payload.
- `mk.py`: patches the payload in place (addresses are fixed, so it only works with that exact build; it asserts as it goes).
- `build.sh`: compiles `pe3.c` and runs `mk.py`. Needs clang, ld.lld, llvm-objcopy, nm, readelf, python3.

Put `autopatch60.elf` in this folder and run `sh build.sh`. Output: `rdr2_1440p60.elf`.
