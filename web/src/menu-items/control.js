import { FormattedMessage } from 'react-intl';

import { CalendarOutlined, ProfileOutlined } from '@ant-design/icons';

const control = {
  id: 'group-control',
  title: <FormattedMessage id="drawer.group.control" />,
  type: 'group',
  children: [
    {
      id: 'dimmingProfile',
      title: <FormattedMessage id="dimmingProfile.drawer.label" />,
      type: 'item',
      icon: ProfileOutlined,
      url: '/dimmingprofiles'
    },
    {
      id: 'dimmingCalendar',
      title: <FormattedMessage id="dimmingCalendar.drawer.label" />,
      type: 'item',
      icon: CalendarOutlined,
      url: '/dimmingcalendar'
    }
  ]
};

export default control;
