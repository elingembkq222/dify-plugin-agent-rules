import express from 'express';
import cors from 'cors';
import { spawn } from 'child_process';

const app = express();
const PORT = 3001;

app.use(cors());
app.use(express.json());

app.post('/generate_rule_from_query', (req, res) => {
  const { query } = req.body;
  
  if (!query) {
    return res.status(400).json({ error: 'Query parameter is required' });
  }

  // Use Python to generate the rule
  const pythonProcess = spawn('python3', [
    '-c',
    `import json;
from provider.llm_query_parser import parse_query_to_ruleset;
result = parse_query_to_ruleset('${query.replace(/'/g, "\\'")}', {});
print(json.dumps(result, ensure_ascii=False));`
  ], { cwd: '../' });

  let output = '';
  let error = '';

  pythonProcess.stdout.on('data', (data) => {
    output += data.toString();
  });

  pythonProcess.stderr.on('data', (data) => {
    error += data.toString();
  });

  pythonProcess.on('close', (code) => {
    if (code !== 0) {
      console.error('Python error:', error);
      return res.status(500).json({ error: 'Failed to generate rule', message: error });
    }

    try {
      const result = JSON.parse(output);
      res.json({ success: true, result: { query, rule: result } });
    } catch (err) {
      console.error('JSON parse error:', err);
      console.error('Raw output:', output);
      res.status(500).json({ error: 'Failed to parse rule result', message: err.message });
    }
  });
});

// Add a new rule endpoint
app.post('/add_rule', (req, res) => {
  const rule_data = req.body;
  
  if (!rule_data || !rule_data.target || !rule_data.name || !rule_data.rules) {
    return res.status(400).json({ error: 'Missing required fields: target, name, rules' });
  }

  // Convert the rule data to a JSON string that can be passed to Python
  const rule_json = JSON.stringify(rule_data).replace(/'/g, "\\'");

  // Use Python to add the rule
  const pythonProcess = spawn('python3', [
    '-c',
    `import json;
import os;
from dotenv import load_dotenv;
from provider.rule_storage import add_rule_set, init_rule_db;
# Load environment variables
load_dotenv();
# Initialize database
init_rule_db(os.getenv('RULE_DB_URL', 'sqlite:///rule_engine.db'));
result = add_rule_set(${rule_json});
print(json.dumps({ "success": True, "ruleset_id": result }, ensure_ascii=False));`
  ], { cwd: '../' });

  let output = '';
  let error = '';

  pythonProcess.stdout.on('data', (data) => {
    output += data.toString();
  });

  pythonProcess.stderr.on('data', (data) => {
    error += data.toString();
  });

  pythonProcess.on('close', (code) => {
    if (code !== 0) {
      console.error('Python error:', error);
      return res.status(500).json({ error: 'Failed to add rule', message: error });
    }

    try {
      const result = JSON.parse(output);
      res.json(result);
    } catch (err) {
      console.error('JSON parse error:', err);
      console.error('Raw output:', output);
      res.status(500).json({ error: 'Failed to parse add rule result', message: err.message });
    }
  });
});

// List all rules endpoint
app.get('/list_rules', (req, res) => {
  // Use Python to list all rules
  const pythonProcess = spawn('python3', [
    '-c',
    `import json;
import os;
from dotenv import load_dotenv;
from provider.rule_storage import list_all_rule_sets, init_rule_db;
# Load environment variables
load_dotenv();
# Initialize database
init_rule_db(os.getenv('RULE_DB_URL', 'sqlite:///rule_engine.db'));
result = list_all_rule_sets();
print(json.dumps({ "success": True, "rules": result }, ensure_ascii=False));`
  ], { cwd: '../' });

  let output = '';
  let error = '';

  pythonProcess.stdout.on('data', (data) => {
    output += data.toString();
  });

  pythonProcess.stderr.on('data', (data) => {
    error += data.toString();
  });

  pythonProcess.on('close', (code) => {
    if (code !== 0) {
      console.error('Python error:', error);
      return res.status(500).json({ error: 'Failed to list rules', message: error });
    }

    try {
      const result = JSON.parse(output);
      res.json(result);
    } catch (err) {
      console.error('JSON parse error:', err);
      console.error('Raw output:', output);
      res.status(500).json({ error: 'Failed to parse list rules result', message: err.message });
    }
  });
});

// Validate ruleset endpoint
app.post('/validate_ruleset', (req, res) => {
  const { ruleset_id, context, ruleset } = req.body;
  
  if (!context) {
    return res.status(400).json({ error: 'Missing required field: context' });
  }

  // Convert context to JSON string for Python execution
  const context_json = JSON.stringify(context);
  const ruleset_json = JSON.stringify(ruleset);

  // Use Python to validate the ruleset
  const pythonProcess = spawn('python3', [
    '-c',
    `import json;
import os;
from dotenv import load_dotenv;
from provider.rule_storage import get_rule_set, init_rule_db;
from provider.rule_engine import execute_rule_set;

# Load environment variables
load_dotenv();

# Initialize database
init_rule_db(os.getenv('RULE_DB_URL', 'sqlite:///rule_engine.db'));

# Get the ruleset
ruleset = None;
${ruleset ? `ruleset = ${ruleset_json};` : `ruleset = get_rule_set('${ruleset_id}');`}
if not ruleset:
    print(json.dumps({"success": False, "error": "Ruleset not found"}, ensure_ascii=False));
else:
    # Execute the ruleset
    context = ${context_json};
    result = execute_rule_set(ruleset, context);
    print(json.dumps({"success": True, "result": result}, ensure_ascii=False));`
  ], { cwd: '../' });

  let output = '';
  let error = '';

  pythonProcess.stdout.on('data', (data) => {
    output += data.toString();
  });

  pythonProcess.stderr.on('data', (data) => {
    error += data.toString();
  });

  pythonProcess.on('close', (code) => {
    if (code !== 0) {
      console.error('Python error:', error);
      return res.status(500).json({ error: 'Failed to validate ruleset', message: error });
    }

    try {
      const result = JSON.parse(output);
      res.json(result);
    } catch (err) {
      console.error('JSON parse error:', err);
      console.error('Raw output:', output);
      res.status(500).json({ error: 'Failed to parse validate ruleset result', message: err.message });
    }
  });
});

app.listen(PORT, () => {
  console.log(`Direct server running on http://localhost:${PORT}`);
  console.log('API endpoint: /api/generate_rule_from_query');
  console.log('API endpoint: /api/add_rule');
  console.log('API endpoint: /api/list_rules');
  console.log('API endpoint: /api/validate_ruleset');
});