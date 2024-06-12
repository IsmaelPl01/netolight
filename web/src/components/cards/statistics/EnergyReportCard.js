import PropTypes from 'prop-types';

import { Card, CardContent, Grid, Stack, Typography } from '@mui/material';

const ReportCard = ({ primary, secondary, iconPrimary, color }) => {
  const IconPrimary = iconPrimary;
  const primaryIcon = iconPrimary ? <IconPrimary fontSize="large" /> : null;

  return (
    <Card>
      <CardContent>
        <Grid container justifyContent="space-between" alignItems="center">
          <Grid item>
            <Stack spacing={1}>
              <Typography variant="body1" color="secondary">
                {secondary}
              </Typography>
              <Typography variant="h4">{primary}</Typography>
            </Stack>
          </Grid>
          <Grid item>
            <Typography variant="h2" style={{ color }}>
              {primaryIcon}
            </Typography>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

ReportCard.propTypes = {
  primary: PropTypes.string,
  secondary: PropTypes.string,
  iconPrimary: PropTypes.object,
  color: PropTypes.string
};

export default ReportCard;
