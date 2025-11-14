import express from 'express';
import cors from 'cors';
import { spawn } from 'child_process';

const app = express();
const PORT = 3001;

app.use(cors());
app.use(express.json());

app.post('/api/generate_rule_from_query', (req, res) => {
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

app.post('/api/add_rule', (req, res) => {
  let rule_raw;

  // 自动识别格式
  if (req.body?.result?.rule) {
    rule_raw = req.body.result.rule;
  } else if (req.body?.rule) {
    rule_raw = req.body.rule;
  } else {
    rule_raw = req.body;
  }

  // 校验
  if (!rule_raw || !rule_raw.id || !rule_raw.target || !rule_raw.name || !rule_raw.rules) {
    return res.status(400).json({
      error: 'Missing required fields: id, target, name, rules',
      received: rule_raw
    });
  }

  // 构造数据库结构（保持与 MySQL x_rule_sets 字段一致）
  const now = new Date().toISOString().slice(0, 19).replace("T", " ");

  const rule_data = {
    id: rule_raw.id,
    target: rule_raw.target,
    name: rule_raw.name,
    description: rule_raw.description ?? null,
    applies_when: rule_raw.applies_when ?? null,
    rules: rule_raw.rules,
    on_fail: rule_raw.on_fail ?? null,
    created_at: now,
    updated_at: now
  };

  console.log("Prepared rule_data:", rule_data);

  // Python 直接接收 JSON，不做任何转义处理
  const pythonProcess = spawn('python3', [
    '-c',
    `
import json, os
from dotenv import load_dotenv
from provider.rule_storage import add_rule_set, init_rule_db

load_dotenv()
init_rule_db(os.getenv('RULE_DB_URL', 'sqlite:///rule_engine.db'))

rule_data = json.loads("""${JSON.stringify(rule_data)}""")
result = add_rule_set(rule_data)

print(json.dumps({
  "success": True,
  "ruleset_id": rule_data["id"]
}, ensure_ascii=False))
    `
  ], { cwd: '../' });

  let output = '';
  let error = '';

  pythonProcess.stdout.on('data', (d) => { output += d.toString(); });
  pythonProcess.stderr.on('data', (d) => { error += d.toString(); });

  pythonProcess.on('close', (code) => {
    if (code !== 0) {
      console.error("Python error:", error);
      return res.status(500).json({ error: "Python failed", detail: error });
    }

    try {
      res.json(JSON.parse(output));
    } catch (e) {
      console.error("JSON parse error:", output);
      res.status(500).json({ error: "Invalid JSON from Python", output });
    }
  });
});



// List all rules endpoint
app.get('/api/list_rules', (req, res) => {
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
app.post('/api/validate_ruleset', (req, res) => {
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