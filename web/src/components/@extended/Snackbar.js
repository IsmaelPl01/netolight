import { useDispatch, useSelector } from 'react-redux';

import { Alert, Button, Fade, Grow, Slide } from '@mui/material';
import MuiSnackbar from '@mui/material/Snackbar';

import IconButton from './IconButton';
import { closeSnackbar } from 'store/reducers/snackbar';

import { CloseOutlined } from '@ant-design/icons';

function TransitionSlideLeft(props) {
  return <Slide {...props} direction="left" />;
}

function TransitionSlideUp(props) {
  return <Slide {...props} direction="up" />;
}

function TransitionSlideRight(props) {
  return <Slide {...props} direction="right" />;
}

function TransitionSlideDown(props) {
  return <Slide {...props} direction="down" />;
}

function GrowTransition(props) {
  return <Grow {...props} />;
}

const animation = {
  SlideLeft: TransitionSlideLeft,
  SlideUp: TransitionSlideUp,
  SlideRight: TransitionSlideRight,
  SlideDown: TransitionSlideDown,
  Grow: GrowTransition,
  Fade
};

const Snackbar = () => {
  const dispatch = useDispatch();
  const snackbar = useSelector((state) => state.snackbar);
  const { actionButton, anchorOrigin, alert, close, message, open, transition, variant } = snackbar;

  const handleClose = (event, reason) => {
    if (reason === 'clickaway') {
      return;
    }
    dispatch(closeSnackbar());
  };

  return (
    <>
      {/* default snackbar */}
      {variant === 'default' && (
        <MuiSnackbar
          anchorOrigin={anchorOrigin}
          open={open}
          autoHideDuration={6000}
          onClose={handleClose}
          message={message}
          TransitionComponent={animation[transition]}
          action={
            <>
              <Button color="secondary" size="small" onClick={handleClose}>
                UNDO
              </Button>
              <IconButton size="small" aria-label="close" color="inherit" onClick={handleClose} sx={{ mt: 0.25 }}>
                <CloseOutlined />
              </IconButton>
            </>
          }
        />
      )}

      {/* alert snackbar */}
      {variant === 'alert' && (
        <MuiSnackbar
          TransitionComponent={animation[transition]}
          anchorOrigin={anchorOrigin}
          open={open}
          autoHideDuration={6000}
          onClose={handleClose}
        >
          <Alert
            variant={alert.variant}
            color={alert.color}
            action={
              <>
                {actionButton !== false && (
                  <Button color={alert.color} size="small" onClick={handleClose}>
                    UNDO
                  </Button>
                )}
                {close !== false && (
                  <IconButton
                    sx={{ mt: 0.25 }}
                    size="small"
                    aria-label="close"
                    variant="contained"
                    color={alert.color}
                    onClick={handleClose}
                  >
                    <CloseOutlined />
                  </IconButton>
                )}
              </>
            }
            sx={{
              ...(alert.variant === 'outlined' && {
                bgcolor: 'grey.0'
              })
            }}
          >
            {message}
          </Alert>
        </MuiSnackbar>
      )}
    </>
  );
};

export default Snackbar;
