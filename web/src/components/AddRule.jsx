import { useState } from 'react';
import { Form, Input, Button, message, Card, Row, Col } from 'antd';
import { PlusOutlined, SaveOutlined } from '@ant-design/icons';
import { addRule, generateRule } from '../api';

const { TextArea } = Input;

const AddRule = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [generatedResult, setGeneratedResult] = useState(null);
  const [editableResult, setEditableResult] = useState('');

  // Generate rule from natural language query
  const handleGenerate = () => {
    setLoading(true);
    form.validateFields(['query'])
      .then(values => {
        return generateRule(values);
      })
      .then(generateResponse => {
        const generatedResult = generateResponse.data;
        const generatedRuleset = generatedResult.rule || generatedResult;
        setGeneratedResult(generatedRuleset);
        // Convert to formatted JSON string for editing
        setEditableResult(JSON.stringify(generatedRuleset, null, 2));
        message.success('规则生成成功');
      })
      .catch(error => {
        message.error('规则生成失败');
        console.error('规则生成失败:', error);
      })
      .finally(() => {
        setLoading(false);
      });
  };

  // Save the generated and possibly edited rule set
  const handleSave = () => {
    if (!editableResult) return;
    
    try {
      // Parse the edited JSON
      const parsedRuleset = JSON.parse(editableResult);
      setLoading(true);
      
      return addRule(parsedRuleset)
        .then(addResponse => {
          message.success('规则添加成功');
          form.resetFields();
          setGeneratedResult(null);
          setEditableResult('');
        })
        .catch(error => {
          message.error('规则添加失败');
          console.error('规则添加失败:', error);
        })
        .finally(() => {
          setLoading(false);
        });
    } catch (parseError) {
      message.error('JSON格式无效，请检查编辑内容');
      return Promise.reject(parseError);
    }
  };

  // Handle changes to the editable JSON
  const handleEditableResultChange = (e) => {
    setEditableResult(e.target.value);
  };

  // Format the JSON content
  const handleFormatJSON = () => {
    try {
      const parsed = JSON.parse(editableResult);
      const formatted = JSON.stringify(parsed, null, 2);
      setEditableResult(formatted);
      message.success('JSON格式化成功');
    } catch (error) {
      message.error('JSON格式无效，无法格式化');
      console.error('JSON格式化失败:', error);
    }
  };

  const handleCopy = () => {
    if (editableResult) {
      navigator.clipboard.writeText(editableResult)
        .then(() => message.success('生成的规则已复制到剪贴板'))
        .catch(() => message.error('复制失败'));
    }
  };

  return (
    <div className="add-rule">
      <h3>添加新规则</h3>
      <Row gutter={[16, 16]}>
        <Col span={12}>
          <Form
            form={form}
            layout="vertical"
            className="add-rule-form"
          >
            <Form.Item
              name="query"
              label="自然语言查询"
              rules={[{ required: true, message: '请输入自然语言查询' }]}
            >
              <TextArea
                placeholder="例如: 添加生日假规则，员工生日前后一个月内可休1天，试用期员工需在转正后一个月内使用"
                rows={12}
                className="rule-function-textarea"
              />
            </Form.Item>

            <Form.Item>
              <div style={{ display: 'flex', gap: '12px', marginBottom: '24px' }}>
                <Button
                  type="primary"
                  onClick={handleGenerate}
                  loading={loading}
                  icon={<PlusOutlined />}
                  block
                >
                  生成规则
                </Button>
                <Button
                  type="primary"
                  onClick={handleSave}
                  loading={loading}
                  disabled={!editableResult}
                  icon={<SaveOutlined />}
                  block
                >
                  保存规则
                </Button>
              </div>
            </Form.Item>
          </Form>
        </Col>

        <Col span={12}>
          <Card title="生成的规则集 (可编辑)" bordered={false} className="result-card">
            {!editableResult ? (
              <div style={{ textAlign: 'center', padding: '80px 0', color: '#999' }}>
                <p>请点击左侧"生成规则"按钮查看结果</p>
              </div>
            ) : (
              <>                
                <TextArea
                  value={editableResult}
                  onChange={handleEditableResultChange}
                  rows={20}
                  style={{ fontFamily: 'monospace', fontSize: '14px', marginBottom: '12px' }}
                  placeholder="生成的规则将显示在这里，可以直接编辑"
                />
                <div style={{ display: 'flex', gap: '12px' }}>
                  <Button
                    type="default"
                    onClick={handleCopy}
                    disabled={!generatedResult}
                    className="copy-btn"
                  >
                    复制规则
                  </Button>
                  <Button
                    type="default"
                    onClick={handleFormatJSON}
                    disabled={!editableResult}
                  >
                    格式化JSON
                  </Button>
                  <Button
                    type="default"
                    onClick={() => setEditableResult(JSON.stringify(generatedResult, null, 2))}
                    disabled={!generatedResult}
                  >
                    重置
                  </Button>
                </div>
              </>
            )}
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default AddRule;