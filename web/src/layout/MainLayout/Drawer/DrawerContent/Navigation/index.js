import { useSelector } from 'react-redux';

import { Box, Typography } from '@mui/material';

import NavGroup from './NavGroup';
import menuItem from 'menu-items';

const Navigation = () => {
  const menu = useSelector((state) => state.menu);
  const { drawerOpen } = menu;

  const navGroups = menuItem.items.map((item) => {
    switch (item.type) {
      case 'group':
        return <NavGroup key={item.id} item={item} />;
      default:
        return (
          <Typography key={item.id} variant="h6" color="error" align="center">
            Fix - Navigation Group
          </Typography>
        );
    }
  });

  return <Box sx={{ pt: drawerOpen ? 2 : 0, '& > ul:first-of-type': { mt: 0 } }}>{navGroups}</Box>;
};

export default Navigation;
