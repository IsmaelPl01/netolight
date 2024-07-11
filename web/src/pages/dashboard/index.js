/* eslint-disable no-unused-vars */
/* eslint-disable no-console */

import humps from 'humps';
import moment from 'moment';
import 'moment/locale/es';

import { useEffect, useState } from 'react';
import { useDispatch } from 'react-redux';
import { useIntl } from 'react-intl';

import { Box, Grid, Stack, ToggleButton, ToggleButtonGroup, Typography, CircularProgress } from '@mui/material';

import { useTheme } from '@mui/material/styles';

import { BulbOutlined, MonitorOutlined, ThunderboltOutlined } from '@ant-design/icons';

import EnergyReportCard from 'components/cards/statistics/EnergyReportCard';
import StreetlampsConnectivityChart from 'sections/dashboard/StreetlampsConnectivityChart';
import StreetlampsAlarmsChart from 'sections/dashboard/StreetlampsAlarmsChart';
import StreetlampsLifeSpanChart from 'sections/dashboard/StreetlampsLifeSpanChart';
import StreetlampsEnergyOverviewChart from 'sections/dashboard/StreetlampsEnergyOverviewChart';
import StreetlampsMap from 'sections/dashboard/StreetlampsMap';
import MainCard from 'components/MainCard';

import axios from 'utils/axios';

const LoadingIndicator = () => {
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        height: 202
      }}
    >
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'row',
          alignItems: 'center',
          height: '100%'
        }}
      >
        <CircularProgress />
      </Box>
    </Box>
  );
};

const initialEnergyOverview = {
  consumption: {
    totalInKw: 500.0,
    avgInWatts: 20.83
  },
  savings: {
    percentage: 15.0,
    avgInWatts: 3.125
  },
  dimmingSavings: {
    percentage: 10.0,
    avgInWatts: 2.083
  },
  co2Savings: {
    totalInTon: 1.5,
    avgInTon: 0.0625
  }
};

const initialState = {
  connectivitySeries: [10, 5, 85],
  alarmsSeries: [1, 2, 3],
  lifeSpanSeries: [50, 30, 15, 5],
  energyOverview: {
    today: initialEnergyOverview,
    yesterday: initialEnergyOverview,
    lastWeek: initialEnergyOverview,
    lastMonth: initialEnergyOverview,
    mtdDaily: Array.from({ length: 30 }, (_, i) => ({
      day: `2024-06-${i + 1}`,
      consumption: Math.random() * 100 + 400,
      savings: Math.random() * 15 + 5,
      dimmingSavings: Math.random() * 10 + 5,
      co2Savings: Math.random() * 1 + 0.5
    })),
    mtdWeekly: Array.from({ length: 4 }, (_, i) => ({
      week: `Week ${i + 1}`,
      consumption: Math.random() * 100 + 400,
      savings: Math.random() * 15 + 5,
      dimmingSavings: Math.random() * 10 + 5,
      co2Savings: Math.random() * 1 + 0.5
    })),
    ytdMonthly: Array.from({ length: 12 }, (_, i) => ({
      month: `2024-${i + 1 < 10 ? `0${i + 1}` : i + 1}`,
      consumption: Math.random() * 100 + 400,
      savings: Math.random() * 15 + 5,
      dimmingSavings: Math.random() * 10 + 5,
      co2Savings: Math.random() * 1 + 0.5
    }))
  },
  geoStates: [
    {
      id: 1,
      name: 'Streetlamp 1',
      lat: 18.554172,
      lon: -69.928796,
      status: 'active'
    },
    {
      id: 2,
      name: 'Streetlamp 2',
      lat: 18.554173,
      lon: -69.928797,
      status: 'inactive'
    }
  ]
};

const Dashboard = () => {
  const theme = useTheme();
  const dispatch = useDispatch();
  const intl = useIntl();
  const [status, setStatus] = useState('loading');
  const [state, setState] = useState(initialState);
  const [slot, setSlot] = useState('lastWeek');

  const mkRangeLabel = (slot) => {
    moment.locale(intl.locale);
    const fmt = (d) => d.format('MMMM Do YYYY');
    const d = moment();
    if (slot === 'today') return fmt(d);
    if (slot === 'yesterday') return fmt(d.subtract(1, 'days'));
    if (slot === 'lastWeek') {
      const i = intl.locale === 'es' ? 1 : 0;
      const r = d.subtract(1, 'weeks');
      const t0 = r.weekday(0).clone().subtract(i, 'days');
      const t1 = r.weekday(6).subtract(i, 'days');
      return `${fmt(t0)} / ${fmt(t1)}`;
    }
    if (slot === 'lastMonth') return d.subtract(1, 'month').format('MMMM');
  };

  const handleChange = (event, newAlignment) => {
    if (newAlignment) setSlot(newAlignment);
  };

  const fetchState = () => {
    return async () => {
      try {
        setStatus('loading');
        const response = await axios.get('/api/dashboards/me');
        const data = humps.camelizeKeys(response.data);
        const connectivitySeries = [data.connectivity.inactive, data.connectivity.neverSeen, data.connectivity.active];
        const alarmsSeries = [data.alarms.critical, data.alarms.major, data.alarms.minor];
        const lifeSpanSeries = [
          data.lifeSpan.ninetyOneHundred,
          data.lifeSpan.seventyNinety,
          data.lifeSpan.fiftySeventy,
          data.lifeSpan.zeroTen
        ];
        const energyOverview = {
          today: data.todayEnergy,
          yesterday: data.yesterdayEnergy,
          lastWeek: data.lastWeekEnergy,
          lastMonth: data.lastMonthEnergy,
          mtdDaily: data.mtdDailyEnergy,
          mtdWeekly: data.mtdWeeklyEnergy,
          ytdMonthly: data.ytdMonthlyEnergy
        };
        setState({
          connectivitySeries: connectivitySeries,
          alarmsSeries: alarmsSeries,
          lifeSpanSeries: lifeSpanSeries,
          energyOverview: energyOverview,
          geoStates: data.geoStates
        });
        setStatus('idle');
      } catch (error) {
        setStatus('error');
        console.log(error);
      }
    };
  };

  useEffect(() => {
    dispatch(fetchState());
  }, [dispatch, intl.locale]);

  return (
    <Grid container rowSpacing={4.5} columnSpacing={2.75}>
      <Grid item xs={12} sm={6} lg={4}>
        <Grid container alignItems="center" justifyContent="space-between">
          <Grid item>
            <Typography variant="h5">{intl.formatMessage({ id: 'dashboard.connectivity-chart.title' })}</Typography>
          </Grid>
        </Grid>
        <MainCard sx={{ mt: 1.5, height: '185px' }}>
          {status === 'loading' ? <LoadingIndicator /> : <StreetlampsConnectivityChart series={state.connectivitySeries} />}
        </MainCard>
      </Grid>
      <Grid item xs={12} sm={6} lg={4}>
        <Grid container alignItems="center" justifyContent="space-between">
          <Grid item>
            <Typography variant="h5">{intl.formatMessage({ id: 'dashboard.alarms-chart.title' })}</Typography>
          </Grid>
        </Grid>
        <MainCard sx={{ mt: 1.5, height: '185px' }}>
          {status === 'loading' ? <LoadingIndicator /> : <StreetlampsAlarmsChart series={state.alarmsSeries} />}
        </MainCard>
      </Grid>
      <Grid item xs={12} sm={6} lg={4}>
        <Grid container alignItems="center" justifyContent="space-between">
          <Grid item>
            <Typography variant="h5">{intl.formatMessage({ id: 'dashboard.lifespan-chart.title' })}</Typography>
          </Grid>
        </Grid>
        <MainCard sx={{ mt: 1.5, height: '185px' }}>
          {status === 'loading' ? <LoadingIndicator /> : <StreetlampsLifeSpanChart series={state.lifeSpanSeries} />}
        </MainCard>
      </Grid>

      <Grid item xs={12} md={12} lg={12}>
        <Grid container alignItems="center" justifyContent="space-between">
          <Grid item>
            <Typography variant="h5">{intl.formatMessage({ id: 'dashboard.energy-overview.title' })}</Typography>
          </Grid>
        </Grid>
        <MainCard content={false} sx={{ mt: 1.5 }}>
          <Grid item>
            <Grid container>
              <Grid item xs={12} sm={6}>
                <Stack sx={{ ml: 2, mt: 3 }} alignItems={{ xs: 'center', sm: 'flex-start' }}>
                  <Typography color="textSecondary" sx={{ display: 'block' }}>
                    {mkRangeLabel(slot)}
                  </Typography>
                </Stack>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Stack
                  direction="row"
                  spacing={1}
                  alignItems="center"
                  justifyContent={{ xs: 'center', sm: 'flex-end' }}
                  sx={{ mt: 3, mr: 2 }}
                >
                  <ToggleButtonGroup exclusive onChange={handleChange} size="small" value={slot}>
                    <ToggleButton disabled={slot === 'today'} value="today" sx={{ px: 2, py: 0.5 }}>
                      {intl.formatMessage({ id: 'dashboard.energy-overview.button.today' })}
                    </ToggleButton>
                    <ToggleButton disabled={slot === 'yesterday'} value="yesterday" sx={{ px: 2, py: 0.5 }}>
                      {intl.formatMessage({ id: 'dashboard.energy-overview.button.yesterday' })}
                    </ToggleButton>
                    <ToggleButton disabled={slot === 'lastWeek'} value="lastWeek" sx={{ px: 2, py: 0.5 }}>
                      {intl.formatMessage({ id: 'dashboard.energy-overview.button.last-week' })}
                    </ToggleButton>
                    <ToggleButton disabled={slot === 'lastMonth'} value="lastMonth" sx={{ px: 2, py: 0.5 }}>
                      {intl.formatMessage({ id: 'dashboard.energy-overview.button.last-month' })}
                    </ToggleButton>
                  </ToggleButtonGroup>
                </Stack>
              </Grid>
            </Grid>
          </Grid>
          <Box sx={{ pt: 3, ml: 2, mr: 2, mb: 2 }}>
            <Grid container>
              <Grid item xs={12} sm={6} lg={3}>
                {status === 'loading' ? (
                  <LoadingIndicator />
                ) : (
                  <EnergyReportCard
                    primary={`${state.energyOverview[slot].consumption.totalInKw} kW·h`}
                    secondary={intl.formatMessage({ id: 'dashboard.energy-overview.consumption.title' })}
                    color={theme.palette.error.main}
                    iconPrimary={ThunderboltOutlined}
                  />
                )}
              </Grid>
              <Grid item xs={12} sm={6} lg={3}>
                {status === 'loading' ? (
                  <LoadingIndicator />
                ) : (
                  <EnergyReportCard
                    primary={`${state.energyOverview[slot].savings.percentage} %`}
                    secondary={intl.formatMessage({ id: 'dashboard.energy-overview.savings.title' })}
                    color={theme.palette.success.main}
                    iconPrimary={BulbOutlined}
                  />
                )}
              </Grid>
              <Grid item xs={12} sm={6} lg={3}>
                {status === 'loading' ? (
                  <LoadingIndicator />
                ) : (
                  <EnergyReportCard
                    primary={`${state.energyOverview[slot].dimmingSavings.percentage} %`}
                    secondary={intl.formatMessage({ id: 'dashboard.energy-overview.dimming-savings.title' })}
                    color={theme.palette.warning.main}
                    iconPrimary={BulbOutlined}
                  />
                )}
              </Grid>
              <Grid item xs={12} sm={6} lg={3}>
                {status === 'loading' ? (
                  <LoadingIndicator />
                ) : (
                  <EnergyReportCard
                    primary={`${state.energyOverview[slot].co2Savings.totalInTon} t`}
                    secondary={intl.formatMessage({ id: 'dashboard.energy-overview.co2-savings.title' })}
                    color={theme.palette.success.main}
                    iconPrimary={MonitorOutlined}
                  />
                )}
              </Grid>
              <Grid item xs={12} sm={12} lg={12}>
                <StreetlampsEnergyOverviewChart
                  slot={slot}
                  mtdDaily={state.energyOverview.mtdDaily}
                  mtdWeekly={state.energyOverview.mtdWeekly}
                  ytdMonthly={state.energyOverview.ytdMonthly}
                />
              </Grid>
            </Grid>
          </Box>
        </MainCard>
      </Grid>

      <Grid item xs={12} md={12} lg={12}>
        <Grid container alignItems="center" justifyContent="space-between">
          <Grid item>
            <Typography variant="h5">{intl.formatMessage({ id: 'dashboard.map-view.title' })}</Typography>
          </Grid>
        </Grid>
        <Grid item xs={12} sm={12} lg={12} sx={{ mt: 1.5 }}>
          <StreetlampsMap streetlamps={state.geoStates} />
        </Grid>
      </Grid>
    </Grid>
  );
};

export default Dashboard;
