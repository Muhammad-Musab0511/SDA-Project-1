# SDA Project Phase 1 - Version Control and Documentation

This file is a simple guide for how we manage code and documentation for Phase 1.

## Project Goal (Phase 1)
Build a functional, data-driven GDP analysis system in Python using functional programming and clean module design.

## Core Rules (Keep These in Mind)
- Use functional constructs: map, filter, lambda, and list/dict comprehensions.
- Avoid heavy loop-based code when possible.
- Keep modules separate (Single Responsibility Principle).
- No hardcoded region, year, or operation in code. Use config.json.

## Functional Requirements (Short Version)
- Load GDP data from CSV.
- Clean missing values and data types.
- Filter by region, year, and optional country.
- Compute stats: average or sum.
- Create at least two region charts and two year-specific charts.
- Label each chart clearly (title and axes).

## Configuration Driven Behavior
All filtering and calculations are driven by config.json:
- region
- year
- operation (average or sum)
- dashboard output choice

## Design Requirements
Modules should stay focused:
- Data Loader: read and clean data
- Data Processor: filter and compute stats
- Dashboard/Visualizer: print results and show charts

## Error Handling
- Show clear messages for missing/invalid CSV files.
- Validate config fields and display helpful errors.

## Version Control (Simple Workflow)
- Everyone works on main (or small feature branches if needed).
- Make small commits with clear messages.
- Commit often during development.

Example commit messages:
- Add functional CSV loader
- Fix region filter logic
- Add bar and pie charts