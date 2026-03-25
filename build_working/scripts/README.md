# Scripts

## run_release.ps1

Executa o binario em modo normal, limpando variaveis de debug mais invasivas.

## run_gate_deep_check.ps1

Executa com telemetria profunda do gate A110 e grava log em:

- `CastlevaniaRecomp-master/blackscreen_gate_deep_check.log`

Uso sugerido:

```powershell
powershell -ExecutionPolicy Bypass -File .\CastlevaniaRecomp-master\scripts\run_gate_deep_check.ps1
```
