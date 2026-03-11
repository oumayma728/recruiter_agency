function SkillsAnalysis({ data }) {
  const skillsAnalysis = data?.analysis_results?.skills_analysis || {};

  const sections = [
    {
      title: "Technical Skills",
      icon: <Award size={18} />,
      items: skillsAnalysis.technical_skills,
      color: "bg-indigo-50 text-indigo-700 border-indigo-200 hover:bg-indigo-100 hover:border-indigo-300 hover:shadow-md hover:-translate-y-0.5"
    },
    {
      title: "Tools",
      icon: <Wrench size={18} />,
      items: skillsAnalysis.tools,
      color: "bg-emerald-50 text-emerald-700 border-emerald-200 hover:bg-emerald-100 hover:border-emerald-300 hover:shadow-md hover:-translate-y-0.5"
    },
    {
      title: "Databases",
      icon: <Database size={18} />,
      items: skillsAnalysis.databases,
      color: "bg-amber-50 text-amber-700 border-amber-200 hover:bg-amber-100 hover:border-amber-300 hover:shadow-md hover:-translate-y-0.5"
    }
  ];

  return (
    <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-100 space-y-8 hover:shadow-2xl transition-shadow duration-300">

      {/* Header with enhanced styling */}
      <div className="flex items-center gap-3 pb-4 border-b border-gray-100">
        <div className="p-2.5 bg-gradient-to-br from-indigo-500 to-indigo-600 rounded-xl shadow-lg shadow-indigo-200">
          <Briefcase className="text-white" size={24} />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-gray-800">
            Skills Analysis
          </h2>
          <p className="text-sm text-gray-500 mt-0.5">
            Technical expertise breakdown
          </p>
        </div>
      </div>

      {/* Stats Cards with enhanced design */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
        {/* Experience Card - Enhanced */}
        <div className="group relative overflow-hidden rounded-xl bg-gradient-to-br from-indigo-50 to-indigo-100/50 p-6 border border-indigo-100 hover:border-indigo-200 transition-all duration-300">
          <div className="absolute top-0 right-0 w-20 h-20 bg-indigo-200/20 rounded-bl-full" />
          <div className="relative">
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
            <div className="mt-3 h-1.5 w-full bg-indigo-200/50 rounded-full overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-indigo-500 to-indigo-600 rounded-full transition-all duration-500"
                style={{ width: `${Math.min((skillsAnalysis.years_of_experience || 0) * 10, 100)}%` }}
              />
            </div>
          </div>
        </div>

        {/* Level Card - Enhanced */}
        <div className="group relative overflow-hidden rounded-xl bg-gradient-to-br from-emerald-50 to-emerald-100/50 p-6 border border-emerald-100 hover:border-emerald-200 transition-all duration-300">
          <div className="absolute top-0 right-0 w-20 h-20 bg-emerald-200/20 rounded-bl-full" />
          <div className="relative">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-semibold text-emerald-600 uppercase tracking-wider">Level</span>
              <TrendingUp size={16} className="text-emerald-400" />
            </div>
            <div className="flex items-center gap-3">
              <span className="text-3xl font-bold text-gray-800">
                {skillsAnalysis.experience_level || "N/A"}
              </span>
              {skillsAnalysis.experience_level && (
                <span className="px-2.5 py-1 text-xs font-medium bg-emerald-100 text-emerald-700 rounded-full">
                  {skillsAnalysis.experience_level === "Senior" ? "Senior Level" : 
                   skillsAnalysis.experience_level === "Mid" ? "Mid Level" : "Junior Level"}
                </span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Skill Sections with enhanced design */}
      <div className="space-y-6">
        {sections.map(
          (section, idx) =>
            section.items?.length > 0 && (
              <div key={idx} className="space-y-3">
                {/* Section Title with icon and count */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className={`p-1.5 rounded-lg ${
                      section.color.split(' ')[0]
                    }`}>
                      {section.icon}
                    </div>
                    <h3 className="font-semibold text-gray-700">
                      {section.title}
                    </h3>
                  </div>
                  <span className="text-xs font-medium px-2 py-1 bg-gray-100 text-gray-600 rounded-full">
                    {section.items.length}
                  </span>
                </div>

                {/* Skills with enhanced badges */}
                <div className="flex flex-wrap gap-2">
                  {section.items.map((item, i) => (
                    <span
                      key={i}
                      className={`
                        px-4 py-2 rounded-lg text-sm font-medium
                        border transition-all duration-200 cursor-default
                        ${section.color}
                      `}
                    >
                      {item}
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