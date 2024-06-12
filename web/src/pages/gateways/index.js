import { format } from 'date-fns';
import PropTypes from 'prop-types';
import { useIntl } from 'react-intl';
import { useEffect, useMemo, useState, Fragment } from 'react';
import { useDispatch } from 'react-redux';
import { useFilters, useExpanded, useGlobalFilter } from 'react-table';
import { useRowSelect, useSortBy, useTable, usePagination } from 'react-table';

import LinearProgress from '@mui/material/LinearProgress';
import { alpha, useTheme } from '@mui/material/styles';
import { Button, Dialog, Stack, Tooltip, Typography, useMediaQuery } from '@mui/material';
import { Table, TableBody, TableCell, TableHead, TableRow } from '@mui/material';

import { PlusOutlined, EditTwoTone, DeleteTwoTone } from '@ant-design/icons';

import AddGateway from 'sections/gateways/AddGateway';
import IconButton from 'components/@extended/IconButton';
import MainCard from 'components/MainCard';
import ScrollX from 'components/ScrollX';
import { renderFilterTypes, GlobalFilter } from 'utils/react-table';
import { HeaderSort, IndeterminateCheckbox } from 'components/third-party/ReactTable';
import { SortingSelect, TablePagination, TableRowSelection } from 'components/third-party/ReactTable';
import axios from 'utils/axios';

function ReactTable({ columns, getHeaderProps }) {
  const intl = useIntl();
  const theme = useTheme();
  const dispatch = useDispatch();
  const matchDownSM = useMediaQuery(theme.breakpoints.down('sm'));

  const filterTypes = useMemo(() => renderFilterTypes, []);
  const sortBy = { id: 'name', desc: false };

  const [pageIndex, setPageIndex] = useState(0);
  const [gateways, setGateways] = useState({ total: 0, data: [] });
  const [gateway, setGateway] = useState(null);
  const [loading, setLoading] = useState('idle');
  const [opened, setOpened] = useState(false);

  const toggleDialog = () => {
    setOpened(!opened);
  };

  const handleTableAddClick = () => {
    toggleDialog();
    if (gateway && !opened) setGateway(null);
  };

  const fetchGateways = (skip, limit) => {
    return async () => {
      try {
        setLoading('pending');
        const response = await axios.get(`/api/gateways?skip=${skip}&limit=${limit}`);
        setGateways(response.data);
        setLoading('idle');
      } catch (error) {
        console.log(error);
      }
    };
  };

  const deleteGateway = (id) => {
    return async () => {
      try {
        await axios.delete(`/api/gateways/${id}`);
        setGateways((gateways) => {
          const data = gateways.data.filter((p) => p.id !== id);
          return { ...gateways, data };
        });
      } catch (error) {
        console.log(error);
      }
    };
  };

  const handleDialogAddSuccess = () => {
    toggleDialog();
    dispatch(fetchGateways(pageIndex * pageSize, pageSize));
  };

  const handleDialogDelete = (id) => {
    dispatch(deleteGateway(id));
  };

  const gotoPage = async (pageIndex) => {
    dispatch(fetchGateways(pageIndex * pageSize, pageSize));
    setPageIndex(pageIndex);
  };

  const handlePageSizeChange = (pageSize) => {
    dispatch(fetchGateways(pageIndex, pageSize));
    setPageSize(pageSize);
  };

  const columnWithActions = useMemo(
    () => {
      return columns.concat([
        {
          Header: intl.formatMessage({ id: 'gateway.table.column.header.actions' }),
          className: 'cell-center',
          disableSortBy: true,
          // eslint-disable-next-line
          Cell: ({ row }) => {
            return (
              <Stack direction="row" alignItems="center" justifyContent="center" spacing={0}>
                <Tooltip title={intl.formatMessage({ id: 'gateway.table.column.header.actions.edit' })}>
                  <IconButton
                    color="primary"
                    onClick={(e) => {
                      e.stopPropagation();
                      // eslint-disable-next-line
                      setGateway(row.values);
                      toggleDialog();
                    }}
                  >
                    <EditTwoTone twoToneColor={theme.palette.primary.main} />
                  </IconButton>
                </Tooltip>
                <Tooltip title={intl.formatMessage({ id: 'gateway.table.column.header.actions.delete' })}>
                  <IconButton
                    color="error"
                    onClick={(e) => {
                      e.stopPropagation();
                      // eslint-disable-next-line
                      handleDialogDelete(row.values.id);
                    }}
                  >
                    <DeleteTwoTone twoToneColor={theme.palette.error.main} />
                  </IconButton>
                </Tooltip>
              </Stack>
            );
          }
        }
      ]);
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
      data: gateways.data,
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
    dispatch(fetchGateways(pageIndex * pageSize, pageSize));
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
            <Button variant="contained" startIcon={<PlusOutlined />} onClick={handleTableAddClick}>
              {intl.formatMessage({ id: 'gateway.table.button.add' })}
            </Button>
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
                  totalCount={gateways.total}
                  setPageSize={handlePageSizeChange}
                  pageSize={pageSize}
                  pageIndex={pageIndex}
                />
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
        <Dialog maxWidth="sm" fullWidth onClose={toggleDialog} open={opened} sx={{ '& .MuiDialog-paper': { p: 0 } }}>
          {opened && <AddGateway gateway={gateway} onCancel={toggleDialog} onSuccess={handleDialogAddSuccess} />}
        </Dialog>
      </Stack>
    </>
  );
}

ReactTable.propTypes = {
  columns: PropTypes.array,
  getHeaderProps: PropTypes.func
};

const GatewayListPage = () => {
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
      Header: intl.formatMessage({ id: 'streetlamp.table.column.header.state' }),
      accessor: 'state',
      disableSortBy: false
    },
    {
      Header: intl.formatMessage({ id: 'streetlamp.table.column.header.last-seen' }),
      accessor: 'lastSeen',
      // eslint-disable-next-line
      Cell: ({ value }) => (
        <Typography>
          {value != null ? format(Date.parse(value), 'yyyy-MM-dd HH:mm:ss') : ''}
        </Typography>
      )
    },
    {
      Header: intl.formatMessage({ id: 'gateway.table.column.header.id' }),
      accessor: 'id'
    },
    {
      Header: intl.formatMessage({ id: 'gateway.table.column.header.name' }),
      accessor: 'name'
    },
    {
      Header: intl.formatMessage({ id: 'gateway.table.column.header.description' }),
      accessor: 'description'
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

export default GatewayListPage;
