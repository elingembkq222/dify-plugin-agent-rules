import { useState } from 'react';
import { Form, Input, Button, message, Card } from 'antd';
import { CheckOutlined } from '@ant-design/icons';
import { validateRuleset } from '../api';

const { TextArea } = Input;

const ValidateRule = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [validationResult, setValidationResult] = useState(null);

  const onFinish = (values) => {
    setLoading(true);
    try {
      const ruleset = JSON.parse(values.ruleset);
      validateRuleset(ruleset)
        .then(response => {
          setValidationResult(response.data);
          if (response.data.success) {
            message.success('规则验证通过');
          } else {
            message.error(`规则验证失败: ${response.data.message}`);
          }
        })
        .catch(error => {
          message.error('验证规则失败');
          console.error('验证规则失败:', error);
        })
        .finally(() => {
          setLoading(false);
        });
    } catch (jsonError) {
      message.error('JSON格式无效，请检查输入');
      setLoading(false);
    }
  };

  return (
    <div className="validate-rule">
      <h3>验证规则集</h3>
      <Form
        form={form}
        layout="vertical"
        onFinish={onFinish}
        className="validate-rule-form"
      >
        <Form.Item
          name="ruleset"
          label="规则集 JSON"
          rules={[{ required: true, message: '请输入规则集 JSON' }]}
        >
          <TextArea
            placeholder="输入规则集 JSON"
            rows={12}
            className="ruleset-textarea"
          />
        </Form.Item>

        <Form.Item>
          <Button
            type="primary"
            htmlType="submit"
            loading={loading}
            icon={<CheckOutlined />}
            block
          >
            验证规则集
          </Button>
        </Form.Item>
      </Form>

      {validationResult && (
        <Card title="验证结果" bordered={false} className="result-card">
          <div>
            <strong>验证结果:</strong> {validationResult.success ? '通过 ✅' : '失败 ❌'}
          </div>
          <div>
            <strong>消息:</strong> {validationResult.message}
          </div>
          {validationResult.details && (
            <div>
              <strong>详细信息:</strong>
              <pre>{JSON.stringify(validationResult.details, null, 2)}</pre>
            </div>
          )}
        </Card>
      )}
    </div>
  );
};

export default ValidateRule;