import PropTypes from 'prop-types';
import { useIntl } from 'react-intl';

import { Table, TableBody, TableCell, TableContainer, TableRow, TableHead } from '@mui/material';

const OverallConsumptionTable = ({ report }) => {
  const intl = useIntl();
  return (
    <TableContainer>
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell sx={{ pl: 3 }}></TableCell>
            <TableCell align="right">{intl.formatMessage({ id: 'energy-consumption.table.column.consumption.label' })}</TableCell>
            <TableCell align="right">{intl.formatMessage({ id: 'energy-consumption.table.column.cost.label' })}</TableCell>
            <TableCell align="right">{intl.formatMessage({ id: 'energy-consumption.table.column.co2.label' })}</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          <TableRow hover>
            <TableCell sx={{ pl: 3 }} component="th" scope="row">
              {intl.formatMessage({ id: 'energy-consumption.table.row.current-month.label' })}
            </TableCell>
            <TableCell align="right">{report.currentMonth.consumption}</TableCell>
            <TableCell align="right">{report.currentMonth.cost}</TableCell>
            <TableCell align="right">{report.currentMonth.co2}</TableCell>
          </TableRow>
          <TableRow hover>
            <TableCell sx={{ pl: 3 }} component="th" scope="row">
              {intl.formatMessage({ id: 'energy-consumption.table.row.last-month.label' })}
            </TableCell>
            <TableCell align="right">{report.lastMonth.consumption}</TableCell>
            <TableCell align="right">{report.lastMonth.cost}</TableCell>
            <TableCell align="right">{report.lastMonth.co2}</TableCell>
          </TableRow>
          <TableRow hover>
            <TableCell sx={{ pl: 3 }} component="th" scope="row">
              {intl.formatMessage({ id: 'energy-consumption.table.row.same-month-last-year.label' })}
            </TableCell>
            <TableCell align="right">{report.sameMonthLastYear.consumption}</TableCell>
            <TableCell align="right">{report.sameMonthLastYear.cost}</TableCell>
            <TableCell align="right">{report.sameMonthLastYear.co2}</TableCell>
          </TableRow>
          <TableRow hover>
            <TableCell sx={{ pl: 3 }} component="th" scope="row">
              {intl.formatMessage({ id: 'energy-consumption.table.row.last-year.label' })}
            </TableCell>
            <TableCell align="right"></TableCell>
            <TableCell align="right"></TableCell>
            <TableCell align="right"></TableCell>
          </TableRow>
          <TableRow hover>
            <TableCell sx={{ pl: 3 }} component="th" scope="row">
              {intl.formatMessage({ id: 'energy-consumption.table.row.monthly-avg.label' })}
            </TableCell>
            <TableCell align="right"></TableCell>
            <TableCell align="right"></TableCell>
            <TableCell align="right"></TableCell>
          </TableRow>
          <TableRow hover>
            <TableCell sx={{ pl: 3 }} component="th" scope="row">
              {intl.formatMessage({ id: 'energy-consumption.table.row.daily-avg.label' })}
            </TableCell>
            <TableCell align="right"></TableCell>
            <TableCell align="right"></TableCell>
            <TableCell align="right"></TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </TableContainer>
  );
};

OverallConsumptionTable.propTypes = {
  report: PropTypes.object
};

export default OverallConsumptionTable;
