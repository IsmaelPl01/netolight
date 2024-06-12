import PropTypes from 'prop-types';
import moment from 'moment';

import { useState, useEffect } from 'react';
import { useIntl } from 'react-intl';

import { useTheme } from '@mui/material/styles';

import useConfig from 'hooks/useConfig';

import ReactApexChart from 'react-apexcharts';

const areaChartOptions = {
  chart: {
    height: 355,
    type: 'area',
    toolbar: {
      show: false
    }
  },
  fill: {
    type: 'gradient',
    gradient: {
      shadeIntensity: 1,
      type: 'vertical',
      inverseColors: false,
      opacityFrom: 0.5,
      opacityTo: 0
    }
  },
  dataLabels: {
    enabled: false
  },
  stroke: {
    curve: 'straight',
    width: 1
  },
  grid: {
    show: true,
    borderColor: '#90A4AE',
    strokeDashArray: 0,
    position: 'back',
    xaxis: {
      lines: {
        show: true
      }
    },
    yaxis: {
      lines: {
        show: true
      }
    }
  },
  markers: {
    size: 5
  }
};

const StreetlampsEnergyOverviewChart = ({ slot, mtdDaily, mtdWeekly, ytdMonthly }) => {
  const theme = useTheme();
  const { mode } = useConfig();
  const intl = useIntl();

  const { primary, secondary } = theme.palette.text;
  const line = theme.palette.divider;

  const [options, setOptions] = useState(areaChartOptions);

  useEffect(() => {
    const mkCategories = () => {
      switch (slot) {
        case 'lastMonth':
          return ytdMonthly.map(({ ts }) => moment(ts).format('MMM'));
        case 'lastWeek':
          return mtdWeekly.map(({ ts }) => moment(ts).format('W'));
        case 'today':
        case 'yesterday':
          return mtdDaily.map(({ ts }) => moment(ts).format('ddd'));
      }
    };
    setOptions((prevState) => ({
      ...prevState,
      colors: [theme.palette.error.main, theme.palette.success.main, theme.palette.warning.main],
      xaxis: {
        categories: mkCategories(),
        labels: {
          style: {
            colors: [
              secondary,
              secondary,
              secondary,
              secondary,
              secondary,
              secondary,
              secondary,
              secondary,
              secondary,
              secondary,
              secondary,
              secondary
            ]
          }
        },
        axisBorder: {
          show: true,
          color: line
        },
        tickAmount: slot === 'lastMonth' ? 11 : 7
      },
      yaxis: {
        labels: {
          style: {
            colors: [secondary]
          }
        }
      },
      grid: {
        borderColor: line
      },
      tooltip: {
        theme: mode === 'dark' ? 'dark' : 'light',
        y: {
          formatter(val) {
            return `${val}`;
          }
        }
      }
    }));
  }, [mode, primary, secondary, line, theme, slot, mtdDaily, mtdWeekly, ytdMonthly]);

  const [series, setSeries] = useState([]);

  useEffect(() => {
    const mkSeries = (td) => {
      if (td.length === 0) return [];
      return [
        {
          name: intl.formatMessage({ id: 'dashboard.energy-overview.chart.consumption' }),
          data: td.map(({ consumption }) => consumption)
        },
        {
          name: intl.formatMessage({ id: 'dashboard.energy-overview.chart.savings' }),
          data: td.map(({ savings }) => savings)
        },
        {
          name: intl.formatMessage({ id: 'dashboard.energy-overview.chart.dimming-savings' }),
          data: td.map(({ dimmingSavings }) => dimmingSavings)
        }
      ];
    };
    switch (slot) {
      case 'lastMonth':
        setSeries(mkSeries(ytdMonthly));
        break;
      case 'lastWeek':
        setSeries(mkSeries(mtdWeekly));
        break;
      case 'today':
      case 'yesterday':
        setSeries(mkSeries(mtdDaily));
        break;
    }
  }, [slot, mtdDaily, mtdWeekly, ytdMonthly, intl]);

  return <ReactApexChart options={options} series={series} type="area" height={355} />;
};

StreetlampsEnergyOverviewChart.propTypes = {
  slot: PropTypes.string,
  mtdDaily: PropTypes.array,
  mtdWeekly: PropTypes.array,
  ytdMonthly: PropTypes.array
};

export default StreetlampsEnergyOverviewChart;
