import { useState } from 'react';
import { Form, Input, Button, message, Card } from 'antd';
import { TrademarkOutlined } from '@ant-design/icons';
import { generateRule } from '../api';
import { prettyPrintJson } from 'pretty-print-json';

const { TextArea } = Input;

const GenerateRule = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [generatedResult, setGeneratedResult] = useState(null);

  const onFinish = (values) => {
    setLoading(true);
    generateRule(values)
      .then(response => {
        setGeneratedResult(response.data);
        message.success('规则生成成功');
      })
      .catch(error => {
        message.error('生成规则失败');
        console.error('生成规则失败:', error);
      })
      .finally(() => {
        setLoading(false);
      });
  };

  const handleCopy = () => {
    if (generatedResult?.rules) {
      navigator.clipboard.writeText(JSON.stringify(generatedResult.rules, null, 2))
        .then(() => message.success('规则已复制到剪贴板'))
        .catch(() => message.error('复制失败'));
    }
  };

  return (
    <div className="generate-rule">
      <h3>从查询生成规则</h3>
      <Form
        form={form}
        layout="vertical"
        onFinish={onFinish}
        className="generate-rule-form"
      >
        <Form.Item
          name="query"
          label="自然语言查询"
          rules={[{ required: true, message: '请输入自然语言查询' }]}
        >
          <TextArea
            placeholder="输入自然语言查询"
            rows={6}
            className="query-textarea"
          />
        </Form.Item>

        <Form.Item
          name="type"
          label="规则类型"
          rules={[{ required: true, message: '请选择规则类型' }]}
        >
          <Input placeholder="输入规则类型 (可选)" />
        </Form.Item>

        <Form.Item
          name="target"
          label="目标"
        >
          <Input placeholder="输入目标 (可选)" />
        </Form.Item>

        <Form.Item>
          <Button
            type="primary"
            htmlType="submit"
            loading={loading}
            icon={<TrademarkOutlined />}
            block
          >
            生成规则
          </Button>
        </Form.Item>
      </Form>

      {generatedResult && (
        <Card title="生成结果" bordered={false} className="result-card">
          <div>
            <strong>生成的规则:</strong>
            <pre dangerouslySetInnerHTML={{ __html: prettyPrintJson.toHtml(generatedResult.rules, { indent: 3, lineNumbers: true, quoteKeys: false, linkUrls: true }) }} />
          </div>
          <Button
            type="primary"
            onClick={handleCopy}
            disabled={!generatedResult?.rules}
            className="copy-btn"
          >
            复制规则
          </Button>
        </Card>
      )}
    </div>
  );
};

export default GenerateRule;