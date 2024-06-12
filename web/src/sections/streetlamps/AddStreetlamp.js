import humps from 'humps';

import PropTypes from 'prop-types';
import { useIntl } from 'react-intl';
import { useDispatch } from 'react-redux';

import { Button, Divider, Grid, InputLabel, Stack, TextField } from '@mui/material';
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

const getInitialValues = (streetlamp, user) => {
  const newStreetlamp = {
    name: '',
    accountId: user.accountId,
    deviceEui: '',
    lon: '',
    lat: '',
    appKey: ''
  };

  if (streetlamp) {
    newStreetlamp.name = streetlamp.name;
    return _.merge({}, newStreetlamp, streetlamp);
  }

  return newStreetlamp;
};

const AddStreetlamp = ({ streetlamp, onCancel, onSuccess }) => {
  const intl = useIntl();
  const dispatch = useDispatch();
  const { user } = useAuth();

  const StreetlampSchema = Yup.object().shape({
    name: Yup.string()
      .max(255)
      .required(intl.formatMessage({ id: 'streetlamp.form.validation.name.required' })),
    deviceEui: Yup.string().required(intl.formatMessage({ id: 'streetlamp.form.validation.device-eui.required' })),
    lon: Yup.number(),
    lat: Yup.number(),
    appKey: Yup.string()
  });

  const handleCancel = () => {
    onCancel();
    formik.setErrors({});
  };

  const formik = useFormik({
    initialValues: getInitialValues(streetlamp, user),
    validationSchema: StreetlampSchema,
    onSubmit: async (values, { setSubmitting }) => {
      const newStreetlamp = {
        name: values.name,
        accountId: user.accountId,
        deviceEui: values.deviceEui,
        lon: values.lon,
        lat: values.lat,
        appKey: values.appKey
      };
      if (streetlamp) {
        try {
          await axios.put(`/api/streetlamps/${streetlamp.id}`, humps.decamelizeKeys(newStreetlamp));
          dispatch(
            openSnackbar({
              open: true,
              message: 'Streetlamp updated successfully.',
              variant: 'alert',
              autoHideDuration: 3000,
              alert: {
                color: 'success'
              },
              close: false
            })
          );
          onSuccess();
        } catch (error) {
          formik.setErrors(unpackErrors(error.detail));
          setSubmitting(false);
        }
      } else {
        try {
          await axios.post('/api/streetlamps', humps.decamelizeKeys(newStreetlamp));
          dispatch(
            openSnackbar({
              open: true,
              message: 'Streetlamp added successfully.',
              variant: 'alert',
              autoHideDuration: 3000,
              alert: {
                color: 'success'
              },
              close: false
            })
          );
          onSuccess();
        } catch (error) {
          formik.setErrors(unpackErrors(error.detail));
          setSubmitting(false);
        }
      }
    }
  });

  const { errors, touched, handleSubmit, isSubmitting, getFieldProps } = formik;

  return (
    <FormikProvider value={formik}>
      <LocalizationProvider dateAdapter={AdapterDateFns}>
        <Form autoComplete="off" noValidate onSubmit={handleSubmit}>
          <DialogTitle>
            {streetlamp ? intl.formatMessage({ id: 'streetlamp.form.edittitle' }) : intl.formatMessage({ id: 'streetlamp.form.addtitle' })}
          </DialogTitle>
          <Divider />
          <DialogContent sx={{ p: 2.5 }}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={8}>
                <Grid container spacing={3}>
                  <Grid item xs={12}>
                    <Stack spacing={1.25}>
                      <InputLabel htmlFor="streetlamp-name">{intl.formatMessage({ id: 'streetlamp.form.field.name.label' })}</InputLabel>
                      <TextField
                        fullWidth
                        id="streetlamp-name"
                        placeholder={intl.formatMessage({ id: 'streetlamp.form.field.name.placeholder' })}
                        {...getFieldProps('name')}
                        error={Boolean(touched.name && errors.name)}
                        helperText={touched.name && errors.name}
                      />
                    </Stack>
                  </Grid>
                  <Grid item xs={12}>
                    <Stack spacing={1.25}>
                      <InputLabel htmlFor="streetlamp-device-eui">
                        {intl.formatMessage({ id: 'streetlamp.form.field.device-eui.label' })}
                      </InputLabel>
                      <TextField
                        fullWidth
                        id="streetlamp-device-eui"
                        placeholder={intl.formatMessage({ id: 'streetlamp.form.field.device-eui.placeholder' })}
                        {...getFieldProps('deviceEui')}
                        error={Boolean(touched.deviceEui && errors.deviceEui)}
                        helperText={touched.deviceEui && errors.deviceEui}
                      />
                    </Stack>
                  </Grid>
                  <Grid item xs={12}>
                    <Stack spacing={1.25}>
                      <InputLabel htmlFor="streetlamp-lon">{intl.formatMessage({ id: 'streetlamp.form.field.lon.label' })}</InputLabel>
                      <TextField
                        fullWidth
                        id="streetlamp-lon"
                        placeholder={intl.formatMessage({ id: 'streetlamp.form.field.lon.placeholder' })}
                        {...getFieldProps('lon')}
                        error={Boolean(touched.lon && errors.lon)}
                        helperText={touched.lon && errors.lon}
                      />
                    </Stack>
                  </Grid>
                  <Grid item xs={12}>
                    <Stack spacing={1.25}>
                      <InputLabel htmlFor="streetlamp-lat">{intl.formatMessage({ id: 'streetlamp.form.field.lat.label' })}</InputLabel>
                      <TextField
                        fullWidth
                        id="streetlamp-lat"
                        placeholder={intl.formatMessage({ id: 'streetlamp.form.field.lat.placeholder' })}
                        {...getFieldProps('lat')}
                        error={Boolean(touched.lat && errors.lat)}
                        helperText={touched.lat && errors.lat}
                      />
                    </Stack>
                  </Grid>
                  {streetlamp == null ? (
                    <Grid item xs={12}>
                      <Stack spacing={1.25}>
                        <InputLabel htmlFor="streetlamp-app-key">
                          {intl.formatMessage({ id: 'streetlamp.form.field.app-key.label' })}
                        </InputLabel>
                        <TextField
                          fullWidth
                          id="streetlamp-app-key"
                          placeholder={intl.formatMessage({ id: 'streetlamp.form.field.app-key.placeholder' })}
                          {...getFieldProps('appKey')}
                          error={Boolean(touched.appKey && errors.appKey)}
                          helperText={touched.appKey && errors.appKey}
                        />
                      </Stack>
                    </Grid>
                  ) : (
                    <></>
                  )}
                </Grid>
              </Grid>
            </Grid>
          </DialogContent>
          <Divider />
          <DialogActions sx={{ p: 2.5 }}>
            <Button color="error" onClick={handleCancel}>
              {intl.formatMessage({ id: 'streetlamp.form.button.cancel' })}
            </Button>
            <Button type="submit" variant="contained" disabled={isSubmitting}>
              {streetlamp
                ? intl.formatMessage({ id: 'streetlamp.form.button.edit' })
                : intl.formatMessage({ id: 'streetlamp.form.button.add' })}
            </Button>
          </DialogActions>
        </Form>
      </LocalizationProvider>
    </FormikProvider>
  );
};

AddStreetlamp.propTypes = {
  streetlamp: PropTypes.object,
  onCancel: PropTypes.func,
  onSuccess: PropTypes.func
};

export default AddStreetlamp;
