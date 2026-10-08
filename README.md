# BEXE v3

BEXE is a package format for Windows executables plus a browser-oriented launcher.

## Important architecture

Chrome cannot directly execute a new `.bexe` file type as machine code. Chrome executes web content/WebAssembly. Therefore BEXE separates the **file format** from the **execution runtime**:

- `game.exe` is packed unchanged into `game.bexe`.
- The BEXE Browser opens the package.
- A compatibility runtime executes the embedded PE.

For broad real-Windows compatibility, use the included Web Runtime adapter with BoxedWine/ExeBrowser or the Linux fallback with Wine. The adapter deliberately does not pretend that arbitrary modern Windows games are universally compatible.

## BEXE format

Binary layout:

```
0-3    BEXE magic: 42 45 58 45
4      format version (1)
5      flags (1)
6-9    manifest length, little-endian uint32
10..   UTF-8 manifest JSON
...    original EXE bytes, unchanged
```

The manifest records filename, size, SHA-256, PE architecture and payload offset.

## Quick test

```bash
python3 bexe.py pack MyGame.exe -o MyGame.bexe
python3 bexe.py inspect MyGame.bexe
python3 bexe.py unpack MyGame.bexe -o MyGame.exe
```

## Linux/ChromeOS fallback

If Linux is enabled on ChromeOS, `install-linux-runtime.sh` installs Wine/Xvfb. Then:

```bash
./bexe-browser.sh
```

Open the local BEXE Browser and drop a `.bexe` file into it. Press Run. The browser server extracts the original EXE and launches it through Wine.

This fallback runs the actual Windows program, but its game window is provided by the Linux compatibility layer rather than magically becoming native Chrome pixels.

## Browser-native route

The project also includes `web-runtime.html`, which is a frontend/adapter for a real WASM Windows runtime. It points at the proven BoxedWine/ExeBrowser architecture rather than the tiny CPU interpreter used by the earlier prototypes. A complete bundled runtime is intentionally not copied into this source package because the runtime is large and has GPL/LGPL components.
