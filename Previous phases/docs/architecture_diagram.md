# Phase 2 Architecture Diagram

## PlantUML Source
- See `docs/architecture.puml`

## Graphical Representation
Render the diagram with any PlantUML renderer:
- VS Code PlantUML extension preview
- PlantUML CLI: `plantuml docs/architecture.puml`
- Online server: `https://www.plantuml.com/plantuml/uml/`

### Fallback (No local Java/PlantUML required)
If local rendering is unavailable, generate SVG through Kroki:

```powershell
$body = Get-Content "docs/architecture.puml" -Raw
Invoke-WebRequest -Uri "https://kroki.io/plantuml/svg" -Method Post -ContentType "text/plain" -Body $body -OutFile "docs/architecture.svg"
```

Or run the helper script:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/render-architecture.ps1
```

Generated file:
- `docs/architecture.svg`

## Dependency Direction (DIP)
- `plugins.inputs` depends on `core.contracts.PipelineService`
- `core.engine.TransformationEngine` depends on `core.contracts.DataSink`
- `plugins.outputs` satisfies `core.contracts.DataSink`
- `main.py` orchestrates and injects concrete dependencies
