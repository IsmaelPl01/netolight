import PropTypes from 'prop-types';
import { useEffect } from 'react';

import { CacheProvider } from '@emotion/react';
import createCache from '@emotion/cache';

import rtlPlugin from 'stylis-plugin-rtl';

import useConfig from 'hooks/useConfig';

const RTLLayout = ({ children }) => {
  const { themeDirection } = useConfig();

  useEffect(() => {
    document.dir = themeDirection;
  }, [themeDirection]);

  const cacheRtl = createCache({
    key: themeDirection === 'rtl' ? 'rtl' : 'css',
    prepend: true,
    stylisPlugins: themeDirection === 'rtl' ? [rtlPlugin] : []
  });

  return <CacheProvider value={cacheRtl}>{children}</CacheProvider>;
};

RTLLayout.propTypes = {
  children: PropTypes.node
};

export default RTLLayout;
