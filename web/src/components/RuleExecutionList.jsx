import React, { useState } from 'react';
import { Table, Button, Modal, Form, Input, message, Space } from 'antd';
import { EditOutlined, DeleteOutlined, UpOutlined, DownOutlined, PlusOutlined, SaveOutlined } from '@ant-design/icons';
import { updateRule } from '../api';



const RuleExecutionList = ({ ruleSet, onUpdate }) => {
  const [expandForm] = Form.useForm();
  const [rules, setRules] = useState(ruleSet.rules || []);
  const [editingRule, setEditingRule] = useState(null);
  const [isModalVisible, setIsModalVisible] = useState(false);

  // 打开编辑/新增弹窗
  const showModal = (rule = null) => {
    setEditingRule(rule);
    if (rule) {
      // 如果是编辑，填充表单数据
      expandForm.setFieldsValue(rule);
    } else {
      // 如果是新增，重置表单
      expandForm.resetFields();
    }
    setIsModalVisible(true);
  };

  // 关闭弹窗
  const handleCancel = () => {
    setIsModalVisible(false);
    setEditingRule(null);
  };

  // 保存规则
  const handleSave = () => {
    expandForm.validateFields()
      .then(values => {
        let updatedRules;
        if (editingRule) {
          // 更新现有规则
          updatedRules = rules.map(rule => rule.id === editingRule.id ? { ...rule, ...values } : rule);
        } else {
          // 新增规则，生成 UUID
          updatedRules = [...rules, { ...values, id: crypto.randomUUID() }];
        }
        // 更新规则集
        updateRule({ ...ruleSet, rules: updatedRules })
          .then(() => {
            message.success('规则保存成功');
            setIsModalVisible(false);
            onUpdate(); // 刷新规则列表
          })
          .catch(err => {
            message.error('规则保存失败');
            console.error('Error saving rule:', err);
          });
      })
      .catch(errorInfo => {
        message.error('表单验证失败');
        console.error('Form validation failed:', errorInfo);
      });
  };

  // 删除规则
  const handleDelete = (id) => {
    Modal.confirm({
      title: '确认删除规则',
      content: '删除规则后将无法恢复，是否继续？',
      okText: '删除',
      okType: 'danger',
      cancelText: '取消',
      onOk: () => {
        const updatedRules = rules.filter(rule => rule.id !== id);
        updateRule({ ...ruleSet, rules: updatedRules })
          .then(() => {
            message.success('规则删除成功');
            onUpdate(); // 刷新规则列表
          })
          .catch(err => {
            message.error('规则删除失败');
            console.error('Error deleting rule:', err);
          });
      },
    });
  };

  // 上移规则
  const moveUp = (index) => {
    if (index === 0) return;
    const newRules = [...rules];
    [newRules[index], newRules[index - 1]] = [newRules[index - 1], newRules[index]];
    setRules(newRules);
  };

  // 下移规则
  const moveDown = (index) => {
    if (index === rules.length - 1) return;
    const newRules = [...rules];
    [newRules[index], newRules[index + 1]] = [newRules[index + 1], newRules[index]];
    setRules(newRules);
  };

  // 保存规则顺序
  const saveOrder = () => {
    updateRule({ ...ruleSet, rules })
      .then(() => {
        message.success('规则顺序保存成功');
        onUpdate(); // 刷新规则列表
      })
      .catch(err => {
        message.error('规则顺序保存失败');
        console.error('Error saving rule order:', err);
      });
  };

  // 定义规则表格列
  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      ellipsis: true,
    },
    {
      title: '规则名称',
      dataIndex: 'name',
      key: 'name',
      ellipsis: true,
    },
    {
      title: '规则类型',
      dataIndex: 'type',
      key: 'type',
      ellipsis: true,
    },
    {
      title: '规则描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
    },
    {
      title: '规则表达式',
      dataIndex: 'expression',
      key: 'expression',
      ellipsis: true,
    },
    {
      title: '提示信息',
      dataIndex: 'message',
      key: 'message',
      ellipsis: true,
    },
    {
      title: '操作',
      key: 'action',
      render: (text, record, index) => (
        <Space size="small">
          <Button type="primary" icon={<EditOutlined />} size="small" onClick={() => showModal(record)}>
            编辑
          </Button>
          <Button danger icon={<DeleteOutlined />} size="small" onClick={() => handleDelete(record.id)}>
            删除
          </Button>
          <Button icon={<UpOutlined />} size="small" disabled={index === 0} onClick={() => moveUp(index)}>
            上移
          </Button>
          <Button icon={<DownOutlined />} size="small" disabled={index === rules.length - 1} onClick={() => moveDown(index)}>
            下移
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => showModal()}>新增规则</Button>
        {rules.length > 1 && (
          <Button style={{ marginLeft: 16 }} type="default" icon={<SaveOutlined />} onClick={saveOrder}>保存顺序</Button>
        )}
      </div>
      <Table
        dataSource={rules}
        columns={columns}
        rowKey="id"
        pagination={false}
        bordered
        size="middle"
      />

      {/* 编辑/新增规则弹窗 */}
      <Modal
        title={editingRule ? '编辑规则' : '新增规则'}
        visible={isModalVisible}
        onCancel={handleCancel}
        footer={[
          <Button key="back" onClick={handleCancel}>取消</Button>,
          <Button key="submit" type="primary" onClick={handleSave}>
            保存
          </Button>,
        ]}
        width={800}
      >
        <Form form={expandForm} layout="vertical">
          <Form.Item name="name" label="规则名称" rules={[{ required: true, message: '请输入规则名称' }]}>
            <Input placeholder="请输入规则名称" />
          </Form.Item>
          <Form.Item name="type" label="规则类型" rules={[{ required: true, message: '请输入规则类型' }]}>
            <Input placeholder="请输入规则类型，如 accumulation" />
          </Form.Item>
          <Form.Item name="description" label="规则描述">
            <Input.TextArea placeholder="请输入规则描述" rows={3} />
          </Form.Item>
          <Form.Item name="expression" label="规则表达式" rules={[{ required: true, message: '请输入规则表达式' }]}>
            <Input.TextArea placeholder="如：context.accumulated_sick_leave_days <= 7" rows={2} />
          </Form.Item>
          <Form.Item name="message" label="提示信息" rules={[{ required: true, message: '请输入提示信息' }]}>
            <Input.TextArea placeholder="如：门诊病假天数已超过年度限制的7天。" rows={2} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default RuleExecutionList;