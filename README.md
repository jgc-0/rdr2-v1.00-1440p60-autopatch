# RDR2 60fps autopatch + 1440p (fork)

Fork of [KurohaXR/rdr2-60fps-autopatch](https://github.com/KurohaXR/rdr2-60fps-autopatch), the in-memory 60 fps patcher for
Red Dead Redemption 2 on a jailbroken PS5. All credit for the original 60 fps patcher, its research and its write-up goes to
KurohaXR; this fork keeps their code, license and credits.

## What this fork adds

`rdr2_1440p60.elf`: a resident variant for RDR2 PS4 v1.00 (CUSA03041) that, on top of the 60 fps patch, renders at 1440p
(2560x1440) and re-applies itself on every game launch instead of once per payload run. The extra code is in [`1440p/`](1440p/);
see its README for what it writes and how to build it.

The original `src/` (the one-shot patcher) and the original build workflow are unchanged. The original README, with the
background, requirements for v1.32, disclaimer and test notes, is at the upstream link above.

## Use

1. Jailbroken PS5 with elfldr and ps5debug-NG running, same as upstream.
2. Load `rdr2_1440p60.elf` once per console boot (Payload Manager). It stays resident and patches each game launch.
3. Launch RDR2 v1.00. The message "RDR2 60fps + 1440p" appears once the patch lands.

This build targets game v1.00. Offsets are specific to it and the patch checks the original bytes before writing, so on a
different version it should write nothing and report an error.

## Credits

- Original 60 fps autopatch: KurohaXR.
- 1.32 Unlock FPS patch: Jao; patch repo illusionyy/PS-Game-Patch.
- ps5debug-NG (OpenSourcereR et al.); ps5-payload-sdk, elfldr, klogsrv, ftpsrv (John Törnblom / ps5-payload-dev).

## License

Same as upstream: the code is MIT. Building the original links against ps5-payload-sdk (GPL-3), so distribute the source
with any binaries.

## Disclaimer

Experimental software, no warranty of any kind, provided "as is". Use at your own risk; the author accepts no responsibility
for lost data, corrupted saves or bans.
