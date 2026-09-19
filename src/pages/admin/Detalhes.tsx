import { useParams, Link } from 'react-router';
import { movimentacoesIniciais } from '../../data/mockData';

function formatarData(iso: string) {
  return new Date(iso).toLocaleString('pt-BR', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  });
}

export default function Detalhes() {
  const { id } = useParams();
  const mov = movimentacoesIniciais.find((m) => m.id === id);

  if (!mov) {
    return (
      <div className="text-center py-24">
        <div className="text-4xl mb-4">❌</div>
        <h2 className="font-serif text-xl font-bold text-[#1a3a6e] mb-2">Registro não encontrado</h2>
        <p className="text-[#4a6080] mb-6">O registro que você procura não existe ou foi removido.</p>
        <Link
          to="/admin/dashboard/movimentacoes"
          className="bg-[#1a3a6e] text-white font-bold px-6 py-2.5 rounded-md hover:bg-[#0f1f3d] transition-colors"
        >
          ← Voltar às movimentações
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-2xl">
      <div className="mb-6 flex items-center gap-3">
        <Link
          to="/admin/dashboard/movimentacoes"
          className="text-sm text-[#2d7dd2] hover:underline"
        >
          ← Movimentações
        </Link>
        <span className="text-[#c8d8ef]">/</span>
        <span className="text-sm text-[#4a6080] truncate">{mov.item}</span>
      </div>

      <div className="bg-white border border-[#c8d8ef] rounded-xl overflow-hidden">
        {/* Header */}
        <div className={`px-6 py-4 border-b border-[#c8d8ef] flex items-center gap-3 ${mov.tipo === 'Entrada' ? 'bg-green-50' : 'bg-red-50'}`}>
          <span
            className={`px-3 py-1 rounded-full text-sm font-bold ${
              mov.tipo === 'Entrada' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-700'
            }`}
          >
            {mov.tipo === 'Entrada' ? '↓ Entrada' : '↑ Saída'}
          </span>
          <h1 className="font-serif text-xl font-bold text-[#1a3a6e]">{mov.item}</h1>
        </div>

        {/* Details */}
        <div className="p-6 grid grid-cols-1 sm:grid-cols-2 gap-6">
          <div>
            <p className="text-xs text-[#4a6080] uppercase tracking-widest mb-1">Data</p>
            <p className="font-semibold text-[#1a3a6e]">{mov.data}</p>
          </div>
          <div>
            <p className="text-xs text-[#4a6080] uppercase tracking-widest mb-1">Quantidade</p>
            <p className="font-semibold text-[#1a3a6e]">{mov.quantidade} {mov.unidade}</p>
          </div>
          <div>
            <p className="text-xs text-[#4a6080] uppercase tracking-widest mb-1">Responsável</p>
            <p className="font-semibold text-[#1a3a6e]">{mov.responsavel}</p>
          </div>
          <div>
            <p className="text-xs text-[#4a6080] uppercase tracking-widest mb-1">Registrado em</p>
            <p className="font-semibold text-[#1a3a6e] font-mono text-sm">{formatarData(mov.criadoEm)}</p>
          </div>
          {mov.atualizadoEm && (
            <div>
              <p className="text-xs text-[#4a6080] uppercase tracking-widest mb-1">Última atualização</p>
              <p className="font-semibold text-[#1a3a6e] font-mono text-sm">{formatarData(mov.atualizadoEm)}</p>
            </div>
          )}
          {mov.observacoes && (
            <div className="sm:col-span-2">
              <p className="text-xs text-[#4a6080] uppercase tracking-widest mb-1">Observações</p>
              <p className="text-[#1a3a6e] leading-relaxed">{mov.observacoes}</p>
            </div>
          )}
        </div>

        {/* Audit history */}
        {mov.historico && mov.historico.length > 0 && (
          <div className="border-t border-[#c8d8ef] px-6 py-5">
            <h2 className="font-bold text-[#1a3a6e] mb-4">Histórico de auditoria</h2>
            <div className="space-y-3">
              {mov.historico.map((h, i) => (
                <div key={i} className="flex gap-4 items-start">
                  <div className="mt-1 w-3 h-3 rounded-full bg-[#2d7dd2] shrink-0" />
                  <div>
                    <p className="text-sm font-semibold text-[#1a3a6e]">{h.acao}</p>
                    <p className="text-xs text-[#4a6080]">
                      Por {h.por} · {formatarData(h.em)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="border-t border-[#c8d8ef] px-6 py-4 flex gap-3 bg-[#f8faff]">
          <Link
            to="/admin/dashboard/movimentacoes"
            className="border border-[#c8d8ef] text-[#4a6080] font-semibold px-5 py-2 rounded-md hover:bg-white transition-colors text-sm"
          >
            ← Voltar
          </Link>
          <Link
            to="/admin/dashboard/registrar"
            className="bg-[#1a3a6e] text-white font-semibold px-5 py-2 rounded-md hover:bg-[#0f1f3d] transition-colors text-sm"
          >
            Nova movimentação
          </Link>
        </div>
      </div>
    </div>
  );
}
