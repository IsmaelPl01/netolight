import PropTypes from 'prop-types';
import { useEffect, useState, useMemo } from 'react';
import { useIntl } from 'react-intl';

import ReactApexChart from 'react-apexcharts';
import { useTheme } from '@mui/material/styles';

import useConfig from 'hooks/useConfig';

const mkColumnChartOptions = (cats) => ({
  chart: {
    type: 'bar',
    height: 300,
    toolbar: {
      show: false
    }
  },
  plotOptions: {
    bar: {
      columnWidth: '30%',
      borderRadius: 4
    }
  },
  dataLabels: {
    enabled: false
  },
  stroke: {
    show: true,
    width: 8,
    colors: ['transparent']
  },
  xaxis: {
    categories: cats
  },
  yaxis: {
    title: {
      text: ''
    }
  },
  fill: {
    opacity: 1
  },
  tooltip: {
    y: {
      formatter(val) {
        return `${val}`;
      }
    }
  },
  legend: {
    show: true,
    fontFamily: `'Public Sans', sans-serif`,
    offsetX: 10,
    offsetY: 10,
    labels: {
      useSeriesColors: false
    },
    markers: {
      width: 16,
      height: 16,
      radius: '50%',
      offsexX: 2,
      offsexY: 2
    },
    itemMargin: {
      horizontal: 15,
      vertical: 50
    }
  },
  responsive: [
    {
      breakpoint: 600,
      options: {
        yaxis: {
          show: false
        }
      }
    }
  ]
});

const OverallConsumptionChart = ({ report }) => {
  const theme = useTheme();
  const { mode, fontFamily } = useConfig();
  const intl = useIntl();

  const { primary, secondary } = theme.palette.text;
  const line = theme.palette.divider;

  const warning = theme.palette.warning.main;
  const primaryMain = theme.palette.primary.main;
  const secondaryMain = theme.palette.secondary.main;
  const successDark = theme.palette.success.dark;

  const cats = useMemo(() => [report.sameMonthLastYear.month, report.lastMonth.month, report.currentMonth.month], [report]);

  const series = useMemo(
    () => [
      {
        name: intl.formatMessage({ id: 'energy-consumption.chart.legend.consumption' }),
        data: [report.sameMonthLastYear.consumption, report.lastMonth.consumption, report.currentMonth.consumption]
      },
      {
        name: intl.formatMessage({ id: 'energy-consumption.chart.legend.cost' }),
        data: [report.sameMonthLastYear.cost, report.lastMonth.cost, report.currentMonth.cost]
      },
      {
        name: intl.formatMessage({ id: 'energy-consumption.chart.legend.co2' }),
        data: [report.sameMonthLastYear.co2, report.lastMonth.co2, report.currentMonth.co2]
      }
    ],
    [report, intl]
  );

  const [options, setOptions] = useState(mkColumnChartOptions(cats));

  useEffect(() => {
    setOptions((prevState) => ({
      ...prevState,
      colors: [warning, primaryMain, secondaryMain],
      xaxis: {
        categories: cats,
        labels: {
          style: {
            colors: [secondary, secondary, secondary, secondary, secondary, secondary]
          }
        }
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
        theme: mode === 'dark' ? 'dark' : 'light'
      },
      legend: {
        show: false,
        fontFamily,
        position: 'top',
        horizontalAlign: 'right',
        labels: {
          colors: 'grey.500'
        }
      }
    }));
  }, [mode, primary, secondary, line, warning, primaryMain, secondaryMain, successDark, fontFamily, report, cats, series]);

  return (
    <div id="chart">
      <ReactApexChart options={options} series={series} type="bar" height={300} />
    </div>
  );
};

OverallConsumptionChart.propTypes = {
  report: PropTypes.object
};

export default OverallConsumptionChart;
