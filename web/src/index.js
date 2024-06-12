import ReactDOM from 'react-dom';
import { BrowserRouter } from 'react-router-dom';

import { Provider as ReduxProvider } from 'react-redux';

import 'simplebar/src/simplebar.css';
import 'slick-carousel/slick/slick.css';
import 'slick-carousel/slick/slick-theme.css';

import 'assets/third-party/apex-chart.css';
import 'assets/third-party/react-table.css';

import App from './App';
import { store } from 'store';
import { ConfigProvider } from 'contexts/ConfigContext';
import reportWebVitals from './reportWebVitals';

ReactDOM.render(
  <ReduxProvider store={store}>
    <ConfigProvider>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </ConfigProvider>
  </ReduxProvider>,
  document.getElementById('root')
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
