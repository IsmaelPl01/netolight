import { combineReducers } from 'redux';

import menu from './menu';
import snackbar from './snackbar';
import dimmingCalendar from './dimmingCalendar';

const reducers = combineReducers({
  menu,
  dimmingCalendar,
  snackbar
});

export default reducers;
