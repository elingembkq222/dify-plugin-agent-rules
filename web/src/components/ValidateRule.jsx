import { useState } from 'react';
import { Form, Input, Button, message, Card, Row, Col, Alert, Collapse } from 'antd';
import { CheckOutlined, ExclamationCircleOutlined } from '@ant-design/icons';
import { validateRuleset } from '../api';
import { prettyPrintJson } from 'pretty-print-json';

const { TextArea } = Input;
const { Panel } = Collapse;

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
            message.error(`规则验证失败: ${response.data.error?.message || response.data.error}`);
          }
        })
        .catch(error => {
          // 处理HTTP错误响应
          let errorMessage = '验证规则失败';
          let errorDetails = null;
          
          if (error.response) {
            // 服务器返回了错误状态码
            const errorData = error.response.data;
            
            if (errorData && errorData.error) {
              if (typeof errorData.error === 'object') {
                // 详细的错误对象
                errorMessage = `验证失败: ${errorData.error.message}`;
                errorDetails = {
                  type: errorData.error.type,
                  message: errorData.error.message,
                  traceback: errorData.error.traceback
                };
              } else {
                // 简单的错误字符串
                errorMessage = `验证失败: ${errorData.error}`;
              }
            } else {
              errorMessage = `验证失败 (${error.response.status}): ${error.response.statusText}`;
            }
          } else if (error.request) {
            // 请求已发送但没有收到响应
            errorMessage = '服务器无响应，请检查网络连接';
          } else {
            // 其他错误
            errorMessage = `验证失败: ${error.message}`;
          }
          
          message.error(errorMessage);
          console.error('验证规则失败:', error);
          
          // 设置错误结果以便显示
          setValidationResult({
            success: false,
            error: errorMessage,
            details: errorDetails
          });
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
                    <Alert
                      message="验证失败"
                      description={validationResult.error}
                      type="error"
                      icon={<ExclamationCircleOutlined />}
                      showIcon
                      style={{ marginBottom: 16 }}
                    />
                    
                    {validationResult.details && (
                      <Collapse ghost>
                        <Panel header="详细错误信息" key="error-details">
                          <div>
                            <strong>错误类型:</strong> {validationResult.details.type}
                          </div>
                          <div style={{ marginTop: 8 }}>
                            <strong>错误消息:</strong> {validationResult.details.message}
                          </div>
                          {validationResult.details.traceback && (
                            <div style={{ marginTop: 8 }}>
                              <strong>错误堆栈:</strong>
                              <pre style={{ 
                                backgroundColor: '#f5f5f5', 
                                padding: '8px', 
                                borderRadius: '4px',
                                fontSize: '12px',
                                overflow: 'auto',
                                maxHeight: '200px'
                              }}>
                                {validationResult.details.traceback}
                              </pre>
                            </div>
                          )}
                        </Panel>
                      </Collapse>
                    )}
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