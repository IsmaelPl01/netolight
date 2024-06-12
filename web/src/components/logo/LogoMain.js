import PropTypes from 'prop-types';

import { useTheme } from '@mui/material/styles';

const LogoMain = () => {
  const theme = useTheme();
  return (
    <>
      <svg width="210" height="42" viewBox="0 0 210 42" xmlns="http://www.w3.org/2000/svg">
        <style>
          {`
           .neto {
              font: 34px san-serif;
              fill: ${theme.palette.mode == 'dark' ? 'white' : 'black'};
              dominant-baseline: middle;
              text-anchor: middle;
            }
           `}
        </style>
        <text x="50%" y="55%" className="neto">
          NetoLight
        </text>
      </svg>
    </>
  );
};

LogoMain.propTypes = {
  reverse: PropTypes.bool
};

export default LogoMain;
