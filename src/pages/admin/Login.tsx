import { useState } from 'react';
import { useNavigate, Link } from 'react-router';
import Logo from '../../components/Logo';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!email || !password) {
      setError('Preencha o e-mail e a senha para continuar.');
      return;
    }

    setLoading(true);
    // Prototype login — any valid email + any password works
    setTimeout(() => {
      setLoading(false);
      navigate('/admin/dashboard');
    }, 800);
  };

  return (
    <div className="min-h-screen bg-[#f8faff] flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <Logo size={56} />
          </div>
          <h1 className="font-serif text-2xl font-bold text-[#1a3a6e] mb-1">Amigos do Zé Alguém</h1>
          <p className="text-sm text-[#4a6080]">Área administrativa</p>
        </div>

        <div className="bg-white rounded-2xl shadow-sm border border-[#c8d8ef] p-8">
          <h2 className="font-bold text-[#1a3a6e] text-lg mb-6">Entrar</h2>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-[#1a3a6e] mb-1">E-mail</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="seu@email.com"
                className="w-full border border-[#c8d8ef] rounded-md px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-[#2d7dd2] bg-white"
                autoComplete="email"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-[#1a3a6e] mb-1">Senha</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full border border-[#c8d8ef] rounded-md px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-[#2d7dd2] bg-white"
                autoComplete="current-password"
              />
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded-md px-4 py-2.5">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-[#1a3a6e] text-white font-bold py-3 rounded-md hover:bg-[#0f1f3d] disabled:opacity-60 transition-colors"
            >
              {loading ? 'Entrando...' : 'Entrar'}
            </button>
          </form>

          <p className="text-xs text-[#4a6080] mt-6 text-center">
            Este é um protótipo acadêmico. Não insira dados reais.
          </p>
        </div>

        <div className="text-center mt-6">
          <Link to="/" className="text-sm text-[#2d7dd2] hover:underline">
            ← Voltar ao site
          </Link>
        </div>
      </div>
    </div>
  );
}
