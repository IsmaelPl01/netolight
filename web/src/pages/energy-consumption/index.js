/* eslint-disable no-console */

import { useEffect, useState } from 'react';
import { useDispatch } from 'react-redux';

import { Grid } from '@mui/material';

import MainCard from 'components/MainCard';
import OverallConsumptionTable from 'sections/reports/energy-consumption/OverallConsumptionTable';
import OverallConsumptionChart from 'sections/reports/energy-consumption/OverallConsumptionChart';

import axios from 'utils/axios';

const OverallConsumption = () => {
  const dispatch = useDispatch();

  const [report, setReport] = useState({
    currentMonth: {
      month: '2024-06',
      consumption: 500.0,
      cost: 100.0,
      co2: 5.0
    },
    lastMonth: {
      month: '2024-05',
      consumption: 480.0,
      cost: 96.0,
      co2: 4.8
    },
    sameMonthLastYear: {
      month: '2023-06',
      consumption: 450.0,
      cost: 90.0,
      co2: 4.5
    },
    lastYear: {
      month: '2023-01',
      consumption: 420.0,
      cost: 84.0,
      co2: 4.2
    }
  });

  const fetchReport = () => {
    return async () => {
      try {
        const response = await axios.get(`/api/reports/energyconsumption`);
        setReport(response.data);
      } catch (error) {
        console.log(error);
      }
    };
  };

  useEffect(() => {
    dispatch(fetchReport());
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <MainCard title="Overall consumption">
      <Grid container spacing={3}>
        <Grid item xs={12} sm={6}>
          <OverallConsumptionTable report={report} />
        </Grid>
        <Grid item xs={12} sm={6}>
          <OverallConsumptionChart report={report} />
        </Grid>
      </Grid>
    </MainCard>
  );
};

const EnergyConsumption = () => {
  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <OverallConsumption />
      </Grid>
    </Grid>
  );
};

export default EnergyConsumption;
