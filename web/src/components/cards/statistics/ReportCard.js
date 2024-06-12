import PropTypes from 'prop-types';

import { Grid, Stack, Typography } from '@mui/material';

import MainCard from 'components/MainCard';

const ReportCard = ({ primary, secondary, tertiary, iconPrimary, color }) => {
  const IconPrimary = iconPrimary;
  const primaryIcon = iconPrimary ? <IconPrimary fontSize="large" /> : null;

  return (
    <MainCard>
      <Grid container justifyContent="space-between" alignItems="center">
        <Grid item>
          <Stack spacing={1}>
            <Typography variant="body1" color="secondary">
              {secondary}
            </Typography>
            <Typography variant="h4">{primary}</Typography>
            <Typography variant="body1" color="secondary">
              {tertiary}
            </Typography>
          </Stack>
        </Grid>
        <Grid item>
          <Typography variant="h2" style={{ color }}>
            {primaryIcon}
          </Typography>
        </Grid>
      </Grid>
    </MainCard>
  );
};

ReportCard.propTypes = {
  primary: PropTypes.string,
  secondary: PropTypes.string,
  iconPrimary: PropTypes.object,
  color: PropTypes.string
};

export default ReportCard;
