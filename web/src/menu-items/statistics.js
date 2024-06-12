import { FormattedMessage } from 'react-intl';

import { BarChartOutlined, DashboardOutlined } from '@ant-design/icons';

const statistics = {
  id: 'group-statistics',
  title: <FormattedMessage id="drawer.group.statistics" />,
  type: 'group',
  children: [
    {
      id: 'dashboard',
      title: <FormattedMessage id="dashboard.drawer.label" />,
      type: 'item',
      icon: DashboardOutlined,
      url: '/dashboard',
      root: 'statistics'
    },
    {
      id: 'energyConsumption',
      title: <FormattedMessage id="energy-consumption.drawer.label" />,
      type: 'item',
      icon: BarChartOutlined,
      url: '/energyconsumption'
    }
  ]
};

export default statistics;
