import { useState, useEffect, useRef } from 'react';
import { Table, Button, Space, Tag, message, Collapse, Modal, Form, Input } from 'antd';
import { EditOutlined, DeleteOutlined, ReloadOutlined, CopyOutlined, UnorderedListOutlined } from '@ant-design/icons';
import { listRules, updateRule, deleteRule } from '../api';
import RuleExecutionList from './RuleExecutionList';

const { Panel } = Collapse;

const RulesList = () => {
  const [rules, setRules] = useState([]);
  const [filteredRules, setFilteredRules] = useState([]);
  const [loading, setLoading] = useState(false);
  const [expandedRuleId, setExpandedRuleId] = useState(null);
  const hasFetched = useRef(false);
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [editForm] = Form.useForm();
  const [editingRecord, setEditingRecord] = useState(null);
  const [searchForm] = Form.useForm();

  const filterData = (data, values) => {
    const id = (values.id || '').trim();
    const name = (values.name || '').trim();
    const target = (values.target || '').trim();
    const description = (values.description || '').trim();
    const created_at = (values.created_at || '').trim();
    const updated_at = (values.updated_at || '').trim();
    const includes = (a, b) => !b || (a || '').toLowerCase().includes(b.toLowerCase());
    return data.filter(rs => (
      includes(String(rs.id || ''), id) &&
      includes(String(rs.name || ''), name) &&
      includes(String(rs.target || ''), target) &&
      includes(String(rs.description || ''), description) &&
      includes(String(rs.created_at || ''), created_at) &&
      includes(String(rs.updated_at || ''), updated_at)
    ));
  };

  const fetchRules = (silent = false) => {
    setLoading(true);
    listRules()
      .then(response => {
        console.log('API响应:', response.data);
        const next = response.data.rulesets || response.data.rules || [];
        setRules(next);
        const values = searchForm.getFieldsValue();
        setFilteredRules(filterData(next, values));
        if (!silent) message.success('规则列表加载成功');
      })
      .catch(error => {
        console.error('加载规则失败 - 详细错误:', error);
        if (error.response) {
          console.error('响应状态:', error.response.status);
          console.error('响应数据:', error.response.data);
        }
        message.error(`加载规则失败: ${error.message || '未知错误'}`);
      })
      .finally(() => {
        setLoading(false);
      });
  };

  useEffect(() => {
    if (!hasFetched.current) {
      hasFetched.current = true;
      fetchRules();
    }
  }, []);

  const handleDelete = (ruleId) => {
    Modal.confirm({
      title: '确认删除规则集',
      content: '删除规则集将同时删除其执行规则，是否继续？',
      okText: '删除',
      okType: 'danger',
      cancelText: '取消',
      onOk: () => {
        deleteRule(ruleId)
          .then(() => {
            message.success('规则集删除成功');
            if (expandedRuleId === ruleId) setExpandedRuleId(null);
            fetchRules(true);
          })
          .catch(err => {
            message.error('规则集删除失败');
            console.error('删除失败:', err);
          });
      },
    });
  };

  const handleEdit = (rule) => {
    setEditingRecord(rule);
    editForm.setFieldsValue({
      target: rule.target,
      name: rule.name,
      description: rule.description,
      applies_when: JSON.stringify(rule.applies_when || [])
    });
    setEditModalVisible(true);
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

  const handleCopyId = (id) => {
    try {
      navigator.clipboard.writeText(id);
      message.success('规则集ID已复制');
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
    // 保持展开面板
    setExpandedRuleId(ruleSetId);
    // 静默刷新，同步服务端的 updated_at 等字段
    fetchRules(true);
  };

  const columns = [
    {
      title: '规则集ID',
      dataIndex: 'id',
      key: 'id',
      ellipsis: true,
      render: (id) => (
        <Button type="link" onClick={() => handleCopyId(id)}>{id}</Button>
      )
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
        <Form form={searchForm} layout="inline" style={{ marginTop: 12 }}>
          <Form.Item name="id" label="ID">
            <Input allowClear placeholder="按ID搜索" onChange={() => setFilteredRules(filterData(rules, searchForm.getFieldsValue()))} />
          </Form.Item>
          <Form.Item name="name" label="名称">
            <Input allowClear placeholder="按名称搜索" onChange={() => setFilteredRules(filterData(rules, searchForm.getFieldsValue()))} />
          </Form.Item>
          <Form.Item name="target" label="目标">
            <Input allowClear placeholder="按目标搜索" onChange={() => setFilteredRules(filterData(rules, searchForm.getFieldsValue()))} />
          </Form.Item>
          <Form.Item name="description" label="描述">
            <Input allowClear placeholder="按描述搜索" onChange={() => setFilteredRules(filterData(rules, searchForm.getFieldsValue()))} />
          </Form.Item>
          <Form.Item name="created_at" label="创建时间">
            <Input allowClear placeholder="按创建时间搜索" onChange={() => setFilteredRules(filterData(rules, searchForm.getFieldsValue()))} />
          </Form.Item>
          <Form.Item name="updated_at" label="更新时间">
            <Input allowClear placeholder="按更新时间搜索" onChange={() => setFilteredRules(filterData(rules, searchForm.getFieldsValue()))} />
          </Form.Item>
          <Form.Item>
            <Button onClick={() => { searchForm.resetFields(); setFilteredRules(rules); }}>清空过滤</Button>
          </Form.Item>
        </Form>
      </div>
      <Table
        dataSource={filteredRules}
        columns={columns}
        rowKey="id"
        bordered
        size="middle"
        pagination={{ pageSize: 10 }}
      />

      <Modal
        title="编辑规则集"
        visible={editModalVisible}
        onCancel={() => setEditModalVisible(false)}
        onOk={() => {
          editForm
            .validateFields()
            .then((values) => {
              let applies_when = [];
              if (typeof values.applies_when === 'string') {
                const t = values.applies_when.trim();
                if (t.length > 0) {
                  try { applies_when = JSON.parse(t); } catch { applies_when = []; }
                }
              }
              const payload = {
                id: editingRecord.id,
                target: values.target,
                name: values.name,
                description: values.description,
                applies_when
              };
              return updateRule(payload)
                .then(() => {
                  message.success('规则集已更新');
                  setEditModalVisible(false);
                  fetchRules(true);
                })
                .catch((err) => {
                  message.error('更新失败');
                  console.error('Edit ruleset failed:', err);
                });
            });
        }}
        okText="保存"
        cancelText="取消"
      >
        <Form form={editForm} layout="vertical">
          <Form.Item name="target" label="目标" rules={[{ required: true, message: '请输入目标' }]}> 
            <Input placeholder="例如：generic" />
          </Form.Item>
          <Form.Item name="name" label="规则集名称" rules={[{ required: true, message: '请输入规则集名称' }]}> 
            <Input placeholder="例如：一年内消费次数限制" />
          </Form.Item>
          <Form.Item name="description" label="描述"> 
            <Input.TextArea placeholder="例如：一年内消费不能低于三次" rows={3} />
          </Form.Item>
          <Form.Item name="applies_when" label="适用条件(JSON数组)"> 
            <Input.TextArea placeholder="[]" rows={3} />
          </Form.Item>
        </Form>
      </Modal>

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