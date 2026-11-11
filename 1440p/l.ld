ENTRY(patch_entry)
SECTIONS {
  . = 0x4ec;
  .text : { *(.text) }
  . = 0x6b0;
  .tab : { *(.text.tab) }
  . = 0x836;
  .p60 : { *(.text.p60) }
  /DISCARD/ : { *(.comment) *(.note*) *(.eh_frame*) }
}
