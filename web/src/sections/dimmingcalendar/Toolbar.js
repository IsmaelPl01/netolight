import PropTypes from 'prop-types';
import { useIntl } from 'react-intl';

import { useMediaQuery, Button, Grid, Stack, Typography } from '@mui/material';

import { format } from 'date-fns';
import { es, enUS } from 'date-fns/locale';

import IconButton from 'components/@extended/IconButton';

import { LeftOutlined, RightOutlined } from '@ant-design/icons';

const Toolbar = ({ date, onClickNext, onClickPrev, onClickToday, ...others }) => {
  const intl = useIntl();
  const matchDownSM = useMediaQuery((theme) => theme.breakpoints.down('sm'));
  return (
    <Grid alignItems="center" container justifyContent="space-between" spacing={matchDownSM ? 1 : 3} {...others} sx={{ pb: 3 }}>
      <Grid item>
        <Button variant="outlined" onClick={onClickToday} size={matchDownSM ? 'small' : 'medium'}>
          Today
        </Button>
      </Grid>
      <Grid item>
        <Stack direction="row" alignItems="center" spacing={matchDownSM ? 1 : 3}>
          <IconButton onClick={onClickPrev} size={matchDownSM ? 'small' : 'large'}>
            <LeftOutlined />
          </IconButton>
          <Typography variant={matchDownSM ? 'h5' : 'h3'} color="textPrimary">
            {format(date, 'MMMM yyyy', { locale: intl.locale == 'es' ? es : enUS })}
          </Typography>
          <IconButton onClick={onClickNext} size={matchDownSM ? 'small' : 'large'}>
            <RightOutlined />
          </IconButton>
        </Stack>
      </Grid>
    </Grid>
  );
};

Toolbar.propTypes = {
  date: PropTypes.object,
  onClickNext: PropTypes.func,
  onClickPrev: PropTypes.func,
  onClickToday: PropTypes.func
};

export default Toolbar;
