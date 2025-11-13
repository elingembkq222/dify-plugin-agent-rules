import { useState } from 'react';
import { Form, Input, Button, message, Card, Row, Col } from 'antd';
import { CheckOutlined } from '@ant-design/icons';
import { validateRuleset } from '../api';
import { prettyPrintJson } from 'pretty-print-json';

const { TextArea } = Input;

const ValidateRule = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [validationResult, setValidationResult] = useState(null);

  const onFinish = (values) => {
    setLoading(true);
    try {
      const ruleset = JSON.parse(values.ruleset);
      const context = JSON.parse(values.context);
      validateRuleset({ ruleset, context })
        .then(response => {
          setValidationResult(response.data);
          if (response.data.success) {
            message.success('规则验证通过');
          } else {
            message.error(`规则验证失败: ${response.data.error}`);
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
      <Row gutter={[16, 16]}>
        <Col span={12}>
          <Form
            form={form}
            layout="vertical"
            onFinish={onFinish}
            className="validate-rule-form"
          >
            <Row gutter={[16, 16]}>
              <Col span={24}>
                <Form.Item
                  name="ruleset"
                  label="规则集 JSON"
                  rules={[{ required: true, message: '请输入规则集 JSON' }]}
                >
                  <TextArea
                    placeholder="输入规则集 JSON (可从规则列表复制)"
                    rows={12}
                    className="ruleset-textarea"
                  />
                </Form.Item>
              </Col>
              <Col span={24}>
                <Form.Item
                  name="context"
                  label="Context JSON"
                  rules={[{ required: true, message: '请输入 Context JSON' }]}
                >
                  <TextArea
                    placeholder='输入 Context JSON (例如: {"product": {"price": 50, "stock": 10}})'
                    rows={6}
                    className="context-textarea"
                  />
                </Form.Item>
              </Col>
            </Row>

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
        </Col>

        <Col span={12}>
          <Card title="验证结果" bordered={false} className="result-card">
            {!validationResult ? (
              <div style={{ textAlign: 'center', padding: '50px 0', color: '#999' }}>
                <p>请点击左侧"验证规则集"按钮查看结果</p>
              </div>
            ) : (
              <>                
                <div>
                  <strong>验证结果:</strong> {validationResult.success ? '通过 ✅' : '失败 ❌'}
                </div>
                {validationResult.success ? (
                  <div>
                    <strong>规则集结果:</strong>
                    <pre dangerouslySetInnerHTML={{ __html: prettyPrintJson.toHtml(validationResult.result, { indent: 3, lineNumbers: true, quoteKeys: false, linkUrls: true }) }}></pre>
                  </div>
                ) : (
                  <div>
                    <strong>错误信息:</strong> {validationResult.error}
                  </div>
                )}
              </>
            )}
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default ValidateRule;