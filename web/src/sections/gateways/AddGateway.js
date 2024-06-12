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

const getInitialValues = (gateway) => {
  const newGateway = {
    id: '',
    name: '',
    description: ''
  };

  if (gateway) {
    return _.merge({}, newGateway, gateway);
  }

  return newGateway;
};

const AddGateway = ({ gateway, onCancel, onSuccess }) => {
  const intl = useIntl();
  const dispatch = useDispatch();

  const GatewaySchema = Yup.object().shape({
    id: Yup.string().required(intl.formatMessage({ id: 'gateway.form.validation.id.required' })),
    name: Yup.string()
      .max(255)
      .required(intl.formatMessage({ id: 'gateway.form.validation.name.required' })),
    description: Yup.string().max(255)
  });

  const handleCancel = () => {
    onCancel();
    formik.setErrors({});
  };

  const formik = useFormik({
    initialValues: getInitialValues(gateway),
    validationSchema: GatewaySchema,
    onSubmit: async (values, { setSubmitting }) => {
      const newGateway = {
        id: values.id,
        name: values.name,
        description: values.description
      };

      if (gateway) {
        try {
          await axios.put(`/api/gateways/${gateway.id}`, newGateway);
          dispatch(
            openSnackbar({
              open: true,
              message: 'Gateway updated successfully.',
              variant: 'alert',
              autoHideDuration: 6000,
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
          await axios.post('/api/gateways', newGateway);
          dispatch(
            openSnackbar({
              open: true,
              message: 'Gateway added successfully.',
              variant: 'alert',
              autoHideDuration: 6000,
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
            {gateway ? intl.formatMessage({ id: 'gateway.form.edittitle' }) : intl.formatMessage({ id: 'gateway.form.addtitle' })}
          </DialogTitle>
          <Divider />
          <DialogContent sx={{ p: 2.5 }}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={8}>
                <Grid container spacing={3}>
                  <Grid item xs={12}>
                    <Stack spacing={1.25}>
                      <InputLabel htmlFor="gateway-id">{intl.formatMessage({ id: 'gateway.form.field.id.label' })}</InputLabel>
                      <TextField
                        fullWidth
                        id="gateway-id"
                        placeholder={intl.formatMessage({ id: 'gateway.form.field.id.placeholder' })}
                        {...getFieldProps('id')}
                        error={Boolean(touched.id && errors.id)}
                        helperText={touched.id && errors.id}
                      />
                    </Stack>
                  </Grid>
                  <Grid item xs={12}>
                    <Stack spacing={1.25}>
                      <InputLabel htmlFor="gateway-name">{intl.formatMessage({ id: 'gateway.form.field.name.label' })}</InputLabel>
                      <TextField
                        fullWidth
                        id="gateway-name"
                        placeholder={intl.formatMessage({ id: 'gateway.form.field.name.placeholder' })}
                        {...getFieldProps('name')}
                        error={Boolean(touched.name && errors.name)}
                        helperText={touched.name && errors.name}
                      />
                    </Stack>
                  </Grid>
                  <Grid item xs={12}>
                    <Stack spacing={1.25}>
                      <InputLabel htmlFor="gateway-description">
                        {intl.formatMessage({ id: 'gateway.form.field.description.label' })}
                      </InputLabel>
                      <TextField
                        fullWidth
                        id="gateway-description"
                        placeholder={intl.formatMessage({ id: 'gateway.form.field.description.placeholder' })}
                        {...getFieldProps('description')}
                        error={Boolean(touched.description && errors.description)}
                        helperText={touched.description && errors.description}
                      />
                    </Stack>
                  </Grid>
                </Grid>
              </Grid>
            </Grid>
          </DialogContent>
          <Divider />
          <DialogActions sx={{ p: 2.5 }}>
            <Button color="error" onClick={handleCancel}>
              {intl.formatMessage({ id: 'gateway.form.button.cancel' })}
            </Button>
            <Button type="submit" variant="contained" disabled={isSubmitting}>
              {gateway ? intl.formatMessage({ id: 'gateway.form.button.edit' }) : intl.formatMessage({ id: 'gateway.form.button.add' })}
            </Button>
          </DialogActions>
        </Form>
      </LocalizationProvider>
    </FormikProvider>
  );
};

AddGateway.propTypes = {
  gateway: PropTypes.object,
  onCancel: PropTypes.func,
  onSuccess: PropTypes.func
};

export default AddGateway;
