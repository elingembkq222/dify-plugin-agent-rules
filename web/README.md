# Dify Agent Rules Plugin - Web UI

This is the frontend interface for the Dify Agent Rules Plugin, providing a user-friendly way to manage and interact with business rules.

## Features

- **Rules List**: View and filter all existing rulesets
- **Add Rule**: Create new rulesets with a structured JSON editor
- **Generate Rule**: Generate rulesets from natural language queries using LLM
- **Validate Rule**: Test rulesets against sample data to ensure they work correctly

## Quick Start

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

3. Build for production:
   ```bash
   npm run build
   ```

4. Start the production server:
   ```bash
   npm run server
   ```

## Usage

- **Rules List**: Navigate to the Rules List tab to see all rulesets. You can filter by target type.
- **Add Rule**: Use the Add Rule tab to create a new ruleset. Enter the JSON structure directly or use the editor.
- **Generate Rule**: In the Generate Rule tab, describe your business rules in natural language, and the plugin will generate a JSON ruleset.
- **Validate Rule**: In the Validate Rule tab, select a ruleset and enter sample data to test if it passes validation.

## Technology Stack

- React 18
- Ant Design
- Vite
- Express
