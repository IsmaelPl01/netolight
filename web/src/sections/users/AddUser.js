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

const getInitialValues = (user) => {
  const newUser = {
    name: ''
  };

  if (user) {
    newUser.name = user.name;
    return _.merge({}, newUser, user);
  }

  return newUser;
};

const AddUser = ({ user, onCancel, onSuccess }) => {
  const intl = useIntl();
  const dispatch = useDispatch();

  const UserSchema = Yup.object().shape({
    name: Yup.string()
      .max(255)
      .required(intl.formatMessage({ id: 'user.form.validation.name.required' }))
  });

  const handleCancel = () => {
    onCancel();
    formik.setErrors({});
  };

  const formik = useFormik({
    initialValues: getInitialValues(user),
    validationSchema: UserSchema,
    onSubmit: async (values, { setSubmitting }) => {
      const newUser = {
        name: values.name
      };

      if (user) {
        updateUser(user.id, newUser);
      } else {
        try {
          await axios.post('/api/users/', newUser);
          dispatch(
            openSnackbar({
              open: true,
              message: 'User added successfully.',
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
          formik.setErrors({ name: error.detail });
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
            {user ? intl.formatMessage({ id: 'user.form.edittitle' }) : intl.formatMessage({ id: 'user.form.addtitle' })}
          </DialogTitle>
          <Divider />
          <DialogContent sx={{ p: 2.5 }}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={8}>
                <Grid container spacing={3}>
                  <Grid item xs={12}>
                    <Stack spacing={1.25}>
                      <InputLabel htmlFor="user-name">{intl.formatMessage({ id: 'user.form.field.name.label' })}</InputLabel>
                      <TextField
                        fullWidth
                        id="user-name"
                        placeholder={intl.formatMessage({ id: 'user.form.field.name.placeholder' })}
                        {...getFieldProps('name')}
                        error={Boolean(touched.name && errors.name)}
                        helperText={touched.name && errors.name}
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
              {intl.formatMessage({ id: 'user.form.button.cancel' })}
            </Button>
            <Button type="submit" variant="contained" disabled={isSubmitting}>
              {user ? intl.formatMessage({ id: 'user.form.button.edit' }) : intl.formatMessage({ id: 'user.form.button.add' })}
            </Button>
          </DialogActions>
        </Form>
      </LocalizationProvider>
    </FormikProvider>
  );
};

AddUser.propTypes = {
  user: PropTypes.object,
  onCancel: PropTypes.func,
  onSuccess: PropTypes.func
};

export default AddUser;
