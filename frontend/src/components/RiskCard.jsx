function RiskCard({ emoji, name, level, details }) {
  return (
    <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-1 hover:shadow-md">
      <h3 className="text-xl font-bold text-slate-900">
        <span className="mr-2">{emoji}</span>{name}
      </h3>
      <p className="mt-2 font-semibold text-sky-700">Risk Level: {level}</p>
      <p className="mt-3 text-slate-600">{details}</p>
    </article>
  );
}

export default RiskCard;
