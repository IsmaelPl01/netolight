import { lazy } from 'react';

import MainLayout from 'layout/MainLayout';
import CommonLayout from 'layout/CommonLayout';
import Loadable from 'components/Loadable';
import AuthGuard from 'utils/route-guard/AuthGuard';

const Dashboard = Loadable(lazy(() => import('pages/dashboard')));
const StreetlampEvents = Loadable(lazy(() => import('pages/streetlamp-events')));
const EnergyConsumptionReport = Loadable(lazy(() => import('pages/energy-consumption')));
const DimmingProfiles = Loadable(lazy(() => import('pages/dimmingprofiles')));
const DimmingCalendar = Loadable(lazy(() => import('pages/dimmingcalendar')));
const Streetlamps = Loadable(lazy(() => import('pages/streetlamps')));
const Gateways = Loadable(lazy(() => import('pages/gateways')));

const AuthLogin = Loadable(lazy(() => import('pages/auth/login')));
const AuthForgotPassword = Loadable(lazy(() => import('pages/auth/forgot-password')));
const AuthResetPassword = Loadable(lazy(() => import('pages/auth/reset-password')));
const AuthCheckMail = Loadable(lazy(() => import('pages/auth/check-mail')));
const AuthCodeVerification = Loadable(lazy(() => import('pages/auth/code-verification')));

const MainRoutes = {
  path: '/',
  children: [
    {
      path: '/',
      element: (
        <AuthGuard>
          <MainLayout />
        </AuthGuard>
      ),
      children: [
        {
          path: 'dashboard',
          element: <Dashboard />
        },
        {
          path: 'streetlampevents',
          element: <StreetlampEvents />
        },
        {
          path: 'dimmingprofiles',
          element: <DimmingProfiles />
        },
        {
          path: 'dimmingcalendar',
          element: <DimmingCalendar />
        },
        {
          path: 'energyconsumption',
          element: <EnergyConsumptionReport />
        },
        {
          path: 'gateways',
          element: <Gateways />
        },
        {
          path: 'streetlamps',
          element: <Streetlamps />
        }
      ]
    },
    {
      path: '/auth',
      element: <CommonLayout />,
      children: [
        {
          path: 'login',
          element: <AuthLogin />
        },
        {
          path: 'forgot-password',
          element: <AuthForgotPassword />
        },
        {
          path: 'reset-password',
          element: <AuthResetPassword />
        },
        {
          path: 'check-mail',
          element: <AuthCheckMail />
        },
        {
          path: 'code-verification',
          element: <AuthCodeVerification />
        }
      ]
    }
  ]
};

export default MainRoutes;
