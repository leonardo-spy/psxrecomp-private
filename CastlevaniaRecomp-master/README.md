# CastlevaniaRecomp

Castlevania: Symphony of the Night (USA, SLUS_000.67) rodando nativamente em PC via PSXRecomp.

Este projeto e uma pasta dedicada no estilo do TombaRecomp, montada a partir do fluxo de investigacao e correcoes aplicadas no workspace `psxrecomp`.

## Status atual

- Bootstrap e display loop inicial funcionando
- Gate critico de A110 (`0x8001A194`) agora pode abrir naturalmente no caminho padrao do projeto
- Branch natural confirmado em runtime quando `v0` cruza `0x3C3` com `c9278=0x3C2`

Limitacoes atuais:
- Ainda ha cenarios com black screen (sem eventos de GPU no mesmo run de diagnostico)
- O projeto esta em fase de estabilizacao funcional

## Estrutura

- `CMakeLists.txt` - build do jogo
- `extras.cpp` - hooks e extras do runner
- `generated/` - codigo C traduzido do EXE PS1
- `annotations/` - anotacoes auxiliares
- `scripts/` - scripts de execucao/diagnostico
- `isos/` - voce deve criar e colocar seus arquivos de disco (gitignored)

## Requisitos

- Windows 10+ 64-bit
- MSYS2 UCRT64 (gcc/g++)
- CMake + Ninja
- GPU com OpenGL 3.3+
- Copia legal do jogo (SLUS_000.67 + CUE/BIN)

## Build

Na raiz do repositorio `psxrecomp`:

```powershell
$env:Path = "C:\PROGRA~2\msys64\ucrt64\bin;C:\PROGRA~2\msys64\usr\bin;" + $env:Path
cmake -S CastlevaniaRecomp-master -B CastlevaniaRecomp-master/build -G Ninja
cmake --build CastlevaniaRecomp-master/build --config Release
```

## Execucao

```powershell
.\CastlevaniaRecomp-master\build\CastlevaniaRecomp.exe --cue "CastlevaniaRecomp-master\isos\Castlevania - Symphony of the Night (USA).cue"
```

Se preferir, use os scripts em `scripts/`.

## Notas de configuracao relevantes

- O modo de fonte do override de `0x80015308` usa por padrao `c2ac-deref`.
- Voce ainda pode forcar manualmente via env:
  - `PSX_CASTLE_15308_SOURCE_MODE=ptr`
  - `PSX_CASTLE_15308_SOURCE_MODE=deref`
  - `PSX_CASTLE_15308_SOURCE_MODE=c2ac-deref`

## Licenca e direitos

- Este projeto usa a infraestrutura de PSXRecomp.
- Nenhum asset do jogo e distribuido aqui.
- Castlevania e seus assets pertencem aos respectivos detentores de direitos.
