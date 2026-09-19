import { useState } from 'react';
import { useNavigate, Link } from 'react-router';
import { USUARIO_LOGADO, movimentacoesIniciais, TipoMovimentacao } from '../../data/mockData';

const unidades = ['kg', 'litros', 'unidades', 'peças', 'kits', 'caixas', 'sacos'];

export default function Registrar() {
  const navigate = useNavigate();
  const [sucesso, setSucesso] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const [form, setForm] = useState({
    tipo: 'Entrada' as TipoMovimentacao,
    data: new Date().toLocaleDateString('pt-BR'),
    item: '',
    quantidade: '',
    unidade: 'unidades',
    observacoes: '',
  });

  const set = (field: string, value: string) => {
    setForm((f) => ({ ...f, [field]: value }));
    setErrors((e) => ({ ...e, [field]: '' }));
  };

  const validate = () => {
    const e: Record<string, string> = {};
    if (!form.data.trim()) e.data = 'Data obrigatória.';
    if (!form.item.trim()) e.item = 'Informe o item ou descrição.';
    if (!form.quantidade || isNaN(Number(form.quantidade)) || Number(form.quantidade) <= 0)
      e.quantidade = 'Informe uma quantidade válida.';
    return e;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const erros = validate();
    if (Object.keys(erros).length > 0) {
      setErrors(erros);
      return;
    }

    const nova = {
      id: String(Date.now()),
      tipo: form.tipo,
      data: form.data,
      item: form.item,
      quantidade: Number(form.quantidade),
      unidade: form.unidade,
      responsavel: USUARIO_LOGADO.nome,
      observacoes: form.observacoes || undefined,
      criadoEm: new Date().toISOString(),
      historico: [{ acao: 'Registro criado', por: USUARIO_LOGADO.nome, em: new Date().toISOString() }],
    };
    movimentacoesIniciais.unshift(nova);
    setSucesso(true);
  };

  if (sucesso) {
    return (
      <div className="max-w-xl mx-auto">
        <div className="bg-white border border-[#c8d8ef] rounded-2xl p-10 text-center">
          <div className="text-5xl mb-4">✅</div>
          <h2 className="font-serif text-2xl font-bold text-[#1a3a6e] mb-2">Movimentação registrada!</h2>
          <p className="text-[#4a6080] mb-6">
            O registro de <strong>{form.tipo.toLowerCase()}</strong> de <strong>{form.item}</strong> foi salvo com sucesso.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <Link
              to="/admin/dashboard/movimentacoes"
              className="bg-[#1a3a6e] text-white font-bold px-6 py-2.5 rounded-md hover:bg-[#0f1f3d] transition-colors"
            >
              Ver movimentações
            </Link>
            <button
              onClick={() => {
                setSucesso(false);
                setForm({ tipo: 'Entrada', data: new Date().toLocaleDateString('pt-BR'), item: '', quantidade: '', unidade: 'unidades', observacoes: '' });
              }}
              className="border border-[#c8d8ef] text-[#4a6080] font-semibold px-6 py-2.5 rounded-md hover:bg-[#f8faff] transition-colors"
            >
              Registrar outra
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl">
      <div className="mb-6">
        <h1 className="font-serif text-2xl font-bold text-[#1a3a6e]">Registrar Movimentação</h1>
        <p className="text-sm text-[#4a6080]">Preencha os dados da entrada ou saída.</p>
      </div>

      <div className="bg-white border border-[#c8d8ef] rounded-xl p-6 md:p-8">
        {/* Logged user */}
        <div className="bg-[#ddeeff] rounded-lg px-4 py-2.5 text-sm text-[#1a3a6e] mb-6">
          <span className="font-semibold">Registrando como:</span> {USUARIO_LOGADO.nome}
        </div>

        <form onSubmit={handleSubmit} className="space-y-5" noValidate>
          {/* Type toggle */}
          <div>
            <label className="block text-sm font-semibold text-[#1a3a6e] mb-2">Tipo de movimentação *</label>
            <div className="flex rounded-md overflow-hidden border border-[#c8d8ef]">
              {(['Entrada', 'Saída'] as TipoMovimentacao[]).map((t) => (
                <button
                  key={t}
                  type="button"
                  onClick={() => set('tipo', t)}
                  className={`flex-1 py-2.5 text-sm font-bold transition-colors ${
                    form.tipo === t
                      ? t === 'Entrada'
                        ? 'bg-green-700 text-white'
                        : 'bg-red-600 text-white'
                      : 'bg-white text-[#4a6080] hover:bg-[#f8faff]'
                  }`}
                >
                  {t === 'Entrada' ? '↓ Entrada' : '↑ Saída'}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-semibold text-[#1a3a6e] mb-1">Data da movimentação *</label>
            <input
              type="text"
              value={form.data}
              onChange={(e) => set('data', e.target.value)}
              placeholder="DD/MM/AAAA"
              className={`w-full border rounded-md px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-[#2d7dd2] bg-white ${errors.data ? 'border-red-400' : 'border-[#c8d8ef]'}`}
            />
            {errors.data && <p className="text-red-600 text-xs mt-1">{errors.data}</p>}
          </div>

          <div>
            <label className="block text-sm font-semibold text-[#1a3a6e] mb-1">Item ou descrição *</label>
            <input
              type="text"
              value={form.item}
              onChange={(e) => set('item', e.target.value)}
              placeholder="Ex.: Arroz tipo 1, Quentinhas, Cestas básicas..."
              className={`w-full border rounded-md px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-[#2d7dd2] bg-white ${errors.item ? 'border-red-400' : 'border-[#c8d8ef]'}`}
            />
            {errors.item && <p className="text-red-600 text-xs mt-1">{errors.item}</p>}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold text-[#1a3a6e] mb-1">Quantidade *</label>
              <input
                type="number"
                min="1"
                value={form.quantidade}
                onChange={(e) => set('quantidade', e.target.value)}
                placeholder="0"
                className={`w-full border rounded-md px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-[#2d7dd2] bg-white ${errors.quantidade ? 'border-red-400' : 'border-[#c8d8ef]'}`}
              />
              {errors.quantidade && <p className="text-red-600 text-xs mt-1">{errors.quantidade}</p>}
            </div>
            <div>
              <label className="block text-sm font-semibold text-[#1a3a6e] mb-1">Unidade</label>
              <select
                value={form.unidade}
                onChange={(e) => set('unidade', e.target.value)}
                className="w-full border border-[#c8d8ef] rounded-md px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-[#2d7dd2] bg-white"
              >
                {unidades.map((u) => <option key={u}>{u}</option>)}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-semibold text-[#1a3a6e] mb-1">
              Observações <span className="font-normal text-[#4a6080]">(opcional)</span>
            </label>
            <textarea
              rows={3}
              value={form.observacoes}
              onChange={(e) => set('observacoes', e.target.value)}
              placeholder="Ex.: origem da doação, destino, campanha, etc."
              className="w-full border border-[#c8d8ef] rounded-md px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-[#2d7dd2] bg-white resize-none"
            />
          </div>

          <div className="flex gap-3 pt-2">
            <button
              type="submit"
              className="flex-1 bg-[#1a3a6e] text-white font-bold py-3 rounded-md hover:bg-[#0f1f3d] transition-colors"
            >
              Salvar movimentação
            </button>
            <Link
              to="/admin/dashboard/movimentacoes"
              className="px-6 py-3 border border-[#c8d8ef] text-[#4a6080] font-semibold rounded-md hover:bg-[#f8faff] transition-colors text-center"
            >
              Cancelar
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
}
