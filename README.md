GDP Growth Rate of Each Country in the given continent for the given data range
# SDA Project - Phase 2

Partners of this Project:
- Muhammad Musab (24L-0511)
- Abdullah Kamran (24L-0581)

## Objective
Phase 2 transitions the project from script-style execution to a modular architecture using Dependency Inversion Principle (DIP).

## Package Structure
- `main.py` → orchestrator/bootstrap layer
- `core/` → domain logic and Protocol contracts
- `plugins/inputs.py` → `CSVReader`, `JSONReader`
- `plugins/outputs.py` → `ConsoleWriter`, `GraphicsChartWriter`
- `docs/architecture.puml` → PlantUML architecture design
- `core/generated_from_plantuml.py` → structural code generated from architecture

## DIP Rules Implemented
- Inbound abstraction: input plugins call `PipelineService` protocol
- Outbound abstraction: core engine writes via `DataSink` protocol
- Contract ownership: protocols are defined in `core/contracts.py`

## Configuration (`config.json`)
```json
{
	"input": {
		"driver": "csv",
		"path": "data/gdp_with_continent_filled.csv"
	},
	"output": {
		"drivers": ["console"]
	},
	"analysis": {
		"region": "Asia",
		"year": 2020,
		"start_year": 2010,
		"end_year": 2022,
		"decline_years": 5
	}
}
```

## Run
```bash
python main.py
```

## Supported Drivers
- Input: `csv`, `json`
- Output: `console`, `chart` (or both by listing both drivers)

## Analytics Produced
1. Top 10 countries by GDP (continent + year)
2. Bottom 10 countries by GDP (continent + year)
3. GDP growth rate by country (continent + range)
4. Average GDP by continent (range)
5. Total global GDP trend (range)
6. Fastest growing continent (range)
7. Countries with consistent GDP decline in last X years
8. Continent contribution to global GDP (range)
