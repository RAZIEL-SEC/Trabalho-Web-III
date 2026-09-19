export type TipoMovimentacao = 'Entrada' | 'Saída';

export interface Movimentacao {
  id: string;
  tipo: TipoMovimentacao;
  data: string; // DD/MM/YYYY
  item: string;
  quantidade: number;
  unidade: string;
  responsavel: string;
  observacoes?: string;
  criadoEm: string; // ISO string
  atualizadoEm?: string;
  historico?: { acao: string; por: string; em: string }[];
}

export const USUARIO_LOGADO = {
  nome: 'Coordenadora Ana Paula',
  email: 'ana.paula@amigosdozealgem.org',
};

export const movimentacoesIniciais: Movimentacao[] = [
  {
    id: '1',
    tipo: 'Entrada',
    data: '15/09/2026',
    item: 'Arroz tipo 1',
    quantidade: 200,
    unidade: 'kg',
    responsavel: 'Coordenadora Ana Paula',
    observacoes: 'Doação da empresa Supermercados Bom Preço',
    criadoEm: '2026-09-15T09:30:00',
    historico: [{ acao: 'Registro criado', por: 'Coordenadora Ana Paula', em: '2026-09-15T09:30:00' }],
  },
  {
    id: '2',
    tipo: 'Entrada',
    data: '14/09/2026',
    item: 'Feijão carioca',
    quantidade: 100,
    unidade: 'kg',
    responsavel: 'Voluntário Carlos Eduardo',
    observacoes: 'Arrecadação da campanha de setembro',
    criadoEm: '2026-09-14T14:00:00',
    historico: [{ acao: 'Registro criado', por: 'Voluntário Carlos Eduardo', em: '2026-09-14T14:00:00' }],
  },
  {
    id: '3',
    tipo: 'Saída',
    data: '13/09/2026',
    item: 'Quentinhas distribuídas',
    quantidade: 150,
    unidade: 'unidades',
    responsavel: 'Coordenadora Ana Paula',
    observacoes: 'Distribuição na Praça Central — sábado',
    criadoEm: '2026-09-13T18:00:00',
    historico: [{ acao: 'Registro criado', por: 'Coordenadora Ana Paula', em: '2026-09-13T18:00:00' }],
  },
  {
    id: '4',
    tipo: 'Saída',
    data: '10/09/2026',
    item: 'Cestas básicas',
    quantidade: 30,
    unidade: 'unidades',
    responsavel: 'Voluntária Maria das Graças',
    observacoes: 'Famílias cadastradas no bairro São João',
    criadoEm: '2026-09-10T10:00:00',
    historico: [{ acao: 'Registro criado', por: 'Voluntária Maria das Graças', em: '2026-09-10T10:00:00' }],
  },
  {
    id: '5',
    tipo: 'Entrada',
    data: '08/09/2026',
    item: 'Kit higiene pessoal',
    quantidade: 80,
    unidade: 'unidades',
    responsavel: 'Coordenadora Ana Paula',
    observacoes: 'Parceria com a farmácia Saúde Total',
    criadoEm: '2026-09-08T11:30:00',
    historico: [{ acao: 'Registro criado', por: 'Coordenadora Ana Paula', em: '2026-09-08T11:30:00' }],
  },
  {
    id: '6',
    tipo: 'Saída',
    data: '05/09/2026',
    item: 'Roupas infantis',
    quantidade: 45,
    unidade: 'peças',
    responsavel: 'Voluntária Maria das Graças',
    observacoes: 'Campanha do agasalho — crianças de 2 a 10 anos',
    criadoEm: '2026-09-05T15:00:00',
    historico: [{ acao: 'Registro criado', por: 'Voluntária Maria das Graças', em: '2026-09-05T15:00:00' }],
  },
  {
    id: '7',
    tipo: 'Entrada',
    data: '01/09/2026',
    item: 'Leite integral',
    quantidade: 60,
    unidade: 'litros',
    responsavel: 'Voluntário Carlos Eduardo',
    criadoEm: '2026-09-01T08:00:00',
    historico: [{ acao: 'Registro criado', por: 'Voluntário Carlos Eduardo', em: '2026-09-01T08:00:00' }],
  },
  {
    id: '8',
    tipo: 'Saída',
    data: '28/08/2026',
    item: 'Material escolar',
    quantidade: 25,
    unidade: 'kits',
    responsavel: 'Coordenadora Ana Paula',
    observacoes: 'Projeto Amigos da Escola — turma de setembro',
    criadoEm: '2026-08-28T09:00:00',
    historico: [{ acao: 'Registro criado', por: 'Coordenadora Ana Paula', em: '2026-08-28T09:00:00' }],
  },
];
