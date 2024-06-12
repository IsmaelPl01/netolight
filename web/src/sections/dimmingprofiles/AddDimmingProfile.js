import PropTypes from 'prop-types';
import { useState } from 'react';
import { useIntl } from 'react-intl';
import { useDispatch } from 'react-redux';
import humps from 'humps';

import { Button, Checkbox, Divider, Grid, InputLabel, Stack, TextField, FormControlLabel } from '@mui/material';
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

const AddDimmingProfile = ({ dimmingProfile, onCancel, onSuccess }) => {
  const intl = useIntl();
  const dispatch = useDispatch();
  const { user } = useAuth();
  const [active, setActive] = useState(false);

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

  const formik = useFormik({
    initialValues: getInitialValues(dimmingProfile, user),
    validationSchema: DimmingProfileSchema,
    onSubmit: async (values, { setSubmitting }) => {
      const newDimmingProfile = {
        accountId: user.accountId,
        multicastGroupId: values.multicastGroupId,
        active: active,
        name: values.name,
        description: values.description,
        color: values.color,
        sunsetDimCmd0: values.sunsetDimCmd0,
        sunsetDimCmd1: values.sunsetDimCmd1,
        h2000DimCmd: values.h2000DimCmd,
        h2200DimCmd: values.h2200DimCmd,
        h0000DimCmd: values.h0000DimCmd,
        h0200DimCmd: values.h0200DimCmd,
        h0400DimCmd: values.h0400DimCmd,
        sunriseDimCmd0: values.sunriseDimCmd0,
        sunriseDimCmd1: values.sunriseDimCmd1
      };

      if (dimmingProfile) {
        try {
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
        } catch (error) {
          formik.setErrors(unpackErrors(error.detail));
          setSubmitting(false);
        }
      } else {
        try {
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
                      <TextField
                        fullWidth
                        id="color"
                        placeholder={intl.formatMessage({ id: 'dimmingProfile.form.field.color.placeholder' })}
                        {...getFieldProps('color')}
                        error={Boolean(touched.color && errors.color)}
                        helperText={touched.color && errors.color}
                      />
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
                    <Stack spacing={1.25}>
                      <InputLabel htmlFor="plan">{intl.formatMessage({ id: 'dimmingProfile.form.field.plan.label' })}</InputLabel>

                      <Grid container>
                        <Grid item xs={6}>
                          <TextField disabled fullWidth value="SUNSET" />
                        </Grid>
                        <Grid item xs={3}>
                          <TextField
                            fullWidth
                            id="sunset-dim-cmd0"
                            {...getFieldProps('sunsetDimCmd0')}
                            error={Boolean(touched.sunsetDimCmd0 && errors.sunsetDimCmd0)}
                            helperText={touched.sunsetDimCmd0 && errors.sunsetDimCmd0}
                          />
                        </Grid>

                        <Grid item xs={3}>
                          <TextField
                            fullWidth
                            id="sunset-dim-cmd1"
                            {...getFieldProps('sunsetDimCmd1')}
                            error={Boolean(touched.sunsetDimCmd1 && errors.sunsetDimCmd1)}
                            helperText={touched.sunsetDimCmd1 && errors.sunsetDimCmd1}
                          />
                        </Grid>
                      </Grid>

                      <Grid container>
                        <Grid item xs={6}>
                          <TextField disabled fullWidth value="20:00" />
                        </Grid>
                        <Grid item xs={6}>
                          <TextField
                            fullWidth
                            id="h2000-dim-cmd"
                            {...getFieldProps('h2000DimCmd')}
                            error={Boolean(touched.h2000DimCmd && errors.h2000DimCmd)}
                            helperText={touched.h2000DimCmd && errors.h2000DimCmd}
                          />
                        </Grid>
                      </Grid>

                      <Grid container>
                        <Grid item xs={6}>
                          <TextField disabled fullWidth value="22:00" />
                        </Grid>
                        <Grid item xs={6}>
                          <TextField
                            fullWidth
                            id="h2200-dim-cmd"
                            {...getFieldProps('h2200DimCmd')}
                            error={Boolean(touched.h2200DimCmd && errors.h2200DimCmd)}
                            helperText={touched.h2200DimCmd && errors.h2200DimCmd}
                          />
                        </Grid>
                      </Grid>

                      <Grid container>
                        <Grid item xs={6}>
                          <TextField disabled fullWidth value="00:00" />
                        </Grid>
                        <Grid item xs={6}>
                          <TextField
                            fullWidth
                            id="h0000-dim-cmd"
                            {...getFieldProps('h0000DimCmd')}
                            error={Boolean(touched.h0000DimCmd && errors.h0000DimCmd)}
                            helperText={touched.h0000DimCmd && errors.h0000DimCmd}
                          />
                        </Grid>
                      </Grid>

                      <Grid container>
                        <Grid item xs={6}>
                          <TextField disabled fullWidth value="02:00" />
                        </Grid>
                        <Grid item xs={6}>
                          <TextField
                            fullWidth
                            id="h0200-dim-cmd"
                            {...getFieldProps('h0200DimCmd')}
                            error={Boolean(touched.h0200DimCmd && errors.h0200DimCmd)}
                            helperText={touched.h0200DimCmd && errors.h0200DimCmd}
                          />
                        </Grid>
                      </Grid>

                      <Grid container>
                        <Grid item xs={6}>
                          <TextField disabled fullWidth value="04:00" />
                        </Grid>
                        <Grid item xs={6}>
                          <TextField
                            fullWidth
                            id="h0400-dim-cmd"
                            {...getFieldProps('h0400DimCmd')}
                            error={Boolean(touched.h0400DimCmd && errors.h0400DimCmd)}
                            helperText={touched.h0400DimCmd && errors.h0400DimCmd}
                          />
                        </Grid>
                      </Grid>

                      <Grid container>
                        <Grid item xs={6}>
                          <TextField disabled fullWidth value="SUNRISE" />
                        </Grid>
                        <Grid item xs={3}>
                          <TextField
                            fullWidth
                            id="sunrise-dim-cmd0"
                            {...getFieldProps('sunriseDimCmd0')}
                            error={Boolean(touched.sunriseDimCmd0 && errors.sunriseDimCmd0)}
                            helperText={touched.sunriseDimCmd0 && errors.sunriseDimCmd0}
                          />
                        </Grid>
                        <Grid item xs={3}>
                          <TextField
                            fullWidth
                            id="sunrise-dim-cmd1"
                            {...getFieldProps('sunriseDimCmd1')}
                            error={Boolean(touched.sunriseDimCmd1 && errors.sunriseDimCmd1)}
                            helperText={touched.sunriseDimCmd1 && errors.sunriseDimCmd1}
                          />
                        </Grid>
                      </Grid>
                    </Stack>
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
