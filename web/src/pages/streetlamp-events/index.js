import PropTypes from 'prop-types';
import { useIntl } from 'react-intl';
import { useEffect, useMemo, useState, Fragment } from 'react';
import { useDispatch } from 'react-redux';
import { useFilters, useExpanded, useGlobalFilter } from 'react-table';
import { useRowSelect, useSortBy, useTable, usePagination } from 'react-table';

import LinearProgress from '@mui/material/LinearProgress';
import { alpha, useTheme } from '@mui/material/styles';
import { Stack, useMediaQuery } from '@mui/material';
import { Table, TableBody, TableCell, TableHead, TableRow } from '@mui/material';

import MainCard from 'components/MainCard';
import ScrollX from 'components/ScrollX';
import { renderFilterTypes, GlobalFilter } from 'utils/react-table';
import { HeaderSort, IndeterminateCheckbox } from 'components/third-party/ReactTable';
import { SortingSelect, TablePagination, TableRowSelection } from 'components/third-party/ReactTable';
import axios from 'utils/axios';

function ReactTable({ columns, getHeaderProps }) {
  const theme = useTheme();
  const dispatch = useDispatch();
  const matchDownSM = useMediaQuery(theme.breakpoints.down('sm'));

  const filterTypes = useMemo(() => renderFilterTypes, []);
  const sortBy = { id: 'id', desc: false };

  const [pageIndex, setPageIndex] = useState(0);
  const [deviceEvents, setDeviceEvents] = useState({ total: 0, data: [] });
  const [loading, setLoading] = useState('idle');

  const fetchDeviceEvents = (skip, limit) => {
    return async () => {
      try {
        setLoading('pending');
        const response = await axios.get(`/api/device_events/?skip=${skip}&limit=${limit}`);
        setDeviceEvents(response.data);
        setLoading('idle');
      } catch (error) {
        console.log(error);
      }
    };
  };

  const gotoPage = async (pageIndex) => {
    dispatch(fetchDeviceEvents(pageIndex * pageSize, pageSize));
    setPageIndex(pageIndex);
  };

  const handlePageSizeChange = (pageSize) => {
    dispatch(fetchDeviceEvents(pageIndex, pageSize));
    setPageSize(pageSize);
  };

  const columnWithActions = useMemo(
    () => {
      return columns.concat([]);
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [theme]
  );

  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    prepareRow,
    allColumns,
    // @ts-ignore
    page,
    // @ts-ignore
    setPageSize,
    // @ts-ignore
    state: { globalFilter, selectedRowIds, pageSize },
    // @ts-ignore
    setGlobalFilter,
    // @ts-ignore
    setSortBy
  } = useTable(
    {
      columns: columnWithActions,
      data: deviceEvents.data,
      // @ts-ignore
      filterTypes,
      // @ts-ignore
      initialState: { pageSize: 5, hiddenColumns: [], sortBy: [sortBy] },
      manualPagination: true
    },
    useGlobalFilter,
    useFilters,
    useSortBy,
    useExpanded,
    usePagination,
    useRowSelect
  );

  useEffect(() => {
    dispatch(fetchDeviceEvents(pageIndex * pageSize, pageSize));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <>
      <TableRowSelection selected={Object.keys(selectedRowIds).length} />
      <Stack spacing={3}>
        <Stack
          direction={matchDownSM ? 'column' : 'row'}
          spacing={1}
          justifyContent="space-between"
          alignItems="center"
          sx={{ p: 3, pb: 0 }}
        >
          <GlobalFilter globalFilter={globalFilter} setGlobalFilter={setGlobalFilter} size="small" />
          <Stack direction={matchDownSM ? 'column' : 'row'} alignItems="center" spacing={1}>
            <SortingSelect sortBy={sortBy.id} setSortBy={setSortBy} allColumns={allColumns} />
          </Stack>
        </Stack>

        <Table {...getTableProps()}>
          <TableHead>
            {headerGroups.map((headerGroup, i) => (
              <TableRow key={i} {...headerGroup.getHeaderGroupProps()} sx={{ '& > th:first-of-type': { width: '58px' } }}>
                {headerGroup.headers.map((column, index) => (
                  <TableCell key={index} {...column.getHeaderProps([{ className: column.className }, getHeaderProps(column)])}>
                    <HeaderSort column={column} />
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableHead>
          <TableBody {...getTableBodyProps()}>
            {loading == 'idle' ? (
              page.map((row, i) => {
                prepareRow(row);

                return (
                  <Fragment key={i}>
                    <TableRow
                      // eslint-disable-next-line
                      {...row.getRowProps()}
                      onClick={() => {
                        // eslint-disable-next-line
                        row.toggleRowSelected();
                      }}
                      // eslint-disable-next-line
                      sx={{ cursor: 'pointer', bgcolor: row.isSelected ? alpha(theme.palette.primary.lighter, 0.35) : 'inherit' }}
                    >
                      {
                        // eslint-disable-next-line
                        row.cells.map((cell, index) => (
                          <TableCell key={index} {...cell.getCellProps([{ className: cell.column.className }])}>
                            {cell.render('Cell')}
                          </TableCell>
                        ))
                      }
                    </TableRow>
                  </Fragment>
                );
              })
            ) : (
              <TableRow>
                <TableCell sx={{ p: 2, py: 3 }} colSpan={9}>
                  <LinearProgress />
                </TableCell>
              </TableRow>
            )}
            <TableRow sx={{ '&:hover': { bgcolor: 'transparent !important' } }}>
              <TableCell sx={{ p: 2, py: 3 }} colSpan={9}>
                <TablePagination
                  gotoPage={gotoPage}
                  totalCount={deviceEvents.total}
                  setPageSize={handlePageSizeChange}
                  pageSize={pageSize}
                  pageIndex={pageIndex}
                />
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </Stack>
    </>
  );
}

ReactTable.propTypes = {
  columns: PropTypes.array,
  getHeaderProps: PropTypes.func
};

const DeviceEventListPage = () => {
  const intl = useIntl();
  const renderCheckbox = ({ getToggleAllPageRowsSelectedProps }) => {
    return <IndeterminateCheckbox indeterminate {...getToggleAllPageRowsSelectedProps()} />;
  };
  const columns = [
    {
      title: 'Row Selection',
      // eslint-disable-next-line
      Header: renderCheckbox,
      accessor: 'selection',
      // eslint-disable-next-line
      Cell: ({ row }) => <IndeterminateCheckbox {...row.getToggleRowSelectedProps()} />,
      disableSortBy: true
    },
    {
      Header: intl.formatMessage({ id: 'device-event.table.column.header.id' }),
      accessor: 'id',
      className: 'cell-center'
    },
    {
      Header: intl.formatMessage({ id: 'device-event.table.column.header.time' }),
      accessor: 'time',
      className: 'cell-center'
    },
    {
      Header: intl.formatMessage({ id: 'device-event.table.column.header.dev-eui' }),
      accessor: 'devEui',
      className: 'cell-center'
    },
    {
      Header: intl.formatMessage({ id: 'device-event.table.column.header.dev-voltage' }),
      accessor: 'devVoltage',
      className: 'cell-center',
      Cell: ({ value }) => parseFloat(value).toFixed(1)
    },
    {
      Header: intl.formatMessage({ id: 'device-event.table.column.header.dev-current' }),
      accessor: 'devCurrent',
      className: 'cell-center',
      Cell: ({ value }) => parseFloat(value).toFixed(1)
    },
    {
      Header: intl.formatMessage({ id: 'device-event.table.column.header.dev-energy-out' }),
      accessor: 'devEnergyOut',
      className: 'cell-center',
      Cell: ({ value }) => parseInt(value)
    },
    {
      Header: intl.formatMessage({ id: 'device-event.table.column.header.dev-energy-in' }),
      accessor: 'devEnergyIn',
      className: 'cell-center',
      Cell: ({ value }) => parseInt(value)
    },
    {
      Header: intl.formatMessage({ id: 'device-event.table.column.header.dev-power' }),
      accessor: 'devPower',
      className: 'cell-center',
      Cell: ({ value }) => parseFloat(value).toFixed(1)
    },
    {
      Header: intl.formatMessage({ id: 'device-event.table.column.header.dev-frequency' }),
      accessor: 'devFrequency',
      className: 'cell-center',
      Cell: ({ value }) => parseFloat(value).toFixed(1)
    }
  ];

  return (
    <MainCard content={false}>
      <ScrollX>
        <ReactTable columns={columns} getHeaderProps={(column) => column.getSortByToggleProps()} />
      </ScrollX>
    </MainCard>
  );
};

export default DeviceEventListPage;
