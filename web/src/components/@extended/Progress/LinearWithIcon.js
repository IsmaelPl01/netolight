import PropTypes from 'prop-types';

import { Box, LinearProgress } from '@mui/material';

export default function LinearWithIcon({ icon, value, ...others }) {
  return (
    <Box sx={{ display: 'flex', alignItems: 'center' }}>
      <Box sx={{ width: '100%', mr: 1 }}>
        <LinearProgress variant="determinate" value={value} {...others} />
      </Box>
      <Box sx={{ minWidth: 35 }}>{icon}</Box>
    </Box>
  );
}

LinearWithIcon.propTypes = {
  icon: PropTypes.node,
  value: PropTypes.number
};
