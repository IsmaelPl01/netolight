/* eslint-disable */
import PropTypes from 'prop-types';
import { useIntl } from 'react-intl';
import { useState } from 'react';
import { useDispatch } from 'react-redux';

import { Button, Divider, Grid, InputLabel, Stack, TextField } from '@mui/material';
import { DialogActions, DialogContent, DialogTitle } from '@mui/material';

import { openSnackbar } from 'store/reducers/snackbar';
import axios from 'utils/axios';

const AddStreetlamp = ({ onCancel, onSuccess }) => {
  const intl = useIntl();
  const dispatch = useDispatch();

  const [file, setSelectedFile] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const handleCancel = () => {
    onCancel();
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      const formData = new FormData();
      formData.append('file', file);
      await axios.post('/api/streetlamps/file', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      openSnackbar({
        open: true,
        message: 'Streetlamps added successfully.',
        variant: 'alert',
        autoHideDuration: 6000,
        alert: {
          color: 'success'
        },
        close: false
      });
      onSuccess();
    } catch (error) {
      setSubmitting(false);
    }

  }

  return (
    <form autoComplete="off" noValidate onSubmit={handleSubmit}>
      <DialogTitle>
        {intl.formatMessage({ id: 'streetlamp-file.form.title' })}
      </DialogTitle>
      <Divider />
      <DialogContent sx={{ p: 2.5 }}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Stack spacing={1.25}>
                  <InputLabel htmlFor="streetlamp-file">{intl.formatMessage({ id: 'streetlamp-file.form.field.file.label' })}</InputLabel>
                  <TextField
                    fullWidth
                    type='file'
                    onChange={(e) => setSelectedFile(e.target.files?.[0])}
                    disabled={submitting}
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
          {intl.formatMessage({ id: 'streetlamp-file.form.button.cancel' })}
        </Button>
        <Button type="submit" variant="contained" disabled={submitting}>
          {intl.formatMessage({ id: 'streetlamp-file.form.button.add' })}
        </Button>
      </DialogActions>
    </form>
  );
};

AddStreetlamp.propTypes = {
  onCancel: PropTypes.func,
  onSuccess: PropTypes.func
};

export default AddStreetlamp;
