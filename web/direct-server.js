import express from 'express';
import cors from 'cors';
import { spawn } from 'child_process';

const app = express();
const PORT = 3001;

app.use(cors());
app.use(express.json());

// 生成规则
app.post('/api/generate_rule_from_query', (req, res) => {
  const now = new Date().toISOString();
  const rule_raw = req.body;
  const query = rule_raw.query;
  const target = rule_raw.target;

  // Python 直接接收 JSON，不做任何转义处理
  const pythonProcess = spawn('python3', [
    '-c',
    `
import json, os
from dotenv import load_dotenv
from provider.llm_query_parser import parse_query_to_rule
from provider.rule_storage import generate_rule_id

load_dotenv()

rule = parse_query_to_rule("""${query}""", """${target}""")

# 确保规则有 ID
if "id" not in rule:
    rule["id"] = generate_rule_id()

# 确保每个规则都有 ID
for i, sub_rule in enumerate(rule.get("rules", [])):
    if "id" not in sub_rule:
        sub_rule["id"] = generate_rule_id()

print(json.dumps({
  "success": True,
  "rule": rule
}, ensure_ascii=False))
    `
  ], { cwd: '../' });

  let output = '';
  let error = '';

  pythonProcess.stdout.on('data', (d) => { output += d.toString(); });
  pythonProcess.stderr.on('data', (d) => { error += d.toString(); });

  pythonProcess.on('close', (code) => {
    if (code !== 0) {
      console.error(`Python error: ${error}`);
      return res.status(500).json({ error: "Python failed", detail: error });
    }

    try {
      const result = JSON.parse(output);
      res.json(result);
    } catch (parseError) {
      console.error(`JSON parse error: ${parseError}, output: ${output}`);
      res.status(500).json({ error: "JSON parse failed", detail: output });
    }
  });
});

// 添加规则
app.post('/api/add_rule', (req, res) => {
  const now = new Date().toISOString();
  const rule_raw = req.body;
  // console.log(rule_raw);
  // 确保规则数据包含必要的字段
  if (!rule_raw.rules) {
    return res.status(400).json({ error: "Missing rules in request body" });
  }

  // 提取必要的字段
  const rule_data = {
    id: rule_raw.id ?? crypto.randomUUID(),
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
      console.error(`Python error: ${error}`);
      return res.status(500).json({ error: "Python failed", detail: error });
    }

    try {
      const result = JSON.parse(output);
      res.json(result);
    } catch (parseError) {
      console.error(`JSON parse error: ${parseError}, output: ${output}`);
      res.status(500).json({ error: "JSON parse failed", detail: output });
    }
  });
});

// 更新规则
app.post('/api/update_rule', (req, res) => {
  const now = new Date().toISOString();
  const rule_raw = req.body;
  // 确保规则数据包含必要的字段
  if (!rule_raw.id) {
    return res.status(400).json({ error: "Missing rule set ID in request body" });
  }
  if (!rule_raw.rules) {
    return res.status(400).json({ error: "Missing rules in request body" });
  }

  // 提取必要的字段
  const rule_data = {
    id: rule_raw.id,
    target: rule_raw.target,
    name: rule_raw.name,
    description: rule_raw.description ?? null,
    applies_when: rule_raw.applies_when ?? null,
    rules: rule_raw.rules,
    on_fail: rule_raw.on_fail ?? null,
    created_at: rule_raw.created_at,
    updated_at: now
  };

  console.log("Prepared rule_data for update:", rule_data);

  // Python 直接接收 JSON，不做任何转义处理
  const pythonProcess = spawn('python3', [
    '-c',
    `
import json, os
from dotenv import load_dotenv
from provider.rule_storage import update_rule_set, init_rule_db

load_dotenv()
init_rule_db(os.getenv('RULE_DB_URL', 'sqlite:///rule_engine.db'))

rule_data = json.loads("""${JSON.stringify(rule_data)}""")
result = update_rule_set(rule_data)

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
      console.error(`Python error: ${error}`);
      return res.status(500).json({ error: "Python failed", detail: error });
    }

    try {
      const result = JSON.parse(output);
      res.json(result);
    } catch (parseError) {
      console.error(`JSON parse error: ${parseError}, output: ${output}`);
      res.status(500).json({ error: "JSON parse failed", detail: output });
    }
  });
});

// 列出规则
app.get('/api/list_rules', (req, res) => {
  // Python 直接接收 JSON，不做任何转义处理
  const pythonProcess = spawn('python3', [
    '-c',
    `
import json, os
from dotenv import load_dotenv
from provider.rule_storage import get_all_rules, init_rule_db

load_dotenv()
init_rule_db(os.getenv('RULE_DB_URL', 'sqlite:///rule_engine.db'))

rules = get_all_rules()

# 确保每个规则集都有 ID
for rule_set in rules:
    if "id" not in rule_set:
        rule_set["id"] = "unknown"

print(json.dumps({
  "success": True,
  "rulesets": rules
}, ensure_ascii=False))
    `
  ], { cwd: '../' });

  let output = '';
  let error = '';

  pythonProcess.stdout.on('data', (d) => { output += d.toString(); });
  pythonProcess.stderr.on('data', (d) => { error += d.toString(); });

  pythonProcess.on('close', (code) => {
    if (code !== 0) {
      console.error(`Python error: ${error}`);
      return res.status(500).json({ error: "Python failed", detail: error });
    }

    try {
      const result = JSON.parse(output);
      res.json(result);
    } catch (parseError) {
      console.error(`JSON parse error: ${parseError}, output: ${output}`);
      res.status(500).json({ error: "JSON parse failed", detail: output });
    }
  });
});

// 验证规则集
app.post('/api/validate_ruleset', (req, res) => {
  const data = req.body;
  const now = new Date().toISOString();
  const ruleset = data.ruleset;
  const user_input = data.user_input;
  const context = data.context;

  // Python 直接接收 JSON，不做任何转义处理
  const pythonProcess = spawn('python3', [
    '-c',
    `
import json, os
from dotenv import load_dotenv
from provider.rule_validator import validate_ruleset

load_dotenv()

result = validate_ruleset("""${json.dumps(ruleset)}""", """${json.dumps(user_input)}""", """${json.dumps(context)}""")

print(json.dumps({
  "success": True,
  "results": result
}, ensure_ascii=False))
    `
  ], { cwd: '../' });

  let output = '';
  let error = '';

  pythonProcess.stdout.on('data', (d) => { output += d.toString(); });
  pythonProcess.stderr.on('data', (d) => { error += d.toString(); });

  pythonProcess.on('close', (code) => {
    if (code !== 0) {
      console.error(`Python error: ${error}`);
      return res.status(500).json({ error: "Python failed", detail: error });
    }

    try {
      const result = JSON.parse(output);
      res.json(result);
    } catch (parseError) {
      console.error(`JSON parse error: ${parseError}, output: ${output}`);
      res.status(500).json({ error: "JSON parse failed", detail: output });
    }
  });
});

app.listen(PORT, () => {
  console.log(`
🚀 Direct server running on http://localhost:${PORT}`);
  console.log('📡 API endpoints:');
  console.log('   POST   /api/generate_rule_from_query - Generate rule from natural language query');
  console.log('   POST   /api/add_rule - Add a new rule set');
  console.log('   POST   /api/update_rule - Update an existing rule set');
  console.log('   GET    /api/list_rules - List all rule sets');
  console.log('   POST   /api/validate_ruleset - Validate a rule set against input data');
  console.log('\n');
});