import { useState } from 'react';
import { Form, Input, Button, message, Card } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { addRule, generateRule } from '../api';

const { TextArea } = Input;

const AddRule = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [generatedResult, setGeneratedResult] = useState(null);

  const onFinish = (values) => {
    setLoading(true);
    // First generate the rule set from natural language query
    generateRule(values)
      .then(generateResponse => {
        const generatedResult = generateResponse.data;
        const generatedRuleset = generatedResult.rule || generatedResult;
        setGeneratedResult(generatedRuleset);
        // Then save the generated rule set
        return addRule(generatedRuleset);
      })
      .then(addResponse => {
        message.success('规则生成并添加成功');
        form.resetFields();
        setGeneratedResult(null);
      })
      .catch(error => {
        message.error('规则生成或添加失败');
        console.error('规则生成或添加失败:', error);
      })
      .finally(() => {
        setLoading(false);
      });
  };

  const handleCopy = () => {
    if (generatedResult) {
      navigator.clipboard.writeText(JSON.stringify(generatedResult, null, 2))
        .then(() => message.success('生成的规则已复制到剪贴板'))
        .catch(() => message.error('复制失败'));
    }
  };

  return (
    <div className="add-rule">
      <h3>添加新规则</h3>
      <Form
        form={form}
        layout="vertical"
        onFinish={onFinish}
        className="add-rule-form"
      >
        <Form.Item
          name="query"
          label="自然语言查询"
          rules={[{ required: true, message: '请输入自然语言查询' }]}
        >
          <TextArea
            placeholder="例如: 添加生日假规则，员工生日前后一个月内可休1天，试用期员工需在转正后一个月内使用"
            rows={6}
            className="rule-function-textarea"
          />
        </Form.Item>

        <Form.Item
          name="name"
          label="规则集名称 (可选)"
        >
          <Input placeholder="输入规则集名称 (可选，生成时会自动生成)" />
        </Form.Item>

        <Form.Item
          name="target"
          label="目标 (可选)"
        >
          <Input placeholder="输入目标 (可选，如: leave_apply)" />
        </Form.Item>

        <Form.Item>
          <Button
            type="primary"
            htmlType="submit"
            loading={loading}
            icon={<PlusOutlined />}
            block
          >
            生成并添加规则
          </Button>
        </Form.Item>
      </Form>

      {generatedResult && (
        <Card title="生成的规则集" bordered={false} className="result-card">
          <pre>{JSON.stringify(generatedResult, null, 2)}</pre>
          <Button
            type="default"
            onClick={handleCopy}
            disabled={!generatedResult}
            className="copy-btn"
          >
            复制规则
          </Button>
        </Card>
      )}
    </div>
  );
};

export default AddRule;