import PropTypes from 'prop-types';
import { Link } from 'react-router-dom';

import { ButtonBase } from '@mui/material';

import LogoMain from './LogoMain';
import LogoIcon from './LogoIcon';
import config from 'config';

const LogoSection = ({ reverse, isIcon, sx, to }) => (
  <ButtonBase disableRipple component={Link} to={!to ? config.defaultPath : to} sx={sx}>
    {isIcon ? <LogoIcon /> : <LogoMain reverse={reverse} />}
  </ButtonBase>
);

LogoSection.propTypes = {
  reverse: PropTypes.bool,
  isIcon: PropTypes.bool,
  sx: PropTypes.object,
  to: PropTypes.string
};

export default LogoSection;
