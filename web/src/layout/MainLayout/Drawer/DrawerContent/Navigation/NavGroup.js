import PropTypes from 'prop-types';
import { useSelector } from 'react-redux';

import { useTheme } from '@mui/material/styles';
import { Box, List, Typography } from '@mui/material';

import NavItem from './NavItem';
import NavCollapse from './NavCollapse';

const NavGroup = ({ item }) => {
  const theme = useTheme();
  const menu = useSelector((state) => state.menu);
  const { drawerOpen } = menu;

  const navCollapse = item.children?.map((menuItem) => {
    switch (menuItem.type) {
      case 'collapse':
        return <NavCollapse key={menuItem.id} menu={menuItem} level={1} />;
      case 'item':
        return <NavItem key={menuItem.id} item={menuItem} level={1} />;
      default:
        return (
          <Typography key={menuItem.id} variant="h6" color="error" align="center">
            Fix - Group Collapse or Items
          </Typography>
        );
    }
  });

  return (
    <List
      subheader={
        item.title &&
        drawerOpen && (
          <Box sx={{ pl: 3, mb: 1.5 }}>
            <Typography variant="subtitle2" color={theme.palette.mode === 'dark' ? 'textSecondary' : 'text.secondary'}>
              {item.title}
            </Typography>
            {item.caption && (
              <Typography variant="caption" color="secondary">
                {item.caption}
              </Typography>
            )}
          </Box>
        )
      }
      sx={{ mt: drawerOpen && item.title ? 1.5 : 0, py: 0, zIndex: 0 }}
    >
      {navCollapse}
    </List>
  );
};

NavGroup.propTypes = {
  item: PropTypes.object
};

export default NavGroup;
