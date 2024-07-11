import PropTypes from 'prop-types';
import { useDispatch } from 'react-redux';
import { useState, useEffect } from 'react';
import axios from 'utils/axios';

import { useTheme } from '@mui/material/styles';
import {
  Button,
  DialogActions,
  DialogContent,
  DialogTitle,
  Divider,
  FormControl,
  Grid,
  InputAdornment,
  InputLabel,
  MenuItem,
  RadioGroup,
  Select,
  Stack,
  TextField,
  Tooltip,
  Typography,
  Slider,
  FormHelperText
} from '@mui/material';
import { LocalizationProvider, MobileDateTimePicker } from '@mui/x-date-pickers';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';

import _ from 'lodash';
import * as Yup from 'yup';
import { useFormik, Form, FormikProvider } from 'formik';

import ColorPalette from './ColorPalette';
import IconButton from 'components/@extended/IconButton';
import { openSnackbar } from 'store/reducers/snackbar';
import { createEvent, deleteEvent, updateEvent } from 'store/reducers/dimmingCalendar';
import useAuth from 'hooks/useAuth';

import { CalendarOutlined, DeleteFilled } from '@ant-design/icons';

const getInitialValues = (event, range) => {
  const newEvent = {
    targetId: '',
    targetType: '[choose]',
    command: '[choose]',
    color: '#177ddc',
    textColor: '#fff',
    start: range ? new Date(range.start).toISOString() : new Date().toISOString(),
    end: range ? new Date(range.end).toISOString() : new Date().toISOString()
  };

  if (event || range) {
    return _.merge({}, newEvent, event);
  }

  return newEvent;
};

const AddEventFrom = ({ event, range, onCancel }) => {
  const theme = useTheme();
  const dispatch = useDispatch();
  const isCreating = !event;
  const { user } = useAuth();
  const [targetIds, setTargetIds] = useState([]);
  const [showSlider, setShowSlider] = useState(false);
  const [dimValue, setDimValue] = useState(50);

  const backgroundColor = [
    theme.palette.primary.main,
    theme.palette.error.main,
    theme.palette.success.main,
    theme.palette.secondary.main,
    theme.palette.warning.main,
    theme.palette.primary.lighter,
    theme.palette.error.lighter,
    theme.palette.success.lighter,
    theme.palette.secondary.lighter,
    theme.palette.warning.lighter
  ];

  const textColor = [
    '#fff',
    theme.palette.error.lighter,
    theme.palette.success.lighter,
    theme.palette.secondary.lighter,
    theme.palette.warning.lighter,
    theme.palette.primary.lighter,
    theme.palette.primary.main,
    theme.palette.error.main,
    theme.palette.success.main,
    theme.palette.secondary.main,
    theme.palette.warning.main
  ];

  useEffect(() => {
    const fetchStreetlampIds = async () => {
      try {
        const response = await axios.get('/api/streetlamps');
        console.log('API response:', response);
        const data = response.data.data; // Ajustado para manejar data.data
        
        if (Array.isArray(data)) {
          setTargetIds(data.map(streetlamp => streetlamp.device_eui)); // Asumiendo que 'device_eui' es el ID
        } else {
          console.error('Unexpected response format:', data);
        }
      } catch (error) {
        console.error('Failed to fetch streetlamp IDs:', error);
      }
    };

    fetchStreetlampIds();
  }, []);

  const EventSchema = Yup.object().shape({
    targetType: Yup.string().required('Target type is required'),
    targetId: Yup.string().required('Target ID is required'),
    command: Yup.string(),
    end: Yup.date().when('start', (start, schema) => start && schema.min(start, 'End date must be later than start date')),
    start: Yup.date(),
    color: Yup.string().max(255),
    textColor: Yup.string().max(255)
  });

  const deleteHandler = () => {
    dispatch(deleteEvent(event?.id));
    dispatch(
      openSnackbar({
        open: true,
        message: 'Event deleted successfully.',
        variant: 'alert',
        autoHideDuration: 3000,
        alert: {
          color: 'success'
        },
        close: false
      })
    );
  };

  const formik = useFormik({
    initialValues: getInitialValues(event, range),
    validationSchema: EventSchema,
    onSubmit: (values, { setSubmitting }) => {
      try {
        const newEvent = {
          accountId: user.accountId,
          targetType: values.targetType,
          targetId: values.targetId,
          command: showSlider ? `dim_${dimValue}` : values.command,
          color: values.color,
          textColor: values.textColor,
          start: values.start,
          end: values.end
        };

        if (event) {
          dispatch(updateEvent(event.id, newEvent));
          dispatch(
            openSnackbar({
              open: true,
              message: 'Event update successfully.',
              variant: 'alert',
              autoHideDuration: 3000,
              alert: {
                color: 'success'
              },
              close: false
            })
          );
        } else {
          dispatch(createEvent(newEvent));
          dispatch(
            openSnackbar({
              open: true,
              message: 'Event add successfully.',
              variant: 'alert',
              autoHideDuration: 3000,
              alert: {
                color: 'success'
              },
              close: false
            })
          );
        }

        setSubmitting(false);
      } catch (error) {
        console.error(error);
      }
    }
  });

  const { values, errors, touched, handleSubmit, isSubmitting, getFieldProps, setFieldValue } = formik;

  const handleCommandChange = (e) => {
    const value = e.target.value;
    setFieldValue('command', value);
    setShowSlider(value === 'dim_valor');
  };

  return (
    <FormikProvider value={formik}>
      <LocalizationProvider dateAdapter={AdapterDateFns}>
        <Form autoComplete="off" noValidate onSubmit={handleSubmit}>
          <DialogTitle>{event ? 'Edit dimming event' : 'Add dimming event'}</DialogTitle>
          <Divider />
          <DialogContent sx={{ p: 2.5 }}>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Stack spacing={1.25}>
                  <InputLabel htmlFor="cal-target-type">Target Type</InputLabel>
                  <Select fullWidth id="cal-target-type" {...getFieldProps('targetType')}>
                    <MenuItem value="[choose]">[Choose a Target Type]</MenuItem>
                    {['streetlamp', 'streetlamp_group'].map((c, i) => (
                      <MenuItem key={i} value={c}>
                        {c.toUpperCase()}
                      </MenuItem>
                    ))}
                  </Select>
                </Stack>
              </Grid>

              <Grid item xs={12}>
                <Stack spacing={1.25}>
                  <InputLabel htmlFor="cal-target-id">Target ID</InputLabel>
                  <Select fullWidth id="cal-target-id" {...getFieldProps('targetId')}>
                    <MenuItem value="[choose]">[Choose a Target ID]</MenuItem>
                    {targetIds.map((id, i) => (
                      <MenuItem key={i} value={id}>
                        {id}
                      </MenuItem>
                    ))}
                  </Select>
                  <FormHelperText error={Boolean(touched.targetId && errors.targetId)}>
                    {touched.targetId && errors.targetId}
                  </FormHelperText>
                </Stack>
              </Grid>

              <Grid item xs={12}>
                <Stack spacing={1.25}>
                  <InputLabel htmlFor="cal-command">Command</InputLabel>
                  <Select fullWidth id="cal-command" {...getFieldProps('command')} onChange={handleCommandChange}>
                    <MenuItem value="[choose]">[Choose a command]</MenuItem>
                    {['turn_on', 'turn_off'].map((c, i) => (
                      <MenuItem key={i} value={c}>
                        {c.toUpperCase()}
                      </MenuItem>
                    ))}
                    <MenuItem value="dim_valor">Dim</MenuItem>
                  </Select>
                </Stack>
              </Grid>

              {showSlider && (
                <Grid item xs={12}>
                  <Stack spacing={1.25}>
                    <InputLabel htmlFor="dim-value">Dim Value</InputLabel>
                    <Slider
                      value={dimValue}
                      onChange={(e, value) => setDimValue(value)}
                      aria-labelledby="dim-value"
                      valueLabelDisplay="auto"
                      step={1}
                      marks
                      min={0}
                      max={100}
                    />
                  </Stack>
                </Grid>
              )}

              <Grid item xs={12} md={6}>
                <Stack spacing={1.25}>
                  <InputLabel htmlFor="cal-start-date">Start Date</InputLabel>
                  <MobileDateTimePicker
                    value={values.start}
                    inputFormat="dd/MM/yyyy hh:mm a"
                    onChange={(date) => setFieldValue('start', date)}
                    renderInput={(params) => (
                      <TextField
                        {...params}
                        id="cal-start-date"
                        placeholder="Start date"
                        fullWidth
                        InputProps={{
                          endAdornment: (
                            <InputAdornment position="end">
                              <CalendarOutlined />
                            </InputAdornment>
                          )
                        }}
                      />
                    )}
                  />
                </Stack>
              </Grid>

              <Grid item xs={12} md={6}>
                <Stack spacing={1.25}>
                  <InputLabel htmlFor="cal-end-date">End Date</InputLabel>
                  <MobileDateTimePicker
                    value={values.end}
                    inputFormat="dd/MM/yyyy hh:mm a"
                    onChange={(date) => setFieldValue('end', date)}
                    renderInput={(params) => (
                      <TextField
                        {...params}
                        id="cal-end-date"
                        placeholder="End date"
                        fullWidth
                        error={Boolean(touched.end && errors.end)}
                        helperText={touched.end && errors.end}
                        InputProps={{
                          endAdornment: (
                            <InputAdornment position="end">
                              <CalendarOutlined />
                            </InputAdornment>
                          )
                        }}
                      />
                    )}
                  />
                </Stack>
              </Grid>
              <Grid item xs={12}>
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <Typography variant="subtitle1">Background Color</Typography>
                  </Grid>
                  <Grid item xs={12}>
                    <FormControl>
                      <RadioGroup
                        row
                        aria-label="color"
                        {...getFieldProps('color')}
                        onChange={(e) => setFieldValue('color', e.target.value)}
                        name="color-radio-buttons-group"
                        sx={{ '& .MuiFormControlLabel-root': { mr: 2 } }}
                      >
                        {backgroundColor.map((value, index) => (
                          <ColorPalette key={index} value={value} color={value} />
                        ))}
                      </RadioGroup>
                    </FormControl>
                  </Grid>
                </Grid>
              </Grid>
              <Grid item xs={12}>
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <Typography variant="subtitle1">Text Color</Typography>
                  </Grid>
                  <Grid item xs={12}>
                    <FormControl component="fieldset">
                      <RadioGroup
                        row
                        aria-label="textColor"
                        {...getFieldProps('textColor')}
                        onChange={(e) => setFieldValue('textColor', e.target.value)}
                        name="text-color-radio-buttons-group"
                        sx={{ '& .MuiFormControlLabel-root': { mr: 2 } }}
                      >
                        {textColor.map((value, index) => (
                          <ColorPalette key={index} value={value} color={value} />
                        ))}
                      </RadioGroup>
                    </FormControl>
                  </Grid>
                </Grid>
              </Grid>
            </Grid>
          </DialogContent>
          <Divider />
          <DialogActions sx={{ p: 2.5 }}>
            <Grid container justifyContent="space-between" alignItems="center">
              <Grid item>
                {!isCreating && (
                  <Tooltip title="Delete Event" placement="top">
                    <IconButton onClick={deleteHandler} size="large" color="error">
                      <DeleteFilled />
                    </IconButton>
                  </Tooltip>
                )}
              </Grid>
              <Grid item>
                <Stack direction="row" spacing={2} alignItems="center">
                  <Button color="error" onClick={onCancel}>
                    Cancel
                  </Button>
                  <Button type="submit" variant="contained" disabled={isSubmitting}>
                    {event ? 'Edit' : 'Add'}
                  </Button>
                </Stack>
              </Grid>
            </Grid>
          </DialogActions>
        </Form>
      </LocalizationProvider>
    </FormikProvider>
  );
};

AddEventFrom.propTypes = {
  event: PropTypes.object,
  range: PropTypes.object,
  onCancel: PropTypes.func
};

export default AddEventFrom;
