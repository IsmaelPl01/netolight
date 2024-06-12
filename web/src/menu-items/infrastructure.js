import { FormattedMessage } from 'react-intl';
import { BulbOutlined, WifiOutlined } from '@ant-design/icons';

const infrastructure = {
  id: 'group-infrastructure',
  title: <FormattedMessage id="drawer.group.infrastructure" />,
  type: 'group',
  children: [
    {
      id: 'gateways',
      title: <FormattedMessage id="gateway.drawer.label" />,
      type: 'item',
      icon: WifiOutlined,
      url: '/gateways'
    },
    {
      id: 'streetlamps',
      title: <FormattedMessage id="streetlamp.drawer.label" />,
      type: 'item',
      icon: BulbOutlined,
      url: '/streetlamps'
    }
  ]
};

export default infrastructure;
