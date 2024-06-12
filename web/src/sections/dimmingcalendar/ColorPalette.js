import PropTypes from 'prop-types';

import { Box, FormControlLabel, Radio } from '@mui/material';

import Avatar from 'components/@extended/Avatar';

import { CheckOutlined } from '@ant-design/icons';

const ColorPalette = ({ color, value }) => (
  <FormControlLabel
    value={value}
    label=""
    control={
      <Radio
        disableRipple
        icon={
          <Avatar variant="rounded" type="combined" size="xs" sx={{ backgroundColor: color, borderColor: 'divider' }}>
            <Box sx={{ display: 'none' }} />
          </Avatar>
        }
        checkedIcon={
          <Avatar variant="rounded" type="combined" size="xs" sx={{ backgroundColor: color, color: '#000', borderColor: 'divider' }}>
            <CheckOutlined />
          </Avatar>
        }
        sx={{
          '&:hover': {
            bgcolor: 'transparent'
          }
        }}
      />
    }
  />
);

ColorPalette.propTypes = {
  color: PropTypes.string,
  value: PropTypes.string
};

export default ColorPalette;
