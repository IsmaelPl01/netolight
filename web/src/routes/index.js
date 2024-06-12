import { lazy } from 'react';
import { useRoutes } from 'react-router-dom';

import CommonLayout from 'layout/CommonLayout';
import Loadable from 'components/Loadable';
import LoginRoutes from './LoginRoutes';
import MainRoutes from './MainRoutes';

const PagesLanding = Loadable(lazy(() => import('pages/landing')));

export default function ThemeRoutes() {
  return useRoutes([
    {
      path: '/',
      element: <CommonLayout layout="landing" />,
      children: [
        {
          path: '/',
          element: <PagesLanding />
        }
      ]
    },
    LoginRoutes,
    MainRoutes
  ]);
}
