import PropTypes from 'prop-types';
import { useState } from 'react';
import { useIntl } from 'react-intl';
import { useDispatch } from 'react-redux';
import humps from 'humps';

import {
  Button, Checkbox, Divider, Grid, InputLabel, Stack, TextField, FormControlLabel, MenuItem, Select, FormControl, FormHelperText, Slider
} from '@mui/material';
import { DialogActions, DialogContent, DialogTitle } from '@mui/material';
import { LocalizationProvider } from '@mui/x-date-pickers';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';

import _ from 'lodash';
import * as Yup from 'yup';
import { useFormik, Form, FormikProvider } from 'formik';

import { openSnackbar } from 'store/reducers/snackbar';
import axios from 'utils/axios';
import unpackErrors from 'utils/unpackErrors';
import useAuth from 'hooks/useAuth';

const getInitialValues = (dimmingProfile, user) => {
  const newDimmingProfile = {
    accountId: user.accountId,
    multicastGroupId: '',
    active: false,
    name: '',
    description: '',
    color: '',
    sunsetDimCmd0: '',
    sunsetDimCmd1: '',
    h2000DimCmd: '',
    h2200DimCmd: '',
    h0000DimCmd: '',
    h0200DimCmd: '',
    h0400DimCmd: '',
    sunriseDimCmd0: '',
    sunriseDimCmd1: ''
  };

  if (dimmingProfile) {
    return _.merge({}, newDimmingProfile, dimmingProfile);
  }

  return newDimmingProfile;
};

const parseDimCommand = (command) => {
  if (command.startsWith('dim_')) {
    const value = command.replace('dim_', '');
    const formattedValue = value.length === 1 ? `0${value}` : value;
    return { type: 'dim_valor', value: parseInt(formattedValue, 10) };
  }
  return { type: command, value: '' };
};

const AddDimmingProfile = ({ dimmingProfile, onCancel, onSuccess }) => {
  const intl = useIntl();
  const dispatch = useDispatch();
  const { user } = useAuth();
  const [active, setActive] = useState(dimmingProfile?.active || false);
  const [commands, setCommands] = useState({
    sunsetDimCmd0: parseDimCommand(dimmingProfile?.sunsetDimCmd0 || ''),
    sunsetDimCmd1: parseDimCommand(dimmingProfile?.sunsetDimCmd1 || ''),
    h2000DimCmd: parseDimCommand(dimmingProfile?.h2000DimCmd || ''),
    h2200DimCmd: parseDimCommand(dimmingProfile?.h2200DimCmd || ''),
    h0000DimCmd: parseDimCommand(dimmingProfile?.h0000DimCmd || ''),
    h0200DimCmd: parseDimCommand(dimmingProfile?.h0200DimCmd || ''),
    h0400DimCmd: parseDimCommand(dimmingProfile?.h0400DimCmd || ''),
    sunriseDimCmd0: parseDimCommand(dimmingProfile?.sunriseDimCmd0 || ''),
    sunriseDimCmd1: parseDimCommand(dimmingProfile?.sunriseDimCmd1 || '')
  });

  const DimmingProfileSchema = Yup.object().shape({
    name: Yup.string().required(intl.formatMessage({ id: 'dimmingProfile.form.validation.name.required' })),
    description: Yup.string(),
    color: Yup.string(),
    sunsetDimCmd0: Yup.string(),
    sunsetDimCmd1: Yup.string(),
    h2000DimCmd: Yup.string(),
    h2200DimCmd: Yup.string(),
    h0000DimCmd: Yup.string(),
    h0200DimCmd: Yup.string(),
    h0400DimCmd: Yup.string(),
    sunriseDimCmd0: Yup.string(),
    sunriseDimCmd1: Yup.string()
  });

  const handleCancel = () => {
    onCancel();
    formik.setErrors({});
  };

  const handleCommandChange = (e, command) => {
    const value = e.target.value;
    setCommands((prev) => ({
      ...prev,
      [command]: { type: value, value: prev[command].value }
    }));
  };

  const handleSliderChange = (event, newValue, command) => {
    setCommands((prev) => ({
      ...prev,
      [command]: { type: prev[command].type, value: newValue }
    }));
  };

  const formik = useFormik({
    initialValues: getInitialValues(dimmingProfile, user),
    validationSchema: DimmingProfileSchema,
    onSubmit: async (values, { setSubmitting }) => {
      const formatDimCommand = (type, value) => {
        if (type === 'dim_valor') {
          const formattedValue = value < 10 ? `0${value}` : value;
          return `dim_${formattedValue}`;
        }
        return type;
      };

      const newDimmingProfile = {
        accountId: user.accountId,
        multicastGroupId: values.multicastGroupId,
        active: active,
        name: values.name,
        description: values.description,
        color: values.color,
        sunsetDimCmd0: formatDimCommand(commands.sunsetDimCmd0.type, commands.sunsetDimCmd0.value),
        sunsetDimCmd1: formatDimCommand(commands.sunsetDimCmd1.type, commands.sunsetDimCmd1.value),
        h2000DimCmd: formatDimCommand(commands.h2000DimCmd.type, commands.h2000DimCmd.value),
        h2200DimCmd: formatDimCommand(commands.h2200DimCmd.type, commands.h2200DimCmd.value),
        h0000DimCmd: formatDimCommand(commands.h0000DimCmd.type, commands.h0000DimCmd.value),
        h0200DimCmd: formatDimCommand(commands.h0200DimCmd.type, commands.h0200DimCmd.value),
        h0400DimCmd: formatDimCommand(commands.h0400DimCmd.type, commands.h0400DimCmd.value),
        sunriseDimCmd0: formatDimCommand(commands.sunriseDimCmd0.type, commands.sunriseDimCmd0.value),
        sunriseDimCmd1: formatDimCommand(commands.sunriseDimCmd1.type, commands.sunriseDimCmd1.value)
      };

      try {
        if (dimmingProfile) {
          await axios.put(`/api/dimming_profiles/${dimmingProfile.id}`, humps.decamelizeKeys(newDimmingProfile));
          dispatch(
            openSnackbar({
              open: true,
              message: 'DimmingProfile updated successfully.',
              variant: 'alert',
              autoHideDuration: 6000,
              alert: {
                color: 'success'
              },
              close: false
            })
          );
          onSuccess();
        } else {
          await axios.post('/api/dimming_profiles/', humps.decamelizeKeys(newDimmingProfile));
          dispatch(
            openSnackbar({
              open: true,
              message: 'DimmingProfile added successfully.',
              variant: 'alert',
              autoHideDuration: 6000,
              alert: {
                color: 'success'
              },
              close: false
            })
          );
          onSuccess();
        }
      } catch (error) {
        formik.setErrors(unpackErrors(error.response.data.detail));
        setSubmitting(false);
      }
    }
  });

  const { errors, touched, handleSubmit, isSubmitting, getFieldProps, setFieldValue } = formik;

  const renderCommandField = (label, id, command) => (
    <Grid container spacing={2} alignItems="center">
      <Grid item xs={4}>
        <InputLabel htmlFor={id}>{label}</InputLabel>
      </Grid>
      <Grid item xs={4}>
        <FormControl fullWidth error={Boolean(touched[command] && errors[command])}>
          <Select
            id={id}
            value={commands[command].type}
            onChange={(e) => handleCommandChange(e, command)}
            displayEmpty
          >
            <MenuItem value=""><em>None</em></MenuItem>
            <MenuItem value="turn_on">Turn On</MenuItem>
            <MenuItem value="turn_off">Turn Off</MenuItem>
            <MenuItem value="dim_valor">Dim</MenuItem>
          </Select>
          <FormHelperText>{touched[command] && errors[command]}</FormHelperText>
        </FormControl>
      </Grid>
      {commands[command].type === 'dim_valor' && (
        <Grid item xs={4}>
          <Slider
            value={commands[command].value}
            onChange={(e, newValue) => handleSliderChange(e, newValue, command)}
            aria-labelledby={`${id}-slider`}
            valueLabelDisplay="auto"
            step={1}
            marks
            min={0}
            max={100}
          />
        </Grid>
      )}
    </Grid>
  );

  return (
    <FormikProvider value={formik}>
      <LocalizationProvider dateAdapter={AdapterDateFns}>
        <Form autoComplete="off" noValidate onSubmit={handleSubmit}>
          <DialogTitle>
            {dimmingProfile
              ? intl.formatMessage({ id: 'dimmingProfile.form.edittitle' })
              : intl.formatMessage({ id: 'dimmingProfile.form.addtitle' })}
          </DialogTitle>
          <Divider />
          <DialogContent sx={{ p: 2.5 }}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={12}>
                <Grid container spacing={3}>
                  <Grid item xs={12}>
                    <Stack spacing={1.25}>
                      <InputLabel htmlFor="name">{intl.formatMessage({ id: 'dimmingProfile.form.field.name.label' })}</InputLabel>
                      <TextField
                        fullWidth
                        id="name"
                        placeholder={intl.formatMessage({ id: 'dimmingProfile.form.field.name.placeholder' })}
                        {...getFieldProps('name')}
                        error={Boolean(touched.name && errors.name)}
                        helperText={touched.name && errors.name}
                      />
                    </Stack>
                  </Grid>

                  <Grid item xs={12}>
                    <Stack spacing={1.25}>
                      <InputLabel htmlFor="description">
                        {intl.formatMessage({ id: 'dimmingProfile.form.field.description.label' })}
                      </InputLabel>
                      <TextField
                        fullWidth
                        id="description"
                        placeholder={intl.formatMessage({ id: 'dimmingProfile.form.field.description.placeholder' })}
                        {...getFieldProps('description')}
                        error={Boolean(touched.description && errors.description)}
                        helperText={touched.description && errors.description}
                      />
                    </Stack>
                  </Grid>

                  <Grid item xs={12}>
                    <Stack spacing={1.25}>
                      <InputLabel htmlFor="dimming-profile-color">
                        {intl.formatMessage({ id: 'dimmingProfile.form.field.color.label' })}
                      </InputLabel>
                      <Stack direction="row" spacing={1} alignItems="center">
                        <input
                          type="color"
                          id="color-picker"
                          value={formik.values.color}
                          onChange={(e) => setFieldValue('color', e.target.value)}
                          style={{ width: '40px', height: '40px', border: 'none', padding: 0 }}
                        />
                        <TextField
                          fullWidth
                          id="color"
                          placeholder={intl.formatMessage({ id: 'dimmingProfile.form.field.color.placeholder' })}
                          {...getFieldProps('color')}
                          error={Boolean(touched.color && errors.color)}
                          helperText={touched.color && errors.color}
                        />
                      </Stack>
                    </Stack>
                  </Grid>

                  <Grid item xs={12}>
                    <Stack spacing={1.25}>
                      <InputLabel htmlFor="dimming-profile-multicast-group-id">
                        {intl.formatMessage({ id: 'dimmingProfile.form.field.multicastGroupId.label' })}
                      </InputLabel>
                      <TextField
                        fullWidth
                        id="multicastGroupId"
                        placeholder={intl.formatMessage({ id: 'dimmingProfile.form.field.multicastGroupId.placeholder' })}
                        {...getFieldProps('multicastGroupId')}
                        error={Boolean(touched.multicastGroupId && errors.multicastGroupId)}
                        helperText={touched.multicastGroupId && errors.multicastGroupId}
                      />
                    </Stack>
                  </Grid>

                  <Grid item xs={12}>
                    <InputLabel htmlFor="plan">{intl.formatMessage({ id: 'dimmingProfile.form.field.plan.label' })}</InputLabel>
                    <Grid container spacing={2} alignItems="center">
                      <Grid item xs={6}>
                        <TextField disabled fullWidth value="SUNSET" />
                      </Grid>
                      <Grid item xs={6}>
                        {renderCommandField('SUNSET Dim Command 0', 'sunset-dim-cmd0', 'sunsetDimCmd0')}
                      </Grid>
                      <Grid item xs={6}>
                        {renderCommandField('SUNSET Dim Command 1', 'sunset-dim-cmd1', 'sunsetDimCmd1')}
                      </Grid>
                      <Grid item xs={6}>
                        <TextField disabled fullWidth value="20:00" />
                      </Grid>
                      <Grid item xs={6}>
                        {renderCommandField('20:00 Dim Command', 'h2000-dim-cmd', 'h2000DimCmd')}
                      </Grid>
                      <Grid item xs={6}>
                        <TextField disabled fullWidth value="22:00" />
                      </Grid>
                      <Grid item xs={6}>
                        {renderCommandField('22:00 Dim Command', 'h2200-dim-cmd', 'h2200DimCmd')}
                      </Grid>
                      <Grid item xs={6}>
                        <TextField disabled fullWidth value="00:00" />
                      </Grid>
                      <Grid item xs={6}>
                        {renderCommandField('00:00 Dim Command', 'h0000-dim-cmd', 'h0000DimCmd')}
                      </Grid>
                      <Grid item xs={6}>
                        <TextField disabled fullWidth value="02:00" />
                      </Grid>
                      <Grid item xs={6}>
                        {renderCommandField('02:00 Dim Command', 'h0200-dim-cmd', 'h0200DimCmd')}
                      </Grid>
                      <Grid item xs={6}>
                        <TextField disabled fullWidth value="04:00" />
                      </Grid>
                      <Grid item xs={6}>
                        {renderCommandField('04:00 Dim Command', 'h0400-dim-cmd', 'h0400DimCmd')}
                      </Grid>
                      <Grid item xs={6}>
                        <TextField disabled fullWidth value="SUNRISE" />
                      </Grid>
                      <Grid item xs={6}>
                        {renderCommandField('SUNRISE Dim Command 0', 'sunrise-dim-cmd0', 'sunriseDimCmd0')}
                      </Grid>
                      <Grid item xs={6}>
                        {renderCommandField('SUNRISE Dim Command 1', 'sunrise-dim-cmd1', 'sunriseDimCmd1')}
                      </Grid>
                    </Grid>
                  </Grid>

                  <Grid item xs={12}>
                    <FormControlLabel
                      control={
                        <Checkbox
                          checked={active}
                          onChange={(event) => setActive(event.target.checked)}
                          name="active"
                          color="primary"
                          size="small"
                        />
                      }
                      label={intl.formatMessage({ id: 'dimmingProfile.form.field.active.label' })}
                    />
                  </Grid>
                </Grid>
              </Grid>
            </Grid>
          </DialogContent>
          <Divider />
          <DialogActions sx={{ p: 2.5 }}>
            <Button color="error" onClick={handleCancel}>
              {intl.formatMessage({ id: 'dimmingProfile.form.button.cancel' })}
            </Button>
            <Button type="submit" variant="contained" disabled={isSubmitting}>
              {dimmingProfile
                ? intl.formatMessage({ id: 'dimmingProfile.form.button.edit' })
                : intl.formatMessage({ id: 'dimmingProfile.form.button.add' })}
            </Button>
          </DialogActions>
        </Form>
      </LocalizationProvider>
    </FormikProvider>
  );
};

AddDimmingProfile.propTypes = {
  dimmingProfile: PropTypes.object,
  onCancel: PropTypes.func,
  onSuccess: PropTypes.func
};

export default AddDimmingProfile;
