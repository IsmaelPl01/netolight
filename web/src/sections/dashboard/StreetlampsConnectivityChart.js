import PropTypes from 'prop-types';
import { useEffect, useState } from 'react';
import { useIntl } from 'react-intl';

import { useTheme } from '@mui/material/styles';

import ReactApexChart from 'react-apexcharts';

import useConfig from 'hooks/useConfig';

const ActiveStreetlampChart = ({ series }) => {
  const theme = useTheme();
  const intl = useIntl();
  const { mode } = useConfig();

  const { primary } = theme.palette.text;
  const line = theme.palette.divider;
  const grey200 = theme.palette.grey[200];
  const backColor = theme.palette.background.paper;

  const pieChartOptions = {
    chart: {
      type: 'pie'
    },
    labels: [
      intl.formatMessage({ id: 'connectivity-chart.legend.offline' }),
      intl.formatMessage({ id: 'connectivity-chart.legend.never-seen' }),
      intl.formatMessage({ id: 'connectivity-chart.legend.online' })
    ],
    legend: {
      show: true,
      fontFamily: `'Roboto', sans-serif`,
      offsetX: 10,
      offsetY: 10,
      labels: {
        useSeriesColors: false
      },
      markers: {
        width: 12,
        height: 12,
        radius: 5
      },
      itemMargin: {
        horizontal: 25,
        vertical: 4
      }
    },
    responsive: [
      {
        breakpoint: 450,
        chart: {
          width: 280,
          height: 280
        },
        options: {
          legend: {
            show: false,
            position: 'bottom'
          }
        }
      }
    ]
  };

  const [options, setOptions] = useState(pieChartOptions);

  const secondary = theme.palette.primary[700];
  const primaryMain = theme.palette.primary.main;
  const successDark = theme.palette.success.main;
  const error = theme.palette.error.main;
  const orangeDark = theme.palette.warning.main;

  useEffect(() => {
    setOptions((prevState) => ({
      ...prevState,
      colors: [error, orangeDark, successDark],
      xaxis: {
        labels: {
          style: {
            colors: [primary, primary, primary, primary, primary, primary, primary]
          }
        }
      },
      yaxis: {
        labels: {
          style: {
            colors: [primary]
          }
        }
      },
      grid: {
        borderColor: line
      },
      legend: {
        labels: {
          colors: 'grey.500'
        }
      },
      stroke: {
        colors: [backColor]
      }
    }));
  }, [mode, primary, line, grey200, backColor, secondary, primaryMain, successDark, error, orangeDark, series]);

  return <ReactApexChart options={options} series={series} type="pie" height="100%" />;
};

ActiveStreetlampChart.propTypes = {
  series: PropTypes.array
};

export default ActiveStreetlampChart;
