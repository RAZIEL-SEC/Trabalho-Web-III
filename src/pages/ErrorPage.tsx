import { Link, isRouteErrorResponse, useRouteError } from 'react-router';

type ErrorContent = {
  code: string;
  title: string;
  description: string;
};

function ErrorScreen({ content }: { content: ErrorContent }) {
  return (
    <main className="min-h-screen bg-[#f8faff] flex items-center justify-center px-4 py-12">
      <section className="w-full max-w-xl rounded-2xl border border-[#c8d8ef] bg-white p-8 text-center shadow-sm md:p-12">
        <p className="mb-3 text-xs font-bold uppercase tracking-[0.2em] text-[#2d7dd2]">Erro {content.code}</p>
        <h1 className="font-serif text-3xl font-bold text-[#1a3a6e] md:text-4xl">{content.title}</h1>
        <p className="mx-auto mt-4 max-w-md leading-relaxed text-[#4a6080]">{content.description}</p>
        <div className="mt-8 flex flex-col justify-center gap-3 sm:flex-row">
          <Link to="/" className="rounded-md bg-[#1a3a6e] px-6 py-3 font-bold text-white transition-colors hover:bg-[#0f1f3d]">
            Voltar ao início
          </Link>
          <button
            type="button"
            onClick={() => window.location.reload()}
            className="rounded-md border border-[#c8d8ef] px-6 py-3 font-semibold text-[#4a6080] transition-colors hover:bg-[#f8faff]"
          >
            Tentar novamente
          </button>
        </div>
      </section>
    </main>
  );
}

export function RouteErrorPage() {
  const error = useRouteError();

  if (isRouteErrorResponse(error)) {
    const content = error.status === 404
      ? {
          code: '404',
          title: 'Página não encontrada',
          description: 'O endereço acessado não corresponde a uma página disponível neste momento.',
        }
      : {
          code: String(error.status),
          title: 'Não foi possível carregar esta página',
          description: 'Ocorreu um problema ao acessar este conteúdo. Tente novamente em alguns instantes.',
        };

    return <ErrorScreen content={content} />;
  }

  return (
    <ErrorScreen
      content={{
        code: '500',
        title: 'Algo não saiu como esperado',
        description: 'Ocorreu um erro inesperado ao carregar esta página. Você pode tentar novamente ou voltar ao início.',
      }}
    />
  );
}

export function NotFoundPage() {
  return (
    <ErrorScreen
      content={{
        code: '404',
        title: 'Página não encontrada',
        description: 'O endereço acessado não corresponde a uma página disponível neste momento.',
      }}
    />
  );
}
