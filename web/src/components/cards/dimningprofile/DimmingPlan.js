/* eslint-disable */

import { Grid, Typography } from '@mui/material';

const DimmingPlan = () => {
  const len = 500;
  const cx = 250;
  const cy = 250;
  const r = 225;

  return (
    <svg height={len} width={len}>
      <circle
        cx={cx}
        cy={cy}
        r={r}
        stroke="gray"
        strokeWidth="3"
        fill="gray"
      />
      <path d="M 475 250 A 1 1 0 0 0 25 250" fill="orange" />
      {[0,2,4,6,8,10,12].map((t) =>
        <line
          x1={cx}
          y1={cy}
          x2={cx + r * Math.cos(-t * Math.PI/12)}
          y2={cy + r * Math.sin(-t * Math.PI/12)}
          stroke="#A9A9A9"
          strokeWidth="2" />) }
      {[...Array(24).keys()].map((t) =>
        <line
          x1={cx + 0.97 * r * Math.cos(-t * Math.PI/12)}
          y1={cy + 0.97 * r * Math.sin(-t * Math.PI/12)}
          x2={cx + r * Math.cos(-t * Math.PI/12)}
          y2={cy + r * Math.sin(-t * Math.PI/12)}
          stroke="black"
          strokeWidth="2" />) }
      {[...Array(24).keys()].map((t) =>
        <text
          x={cx + 0.90 * r * Math.cos(t * Math.PI/12)}
          y={cy + 0.90 * r * Math.sin(t * Math.PI/12)}
        >{(t+6) % 24}</text>) }
    </svg>
  );
};

export default DimmingPlan;
