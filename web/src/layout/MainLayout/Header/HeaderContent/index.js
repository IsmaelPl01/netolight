import { useMemo } from 'react';

import { Box, useMediaQuery } from '@mui/material';

import useConfig from 'hooks/useConfig';
import Search from './Search';
import Profile from './Profile';
import Localization from './Localization';
import MobileSection from './MobileSection';

const HeaderContent = () => {
  const { i18n } = useConfig();

  const matchesXs = useMediaQuery((theme) => theme.breakpoints.down('md'));

  // eslint-disable-next-line react-hooks/exhaustive-deps
  const localization = useMemo(() => <Localization />, [i18n]);

  return (
    <>
      {!matchesXs && <Search />}
      {!matchesXs && localization}
      {matchesXs && <Box sx={{ width: '100%', ml: 1 }} />}
      {!matchesXs && <Profile />}
      {matchesXs && <MobileSection />}
    </>
  );
};

export default HeaderContent;
