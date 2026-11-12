import { createBrowserRouter } from 'react-router';
import PublicLayout from './layouts/PublicLayout';
import Home from './pages/public/Home';
import QuemSomos from './pages/public/QuemSomos';
import NossasAcoes from './pages/public/NossasAcoes';
import ComoAjudar from './pages/public/ComoAjudar';
import Contato from './pages/public/Contato';
import { NotFoundPage, RouteErrorPage } from './pages/ErrorPage';

export const router = createBrowserRouter([
  {
    path: '/',
    Component: PublicLayout,
    ErrorBoundary: RouteErrorPage,
    children: [
      { index: true, Component: Home },
      { path: 'quem-somos', Component: QuemSomos },
      { path: 'nossas-acoes', Component: NossasAcoes },
      { path: 'como-ajudar', Component: ComoAjudar },
      { path: 'contato', Component: Contato },
    ],
  },
  
  {
    path: '*',
    Component: NotFoundPage,
  },
]);
