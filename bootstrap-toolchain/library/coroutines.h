// Native coroutine library; CO.5 production interface.
// Link BOOT_OBJ(BCPLCO) and BOOT_OBJ(COROUTIN), register exports.
// Bounded: root plus two live workers; SIZE=1024; known-live handles.
GLOBAL $(
  CO3INIT:289
  CREATECO:290
  DELETECO:291
  CALLCO:292
  COWAIT:293
  RESUMECO:294
  CO3CURR:295
  CO3ROOT:296
  CO3LIST:297
  CO2INIT:298
  CHANGECO:299
  CO3DROP:300
$)
