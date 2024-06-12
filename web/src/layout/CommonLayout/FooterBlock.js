import PropTypes from 'prop-types';

import { useTheme } from '@mui/material/styles';
import { Box, Container, Divider, Grid, Typography } from '@mui/material';

const FooterBlock = () => {
  const theme = useTheme();

  return (
    <>
      <Divider sx={{ borderColor: 'grey.700' }} />
      <Box
        sx={{
          py: 1.5,
          bgcolor: theme.palette.mode === 'dark' ? theme.palette.grey[50] : theme.palette.grey[800]
        }}
      >
        <Container>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={8}>
              <Typography variant="subtitle2" color="secondary">
                © ESCG
              </Typography>
            </Grid>
            <Grid item xs={12} sm={4}></Grid>
          </Grid>
        </Container>
      </Box>
    </>
  );
};

FooterBlock.propTypes = {
  isFull: PropTypes.bool
};

export default FooterBlock;
