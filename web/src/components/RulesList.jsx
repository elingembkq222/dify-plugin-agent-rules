import { useState, useEffect } from 'react';
import { Table, Button, Space, Tag, message } from 'antd';
import { EditOutlined, DeleteOutlined, ReloadOutlined, CopyOutlined } from '@ant-design/icons';
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

  const handleCopy = (record) => {
    try {
      const jsonString = JSON.stringify(record, null, 2);
      navigator.clipboard.writeText(jsonString);
      message.success('规则JSON已复制到剪贴板');
    } catch (error) {
      message.error('复制失败');
      console.error('复制失败:', error);
    }
  };

  const columns = [
    {
      title: '规则集ID',
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
      title: '目标',
      dataIndex: 'target',
      key: 'target',
      ellipsis: true,
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
    },
    {
      title: '规则数量',
      key: 'ruleCount',
      render: (_, record) => record.rules?.length || 0,
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      ellipsis: true,
    },
    {
      title: '更新时间',
      dataIndex: 'updated_at',
      key: 'updated_at',
      ellipsis: true,
    },
    {title: '操作',
      key: 'action',
      width: 330,
      render: (_, record) => (
        <Space size="small">
          <Button
            type="primary"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Button
            danger
            size="small"
            icon={<DeleteOutlined />}
            onClick={() => handleDelete(record.id)}
          >
            删除
          </Button>
          <Button
            size="small"
            icon={<CopyOutlined />}
            onClick={() => handleCopy(record)}
          >
            复制
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
        scroll={{ x: 1350 }}
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