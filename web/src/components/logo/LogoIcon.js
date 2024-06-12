import { useTheme } from '@mui/material/styles';

const LogoIcon = () => {
  const theme = useTheme();
  return (
    <svg width="129" height="129" viewBox="0 0 129 129" xmlns="http://www.w3.org/2000/svg">
      <style>
        {`
           .neto {
              font: 80px san-serif;
              fill: ${theme.palette.mode == 'dark' ? 'white' : 'black'};
              dominant-baseline: middle;
              text-anchor: middle;
            }
         `}
      </style>
      <text x="50%" y="55%" className="neto">
        NL
      </text>
    </svg>
  );
};

export default LogoIcon;
