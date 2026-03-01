# Phase 2 Architecture Diagram

## PlantUML Source
- See `docs/architecture.puml`

## Graphical Representation
Render the diagram with any PlantUML renderer:
- VS Code PlantUML extension preview
- PlantUML CLI: `plantuml docs/architecture.puml`
- Online server: `https://www.plantuml.com/plantuml/uml/`

## Dependency Direction (DIP)
- `plugins.inputs` depends on `core.contracts.PipelineService`
- `core.engine.TransformationEngine` depends on `core.contracts.DataSink`
- `plugins.outputs` satisfies `core.contracts.DataSink`
- `main.py` orchestrates and injects concrete dependencies
