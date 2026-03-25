# CastlevaniaRecomp (starter)

Projeto inicial para recompilar Castlevania usando o framework PSXRecomp neste repositório.

## Estrutura

- `isos/` - coloque aqui o executável extraído do jogo (ex.: `SLUS_000.67`)
- `generated/` - saída do recompiler (`castlevania_full.c`, `castlevania_dispatch.c`)
- `annotations/` - notas opcionais de funções/endereço

## 1) Gerar C traduzido

No terminal MSYS2 UCRT64, na raiz de `psxrecomp`:

```bash
./build/recompiler/PSXRecomp.exe CastlevaniaRecomp/isos/SLUS_000.67
```

Se os arquivos gerados vierem com outro nome-base, ajuste `GAME_BASENAME` no `CMakeLists.txt`.

## 2) Compilar o projeto do jogo

Ainda na raiz de `psxrecomp`:

```bash
cmake -S CastlevaniaRecomp -B CastlevaniaRecomp/build -G Ninja
ninja -C CastlevaniaRecomp/build
```

## 3) Executar

```bash
./CastlevaniaRecomp/build/CastlevaniaRecomp.exe
```

Na primeira execução, selecione o arquivo `.cue` do disco quando o launcher pedir.

## Ajustes importantes

- `GAME_EXE_FILENAME`: nome do EXE PS1 real dentro do disco
- `GAME_EXPECTED_CRC32`: `0` para desativar validação, ou defina o CRC correto
- `GAME_DISPLAY_ENTRY`: começa em `0` e depois ajuste com análise do jogo
