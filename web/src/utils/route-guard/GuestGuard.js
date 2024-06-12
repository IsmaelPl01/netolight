import PropTypes from 'prop-types';
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

import config from 'config';
import useAuth from 'hooks/useAuth';

const GuestGuard = ({ children }) => {
  const { isLoggedIn } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (isLoggedIn) {
      navigate(config.defaultPath, { replace: true });
    }
  }, [isLoggedIn, navigate]);

  return children;
};

GuestGuard.propTypes = {
  children: PropTypes.node
};

export default GuestGuard;
