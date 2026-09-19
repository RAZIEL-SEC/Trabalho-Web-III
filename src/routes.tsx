import { createBrowserRouter } from 'react-router';
import PublicLayout from './layouts/PublicLayout';
import AdminLayout from './layouts/AdminLayout';
import Home from './pages/public/Home';
import QuemSomos from './pages/public/QuemSomos';
import NossasAcoes from './pages/public/NossasAcoes';
import ComoAjudar from './pages/public/ComoAjudar';
import Contato from './pages/public/Contato';
import Login from './pages/admin/Login';
import Dashboard from './pages/admin/Dashboard';
import Movimentacoes from './pages/admin/Movimentacoes';
import Registrar from './pages/admin/Registrar';
import Detalhes from './pages/admin/Detalhes';

export const router = createBrowserRouter([
  {
    path: '/',
    Component: PublicLayout,
    children: [
      { index: true, Component: Home },
      { path: 'quem-somos', Component: QuemSomos },
      { path: 'nossas-acoes', Component: NossasAcoes },
      { path: 'como-ajudar', Component: ComoAjudar },
      { path: 'contato', Component: Contato },
    ],
  },
  {
    path: '/admin',
    Component: Login,
  },
  {
    path: '/admin/dashboard',
    Component: AdminLayout,
    children: [
      { index: true, Component: Dashboard },
      { path: 'movimentacoes', Component: Movimentacoes },
      { path: 'registrar', Component: Registrar },
      { path: 'movimentacoes/:id', Component: Detalhes },
    ],
  },
]);
