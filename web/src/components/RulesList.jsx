import { useState, useEffect } from 'react';
import { Table, Button, Space, Tag, message, Collapse } from 'antd';
import { EditOutlined, DeleteOutlined, ReloadOutlined, CopyOutlined, UnorderedListOutlined } from '@ant-design/icons';
import { listRules, updateRule } from '../api';
import RuleExecutionList from './RuleExecutionList';

const { Panel } = Collapse;

const RulesList = () => {
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(false);
  const [expandedRuleId, setExpandedRuleId] = useState(null);

  const fetchRules = () => {
    setLoading(true);
    listRules()
      .then(response => {
        setRules(response.data.rulesets || response.data.rules || []);
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

  const handleViewExecutionList = (ruleId) => {
    if (expandedRuleId === ruleId) {
      setExpandedRuleId(null);
    } else {
      setExpandedRuleId(ruleId);
    }
  };

  const handleUpdateRule = (ruleSetId, ruleData) => {
    // 更新规则集信息
    const existingRuleSet = rules.find(r => r.id === ruleSetId);
    if (!existingRuleSet) return;
    const updatedRuleSet = { ...existingRuleSet, rules: ruleData };
    // 更新本地规则列表
    const updatedRules = rules.map(rule => rule.id === ruleSetId ? updatedRuleSet : rule);
    setRules(updatedRules);
    // 收起面板
    setExpandedRuleId(null);
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
    {
      title: '操作',
      key: 'action',
      width: 420,
      render: (_, record) => (
        <Space size="small">
          <Button
            type="primary"
            size="small"
            icon={<UnorderedListOutlined />}
            onClick={() => handleViewExecutionList(record.id)}
          >
            执行规则列表
          </Button>
          <Button
            type="default"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑规则集
          </Button>
          <Button
            type="default"
            size="small"
            icon={<CopyOutlined />}
            onClick={() => handleCopy(record)}
          >
            复制JSON
          </Button>
          <Button
            danger
            size="small"
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
    <div>
      <div style={{ marginBottom: 16 }}>
        <Button
          type="primary"
          icon={<ReloadOutlined />}
          onClick={fetchRules}
          loading={loading}
        >
          刷新规则列表
        </Button>
      </div>
      <Table
        dataSource={rules}
        columns={columns}
        rowKey="id"
        bordered
        size="middle"
        pagination={{ pageSize: 10 }}
      />

      {/* 展开面板显示规则执行列表 */}
      <div style={{ marginTop: 16 }}>
        {expandedRuleId && (
          <Collapse defaultActiveKey={[expandedRuleId]} ghost>
            <Panel
              header={`执行规则列表 - ${rules.find(r => r.id === expandedRuleId)?.name || expandedRuleId}`}
              key={expandedRuleId}
            >
              <RuleExecutionList
                ruleSet={rules.find(r => r.id === expandedRuleId)}
                onUpdate={handleUpdateRule}
              />
            </Panel>
          </Collapse>
        )}
      </div>
    </div>
  );
};

export default RulesList;