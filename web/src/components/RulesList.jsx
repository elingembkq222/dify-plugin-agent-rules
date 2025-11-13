import { useState, useEffect } from 'react';
import { Table, Button, Space, Tag, message } from 'antd';
import { EditOutlined, DeleteOutlined, ReloadOutlined } from '@ant-design/icons';
import { listRules } from '../api';

const RulesList = () => {
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchRules = () => {
    setLoading(true);
    listRules()
      .then(response => {
        setRules(response.data.rules);
        message.success('规则列表加载成功');
      })
      .catch(error => {
        message.error('加载规则失败');
        console.error('加载规则失败:', error);
      })
      .finally(() => {
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchRules();
  }, []);

  const handleDelete = (ruleId) => {
    // TODO: 实现删除功能
    message.info('删除规则功能待实现');
  };

  const handleEdit = (rule) => {
    // TODO: 实现编辑功能
    message.info('编辑规则功能待实现');
  };

  const columns = [
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
      render: (type) => <Tag color={type === 'function' ? 'blue' : 'green'}>{type}</Tag>,
    },
    {
      title: '目标',
      dataIndex: 'target',
      key: 'target',
      ellipsis: true,
    },
    {
      title: '规则函数',
      dataIndex: 'function',
      key: 'function',
      ellipsis: true,
      render: (func) => <pre className="rule-function">{func}</pre>,
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space size="middle">
          <Button
            type="primary"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Button
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDelete(record.id)}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div className="rules-list">
      <div className="rules-list-header">
        <Button
          type="primary"
          icon={<ReloadOutlined />}
          onClick={fetchRules}
          loading={loading}
          className="reload-btn"
        >
          刷新列表
        </Button>
      </div>

      <Table
        columns={columns}
        dataSource={rules}
        rowKey="id"
        loading={loading}
        bordered
        size="middle"
        pagination={{
          pageSize: 10,
          showSizeChanger: true,
          showTotal: (total) => `共 ${total} 条规则`,
        }}
      />
    </div>
  );
};

export default RulesList;