import Routes from 'routes';
import ThemeCustomization from 'themes';
import Locales from 'components/Locales';
import RTLLayout from 'components/RTLLayout';
import ScrollTop from 'components/ScrollTop';
import Snackbar from 'components/@extended/Snackbar';

import { JWTProvider as AuthProvider } from 'contexts/JWTContext';

const App = () => (
  <ThemeCustomization>
    <RTLLayout>
      <Locales>
        <ScrollTop>
          <AuthProvider>
            <>
              <Routes />
              <Snackbar />
            </>
          </AuthProvider>
        </ScrollTop>
      </Locales>
    </RTLLayout>
  </ThemeCustomization>
);

export default App;
