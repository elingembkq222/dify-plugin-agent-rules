import { useState } from 'react';
import { Form, Input, Select, Button, message } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { addRule } from '../api';

const { TextArea } = Input;

const AddRule = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  const onFinish = (values) => {
    setLoading(true);
    addRule(values)
      .then(response => {
        message.success('规则添加成功');
        form.resetFields();
      })
      .catch(error => {
        message.error('添加规则失败');
        console.error('添加规则失败:', error);
      })
      .finally(() => {
        setLoading(false);
      });
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
          name="name"
          label="规则集名称"
          rules={[{ required: true, message: '请输入规则集名称' }]}
        >
          <Input placeholder="输入规则集名称" />
        </Form.Item>

        <Form.Item
          name="type"
          label="规则类型"
          rules={[{ required: true, message: '请选择规则类型' }]}
        >
          <Select placeholder="选择规则类型">
            <Select.Option value="function">函数规则</Select.Option>
            <Select.Option value="regex">正则规则</Select.Option>
            <Select.Option value="template">模板规则</Select.Option>
          </Select>
        </Form.Item>

        <Form.Item
          name="target"
          label="目标"
          rules={[{ required: true, message: '请输入目标' }]}
        >
          <Input placeholder="输入目标" />
        </Form.Item>

        <Form.Item
          name="description"
          label="规则描述"
        >
          <Input placeholder="输入规则描述" />
        </Form.Item>

        <Form.Item
          name="function"
          label="规则函数"
          rules={[{ required: true, message: '请输入规则函数' }]}
        >
          <TextArea
            placeholder="输入规则函数 (Python代码)"
            rows={8}
            className="rule-function-textarea"
          />
        </Form.Item>

        <Form.Item>
          <Button
            type="primary"
            htmlType="submit"
            loading={loading}
            icon={<PlusOutlined />}
            block
          >
            添加规则
          </Button>
        </Form.Item>
      </Form>
    </div>
  );
};

export default AddRule;