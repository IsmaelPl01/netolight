import PropTypes from 'prop-types';
import { useIntl } from 'react-intl';
import { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';

import MuiBreadcrumbs from '@mui/material/Breadcrumbs';
import { useTheme } from '@mui/material/styles';
import { Divider, Grid, Typography } from '@mui/material';

import MainCard from '../MainCard';

import { ApartmentOutlined, HomeFilled, HomeOutlined } from '@ant-design/icons';

const Breadcrumbs = ({
  card,
  divider = true,
  icon,
  icons,
  maxItems,
  navigation,
  rightAlign,
  separator,
  title,
  titleBottom,
  sx,
  ...others
}) => {
  const intl = useIntl();
  const theme = useTheme();
  const location = useLocation();
  const [main, setMain] = useState();
  const [item, setItem] = useState();

  const iconSX = {
    marginRight: theme.spacing(0.75),
    marginTop: `-${theme.spacing(0.25)}`,
    width: '1rem',
    height: '1rem',
    color: theme.palette.secondary.main
  };

  const getCollapse = (menu) => {
    if (menu.children) {
      menu.children.filter((collapse) => {
        if (collapse.type && collapse.type === 'collapse') {
          getCollapse(collapse);
        } else if (collapse.type && collapse.type === 'item') {
          if (location.pathname === collapse.url) {
            setMain(menu);
            setItem(collapse);
          }
        }
        return false;
      });
    }
  };

  useEffect(() => {
    navigation?.items?.map((menu) => {
      if (menu.type && menu.type === 'group') {
        getCollapse(menu);
      }
      return false;
    });
  });

  const SeparatorIcon = separator;
  const separatorIcon = separator ? <SeparatorIcon style={{ fontSize: '0.75rem', marginTop: 2 }} /> : '/';

  let mainContent;
  let itemContent;
  let breadcrumbContent = <Typography />;
  let itemTitle = '';
  let CollapseIcon;
  let ItemIcon;

  if (main && main.type === 'collapse') {
    CollapseIcon = main.icon ? main.icon : ApartmentOutlined;
    mainContent = (
      <Typography component={Link} to={document.location.pathname} variant="h6" sx={{ textDecoration: 'none' }} color="textSecondary">
        {icons && <CollapseIcon style={iconSX} />}
        {main.title}
      </Typography>
    );
  }

  if (item && item.type === 'item') {
    itemTitle = item.title;

    ItemIcon = item.icon ? item.icon : ApartmentOutlined;
    itemContent = (
      <Typography variant="subtitle1" color="textPrimary">
        {icons && <ItemIcon style={iconSX} />}
        {itemTitle}
      </Typography>
    );

    const getMsgId = () => {
      if (['dashboard', 'energyConsumption'].includes(item.id)) return 'breadcrumb.statistics';
      else if (['dimmingProfile', 'dimmingCalendar'].includes(item.id)) return 'breadcrumb.control';
      else if (['gateways', 'streetlamps'].includes(item.id)) return 'breadcrumb.infrastructure';
      return '';
    };

    const msgId = getMsgId();

    if (item.breadcrumbs !== false) {
      breadcrumbContent = (
        <MainCard
          border={card}
          sx={card === false ? { mb: 3, bgcolor: 'transparent', ...sx } : { mb: 3, ...sx }}
          {...others}
          content={card}
          shadow="none"
        >
          <Grid
            container
            direction={rightAlign ? 'row' : 'column'}
            justifyContent={rightAlign ? 'space-between' : 'flex-start'}
            alignItems={rightAlign ? 'center' : 'flex-start'}
            spacing={1}
          >
            {title && !titleBottom && (
              <Grid item>
                <Typography variant="h2">{item.title}</Typography>
              </Grid>
            )}
            <Grid item>
              <MuiBreadcrumbs aria-label="breadcrumb" maxItems={maxItems || 8} separator={separatorIcon}>
                <Typography component={Link} to="/" color="textSecondary" variant="h6" sx={{ textDecoration: 'none' }}>
                  {icons && <HomeOutlined style={iconSX} />}
                  {icon && !icons && <HomeFilled style={{ ...iconSX, marginRight: 0 }} />}
                  {(!icon || icons) && intl.formatMessage({ id: msgId })}
                </Typography>
                {mainContent}
                {itemContent}
              </MuiBreadcrumbs>
            </Grid>
            {title && titleBottom && (
              <Grid item sx={{ mt: card === false ? 0.25 : 1 }}>
                <Typography variant="h2">{item.title}</Typography>
              </Grid>
            )}
          </Grid>
          {card === false && divider !== false && <Divider sx={{ mt: 2 }} />}
        </MainCard>
      );
    }
  }

  return breadcrumbContent;
};

Breadcrumbs.propTypes = {
  card: PropTypes.bool,
  divider: PropTypes.bool,
  icon: PropTypes.bool,
  icons: PropTypes.bool,
  maxItems: PropTypes.number,
  navigation: PropTypes.object,
  rightAlign: PropTypes.bool,
  separator: PropTypes.oneOfType([PropTypes.func, PropTypes.object]),
  title: PropTypes.bool,
  titleBottom: PropTypes.bool,
  sx: PropTypes.oneOfType([PropTypes.object, PropTypes.string])
};

export default Breadcrumbs;
