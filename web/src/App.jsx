import { Tabs, Card, Typography } from 'antd';
import 'antd/dist/reset.css';
import './App.css';
import RulesList from './components/RulesList';
import AddRule from './components/AddRule';
import ValidateRule from './components/ValidateRule';
import GenerateRule from './components/GenerateRule';

import { UnorderedListOutlined, PlusCircleOutlined, CheckCircleOutlined, TrademarkOutlined } from '@ant-design/icons';

const { Title } = Typography;

const App = () => {
  return (
    <div className="app-container">
      <div className="header">
        <Title level={1} className="title">
          <span role="img" aria-label="gear">⚙️</span> Rule Engine 管理控制台
        </Title>
        <p className="subtitle">管理和验证业务规则</p>
      </div>

      <Card className="main-card">
        <Tabs
          defaultActiveKey="1"
          items={[
            {
              key: '1',
              label: (
                <span>
                  <UnorderedListOutlined />
                  规则列表
                </span>
              ),
              children: <RulesList />,
            },
            {
              key: '2',
              label: (
                <span>
                  <PlusCircleOutlined />
                  添加规则
                </span>
              ),
              children: <AddRule />,
            },
            {
              key: '3',
              label: (
                <span>
                  <CheckCircleOutlined />
                  验证规则
                </span>
              ),
              children: <ValidateRule />,
            },
            { key: '4',
              label: (
                <span>
                  <TrademarkOutlined />
                  生成规则
                </span>
              ),
              children: <GenerateRule />,
            },

          ]}
        />
      </Card>
    </div>
  );
};

export default App;
