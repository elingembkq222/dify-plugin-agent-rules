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

app.listen(PORT, () => {
  console.log(`Direct server running on http://localhost:${PORT}`);
  console.log('API endpoint: /api/generate_rule_from_query');
});