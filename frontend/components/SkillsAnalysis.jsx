import { Briefcase, Award, TrendingUp, Wrench, Database } from 'lucide-react';

function SkillsAnalysis({ data }) {
  const skillsAnalysis = data?.analysis_results?.skills_analysis || {};

  const sections = [
    {
      title: "Technical Skills",
      icon: <Award size={18} />,
      items: skillsAnalysis.technical_skills,
      color: "text-indigo-600",
      borderColor: "border-indigo-200",
      bgColor: "bg-indigo-50",
      iconBg: "bg-indigo-100",
      skillBg: "bg-white border border-indigo-200 text-indigo-700 hover:bg-indigo-50"
    },
    {
      title: "Tools",
      icon: <Wrench size={18} />,
      items: skillsAnalysis.tools,
      color: "text-emerald-600",
      borderColor: "border-emerald-200",
      bgColor: "bg-emerald-50",
      iconBg: "bg-emerald-100",
      skillBg: "bg-white border border-emerald-200 text-emerald-700 hover:bg-emerald-50"
    },
    {
      title: "Databases",
      icon: <Database size={18} />,
      items: skillsAnalysis.databases,
      color: "text-amber-600",
      borderColor: "border-amber-200",
      bgColor: "bg-amber-50",
      iconBg: "bg-amber-100",
      skillBg: "bg-white border border-amber-200 text-amber-700 hover:bg-amber-50"
    }
  ];

  return (
    <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-100 space-y-8 hover:shadow-2xl transition-shadow duration-300 max-w-6xl mx-auto">

      {/* Header */}
      <div className="flex items-center gap-3 pb-4 border-b border-gray-100">
        <div className="p-2.5 bg-gradient-to-br from-indigo-500 to-indigo-600 rounded-xl shadow-lg shadow-indigo-200">
          <Briefcase className="text-white" size={24} />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-gray-800">Skills Analysis</h2>
          <p className="text-sm text-gray-500 mt-0.5">Technical expertise breakdown</p>
        </div>
      </div>

      {/* Stats Cards — always 2 columns */}
      <div className="grid grid-cols-2 gap-6">
        <div className="rounded-xl bg-gradient-to-br from-indigo-50 to-white p-6 border border-indigo-100 shadow-sm hover:shadow-md transition-all">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-indigo-600 uppercase tracking-wider">Experience</span>
            <Briefcase size={16} className="text-indigo-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-4xl font-bold text-gray-800">
              {skillsAnalysis.years_of_experience || 0}
            </span>
            <span className="text-sm font-medium text-gray-500">years</span>
          </div>
          <div className="mt-5 h-3 w-full bg-indigo-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-indigo-500 to-indigo-600 rounded-full"
              style={{ width: `${Math.min((skillsAnalysis.years_of_experience || 0) * 10, 100)}%` }}
            />
          </div>
        </div>

        <div className="rounded-xl bg-gradient-to-br from-emerald-50 to-white p-6 border border-emerald-100 shadow-sm hover:shadow-md transition-all">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-emerald-600 uppercase tracking-wider">Level</span>
            <TrendingUp size={16} className="text-emerald-400" />
          </div>
          <div className="flex items-center gap-3">
            <span className="text-3xl font-bold text-gray-800">
              {skillsAnalysis.experience_level || "N/A"}
            </span>
          </div>
        </div>
      </div>

      {/* Skills Sections */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        {sections.map(
          (section, idx) =>
            section.items?.length > 0 && (
              <div
                key={idx}
                className={`p-6 rounded-xl border ${section.borderColor} ${section.bgColor} shadow-sm`}
                style={{ minWidth: 0, overflow: 'hidden' }}
              >
                {/* Section Header */}
                <div className="flex items-center gap-2 mb-5">
                  <div className={`p-2 rounded-lg ${section.iconBg} ${section.color}`}>
                    {section.icon}
                  </div>
                  <h3 className="font-semibold text-gray-800 text-base">
                    {section.title}
                  </h3>
                </div>

                {/* Pills — inline styles guarantee wrap works regardless of Tailwind purge */}
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', width: '100%', minWidth: 0 }}>
                  {section.items.map((skill, i) => (
                    <span
                      key={i}
                      className={`px-3 py-1.5 text-sm font-medium rounded-full transition-colors cursor-pointer ${section.skillBg}`}
                      style={{ whiteSpace: 'nowrap' }}
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )
        )}
      </div>

    </div>
  );
}

export default SkillsAnalysis;