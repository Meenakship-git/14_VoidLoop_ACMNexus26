import RiskCard from '../components/RiskCard';
import { riskData } from '../services/riskData';

function HomePage() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="sticky top-0 z-20 border-b border-slate-200 bg-white/90 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-5 py-4">
          <h1 className="text-xl font-bold tracking-tight text-slate-900">AlertWave</h1>
          <p className="text-sm text-slate-500">Wayanad Climate Intelligence</p>
        </div>
      </header>

      <main className="mx-auto w-full max-w-6xl px-5 py-10">
        <section className="rounded-2xl border border-slate-200 bg-gradient-to-br from-cyan-50 via-white to-blue-50 p-8 shadow-sm">
          <h2 className="text-3xl font-extrabold text-slate-900 md:text-4xl">Wayanad Risk Monitoring</h2>
          <p className="mt-3 max-w-2xl text-lg text-slate-700">
            Stay ahead of floods, landslides and heatwaves with real-time risk signals and actionable hazard guidance.
          </p>
          <button
            type="button"
            className="mt-6 rounded-xl bg-sky-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-sky-700"
          >
            Explore Risk Dashboard
          </button>
        </section>

        <section className="mt-10 grid gap-5 sm:grid-cols-3">
          {riskData.map((risk) => (
            <RiskCard key={risk.id} {...risk} />
          ))}
        </section>
      </main>
    </div>
  );
}

export default HomePage;
