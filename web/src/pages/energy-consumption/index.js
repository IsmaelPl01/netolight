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
      month: '2023-06',
      consumption: 0.0,
      cost: 0.0,
      co2: 0.0
    },
    lastMonth: {
      month: '2023-05',
      consumption: 0.0,
      cost: 0.0,
      co2: 0.0
    },
    sameMonthLastYear: {
      month: '2022-06',
      consumption: 0.0,
      cost: 0.0,
      co2: 0.0
    },
    lastYear: {
      month: '2022-01',
      consumption: 0.0,
      cost: 0.0,
      co2: 0.0
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
