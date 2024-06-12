import PropTypes from 'prop-types';
import { createContext, useEffect, useReducer } from 'react';

import humps from 'humps';
import jwtDecode from 'jwt-decode';

import { LOGIN, LOGOUT } from 'store/reducers/actions';
import authReducer from 'store/reducers/auth';

import Loader from 'components/Loader';
import axios from 'utils/axios';

const initialState = {
  isLoggedIn: false,
  isInitialized: false,
  user: null
};

const verifyToken = (serviceToken) => {
  if (!serviceToken) {
    return false;
  }
  const decoded = jwtDecode(serviceToken);
  return decoded.exp > Date.now() / 1000;
};

const setSession = (serviceToken) => {
  if (serviceToken) {
    localStorage.setItem('serviceToken', serviceToken);
    axios.defaults.headers.common.Authorization = `Bearer ${serviceToken}`;
  } else {
    localStorage.removeItem('serviceToken');
    delete axios.defaults.headers.common.Authorization;
  }
};

const JWTContext = createContext(null);

export const JWTProvider = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  useEffect(() => {
    const init = async () => {
      try {
        const serviceToken = window.localStorage.getItem('serviceToken');
        if (serviceToken && verifyToken(serviceToken)) {
          setSession(serviceToken);
          const response = await axios.get('/api/users/me');
          dispatch({
            type: LOGIN,
            payload: {
              isLoggedIn: true,
              user: humps.camelizeKeys(response.data)
            }
          });
        } else {
          dispatch({
            type: LOGOUT
          });
        }
      } catch (err) {
        console.error(err);
        dispatch({
          type: LOGOUT
        });
      }
    };

    init();
  }, []);

  const login = async (username, password) => {
    const form = new FormData();
    form.append('grant_type', 'password');
    form.append('username', username);
    form.append('password', password);
    const tresp = await axios.post('http://localhost:5000/api/token', form);
    setSession(tresp.data.access_token);
    const uresp = await axios.get('/api/users/me');
    dispatch({
      type: LOGIN,
      payload: {
        isLoggedIn: true,
        user: humps.camelizeKeys(uresp.data)
      }
    });
  };

  const logout = () => {
    setSession(null);
    dispatch({ type: LOGOUT });
  };

  const resetPassword = async () => {};

  const updateProfile = () => {};

  if (state.isInitialized !== undefined && !state.isInitialized) {
    return <Loader />;
  }

  return <JWTContext.Provider value={{ ...state, login, logout, resetPassword, updateProfile }}>{children}</JWTContext.Provider>;
};

JWTProvider.propTypes = {
  children: PropTypes.node
};

export default JWTContext;
