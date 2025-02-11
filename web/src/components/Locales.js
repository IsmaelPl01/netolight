import PropTypes from 'prop-types';
import { useEffect, useState } from 'react';

import { IntlProvider } from 'react-intl';

import useConfig from 'hooks/useConfig';

const loadLocaleData = (locale) => {
  switch (locale) {
    case 'es':
      return import('utils/locales/es.json');
    case 'en':
    default:
      return import('utils/locales/en.json');
  }
};

const Locales = ({ children }) => {
  const { i18n } = useConfig();

  const [messages, setMessages] = useState();

  useEffect(() => {
    loadLocaleData(i18n).then((d) => {
      setMessages(d.default);
    });
  }, [i18n]);

  return (
    <>
      {messages && (
        <IntlProvider locale={i18n} defaultLocale="en" messages={messages}>
          {children}
        </IntlProvider>
      )}
    </>
  );
};

Locales.propTypes = {
  children: PropTypes.node
};

export default Locales;
