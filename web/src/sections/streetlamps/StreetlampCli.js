import humps from 'humps';
import moment from 'moment';
import 'moment/locale/es';

import PropTypes from 'prop-types';

import { useEffect, useState } from 'react';
import { useIntl } from 'react-intl';
import { useDispatch } from 'react-redux';

import {
  Box,
  Button,
  CircularProgress,
  Divider,
  Grid,
  InputLabel,
  List,
  ListItem,
  ListItemText,
  MenuItem,
  Select,
  Stack,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableRow,
  DialogActions,
  DialogContent,
  DialogTitle,
  Slider
} from '@mui/material';

import { LocalizationProvider } from '@mui/x-date-pickers';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';

import * as Yup from 'yup';
import { useFormik, Form, FormikProvider } from 'formik';

import axios from 'utils/axios';
import unpackErrors from 'utils/unpackErrors';

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

const StreetlampCli = ({ devEui, onClose }) => {
  const intl = useIntl();
  const dispatch = useDispatch();

  const [loading, setLoading] = useState('loading');
  const [streetlampState, setStreetlampState] = useState(null);
  const [latestCmdSentDate, setLatestCmdSentDate] = useState(null);

  const [showSlider, setShowSlider] = useState(false);
  const [sliderValue, setSliderValue] = useState(0);

  const StreetlampSchema = Yup.object().shape({ command: Yup.string() });

  const handleClose = () => {
    onClose();
    formik.setErrors({});
  };

  const formik = useFormik({
    initialValues: { command: '[choose]' },
    validationSchema: StreetlampSchema,
    onSubmit: async (values, { setSubmitting }) => {
      const sendCmd = {
        command: values.command
      };
      try {
        await axios.put(`/api/devices/${devEui}/send_command`, humps.decamelizeKeys(sendCmd));
        setLatestCmdSentDate(moment());
        setSubmitting(false);
      } catch (error) {
        formik.setErrors(unpackErrors(error.detail));
        setSubmitting(false);
      }
    }
  });
  const { handleSubmit, isSubmitting } = formik;

  const fetchLatestState = () => {
    return async () => {
      try {
        setLoading('pending');
        const response = await axios.get(`/api/streetlamp_states/latest?dev_eui=${devEui}`);
        setStreetlampState(humps.camelizeKeys(response.data));
        setLoading('idle');
      } catch (error) {
        console.log(error);
      }
    };
  };

  const reload = () => {
    dispatch(fetchLatestState());
  };

  useEffect(() => {
    dispatch(fetchLatestState());
  }, [devEui, dispatch]);

  return (
    <FormikProvider value={formik}>
      <LocalizationProvider dateAdapter={AdapterDateFns}>
        <Form autoComplete="off" noValidate onSubmit={handleSubmit}>
          <DialogTitle>{intl.formatMessage({ id: 'streetlamp.cli-form.title' })}</DialogTitle>
          <Divider />
          <DialogContent sx={{ p: 2.5 }}>
            <Grid container spacing={2.5} justifyContent="center">
              <Grid item>
                <Typography variant="h5">{intl.formatMessage({ id: 'streetlamp.cli-form.subtitle' }, { devEui: devEui })}</Typography>
              </Grid>
              <Grid item>
                <Grid container spacing={3}>
                  <Grid item xs={6}>
                    {loading == 'loading' ? (
                      <LoadingIndicator />
                    ) : (
                      <Grid container spacing={2.25}>
                        <Grid item xs={12}>
                          <List sx={{ width: 1, p: 0 }}>
                            <ListItem disablePadding>
                              <ListItemText
                                primary={
                                  <Typography variant="subtitle1" align="center">
                                    {intl.formatMessage({ id: 'streetlamp.cli-form.latest-state.label' })}
                                  </Typography>
                                }
                                secondary={
                                  <Typography variant="subtitle1" align="center">
                                    {streetlampState
                                      ? moment(streetlampState.time).locale(intl.locale).format('MMMM Do YYYY, h:mm:ss a')
                                      : '-'}
                                  </Typography>
                                }
                              />
                            </ListItem>
                          </List>
                        </Grid>
                        <Grid item xs={12}>
                          <Grid container spacing={1}>
                            <Grid item xs={12}>
                              <TableContainer>
                                <Table size="small">
                                  <TableBody>
                                    <TableRow hover>
                                      <TableCell sx={{ pl: 3 }} component="th" scope="row">
                                        {intl.formatMessage({ id: 'streetlamp.cli-form.table.row.voltage.label' })}
                                      </TableCell>
                                      <TableCell align="right">{streetlampState ? streetlampState.devVoltage.toFixed(1) : '-'}</TableCell>
                                      <TableCell align="right">V</TableCell>
                                    </TableRow>
                                    <TableRow hover>
                                      <TableCell sx={{ pl: 3 }} component="th" scope="row">
                                        {intl.formatMessage({ id: 'streetlamp.cli-form.table.row.current.label' })}
                                      </TableCell>
                                      <TableCell align="right">{streetlampState ? streetlampState.devCurrent.toFixed(1) : '-'}</TableCell>
                                      <TableCell align="right">A</TableCell>
                                    </TableRow>
                                    <TableRow hover>
                                      <TableCell sx={{ pl: 3 }} component="th" scope="row">
                                        {intl.formatMessage({ id: 'streetlamp.cli-form.table.row.energy-out.label' })}
                                      </TableCell>
                                      <TableCell align="right">{streetlampState ? streetlampState.devEnergyOut : '-'}</TableCell>
                                      <TableCell align="right"></TableCell>
                                    </TableRow>
                                    <TableRow hover>
                                      <TableCell sx={{ pl: 3 }} component="th" scope="row">
                                        {intl.formatMessage({ id: 'streetlamp.cli-form.table.row.energy-in.label' })}
                                      </TableCell>
                                      <TableCell align="right">{streetlampState ? streetlampState.devEnergyIn : '-'}</TableCell>
                                      <TableCell align="right"></TableCell>
                                    </TableRow>
                                    <TableRow hover>
                                      <TableCell sx={{ pl: 3 }} component="th" scope="row">
                                        {intl.formatMessage({ id: 'streetlamp.cli-form.table.row.power.label' })}
                                      </TableCell>
                                      <TableCell align="right">{streetlampState ? streetlampState.devPower.toFixed(1) : '-'}</TableCell>
                                      <TableCell align="right"></TableCell>
                                    </TableRow>
                                    <TableRow hover>
                                      <TableCell sx={{ pl: 3 }} component="th" scope="row">
                                        {intl.formatMessage({ id: 'streetlamp.cli-form.table.row.frequency.label' })}
                                      </TableCell>
                                      <TableCell align="right">{streetlampState ? streetlampState.devFrequency.toFixed(1) : '-'}</TableCell>
                                      <TableCell align="right">Hz</TableCell>
                                    </TableRow>
                                    <TableRow hover>
                                      <TableCell sx={{ pl: 3 }} component="th" scope="row">
                                        {intl.formatMessage({ id: 'streetlamp.cli-form.table.row.status.label' })}
                                      </TableCell>
                                      <TableCell align="right">
                                        {streetlampState
                                          ? streetlampState.devStatusOn
                                            ? intl.formatMessage({ id: 'streetlamp.cli-form.status.on' })
                                            : intl.formatMessage({ id: 'streetlamp.cli-form.status.off' })
                                          : '-'}
                                      </TableCell>
                                      <TableCell align="right"></TableCell>
                                    </TableRow>
                                  </TableBody>
                                </Table>
                              </TableContainer>
                            </Grid>
                          </Grid>
                        </Grid>
                        <Grid item xs={12}>
                          <Button variant="contained" disabled={isSubmitting} onClick={reload}>
                            {intl.formatMessage({ id: 'streetlamp.cli-form.button.reload' })}
                          </Button>
                        </Grid>
                      </Grid>
                    )}
                  </Grid>
                  <Grid item xs={0.5}>
                    <Divider orientation="vertical" />
                  </Grid>
                  <Grid item xs={5.5}>
                    <Grid container spacing={3}>
                      <Grid item xs={12}>
                        <List sx={{ width: 1, p: 0 }}>
                          <ListItem disablePadding>
                            <ListItemText
                              primary={
                                <Typography variant="subtitle1" align="center">
                                  {intl.formatMessage({ id: 'streetlamp.cli-form.latest-command-sent.label' })}
                                </Typography>
                              }
                              secondary={
                                <Typography variant="subtitle1" align="center">
                                  {latestCmdSentDate
                                    ? moment(latestCmdSentDate).locale(intl.locale).format('MMMM Do YYYY, h:mm:ss a')
                                    : '-'}
                                </Typography>
                              }
                            />
                          </ListItem>
                        </List>
                      </Grid>
                      <Grid item xs={12}>
                        <Stack spacing={1.25}>
                          <InputLabel htmlFor="command">{intl.formatMessage({ id: 'streetlamp.cli-form.field.command.label' })}</InputLabel>
                          <Select
                            fullWidth
                            id="command"
                            value={formik.values.command}
                            onChange={(e) => {
                              formik.setFieldValue('command', e.target.value);
                              if (e.target.value === 'dim') {
                                setShowSlider(true);
                              } else {
                                setShowSlider(false);
                              }
                            }}
                          >
                            <MenuItem value="[choose]">
                              {intl.formatMessage({ id: 'streetlamp.cli-form.field.command.placeholder' })}
                            </MenuItem>
                            {['turn_on', 'turn_off', 'dim'].map((c, i) => (
                              <MenuItem key={i} value={c}>
                                {c.toUpperCase()}
                              </MenuItem>
                            ))}
                          </Select>
                        </Stack>
                      </Grid>
                      <Grid item xs={12}>
                        {showSlider && (
                          <Stack spacing={1.25}>
                            <InputLabel htmlFor="slider">{intl.formatMessage({ id: 'streetlamp.cli-form.field.slider.label' })}</InputLabel>
                            <Slider
                              id="slider"
                              value={sliderValue}
                              onChange={(e, newValue) => {
                                setSliderValue(newValue);
                                formik.setFieldValue('command', `dim_${newValue.toString().padStart(2, '0')}`);
                              }}
                              aria-labelledby="slider"
                              valueLabelDisplay="auto"
                              step={1}
                              marks
                              min={0}
                              max={100}
                            />
                          </Stack>
                        )}
                      </Grid>
                      <Grid item xs={12}>
                        <Button type="submit" variant="contained" disabled={isSubmitting}>
                          {intl.formatMessage({ id: 'streetlamp.cli-form.button.send' })}
                        </Button>
                      </Grid>
                    </Grid>
                  </Grid>
                </Grid>
              </Grid>
            </Grid>
          </DialogContent>
          <Divider />
          <DialogActions sx={{ p: 2.5 }}>
            <Button color="error" onClick={handleClose}>
              {intl.formatMessage({ id: 'streetlamp.cli-form.button.close' })}
            </Button>
          </DialogActions>
        </Form>
      </LocalizationProvider>
    </FormikProvider>
  );
};

StreetlampCli.propTypes = {
  devEui: PropTypes.string,
  onClose: PropTypes.func
};

export default StreetlampCli;
