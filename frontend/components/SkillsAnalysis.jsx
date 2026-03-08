import { Briefcase, Award, TrendingUp } from 'lucide-react';

function SkillsAnalysis({ data }) {
  const skillsAnalysis = data?.analysis_results?.skills_analysis || {};

  const sections = [
    { title: 'Technical Skills', icon: <Award size={20} />, items: skillsAnalysis.technical_skills, color: 'from-primary to-primary/70' },
    { title: 'Tools', icon: '🔧', items: skillsAnalysis.tools, color: 'from-green-400 to-green-300' },
    { title: 'Databases', icon: '🗄️', items: skillsAnalysis.databases, color: 'from-orange-400 to-orange-300' },
    { title: 'Domain Expertise', icon: <TrendingUp size={20} />, items: skillsAnalysis.domain_expertise, color: 'from-purple-400 to-purple-300' },
  ];

  return (
    <div className="p-6 md:p-8 bg-white rounded-2xl shadow-xl space-y-8">
      {/* Heading */}
      <h2 className="flex items-center gap-2 text-2xl font-bold text-gray-800">
        <Briefcase size={28} />
        Skills Analysis
      </h2>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
        <div className="flex flex-col items-center justify-center p-6 bg-blue-50 rounded-xl shadow-md min-h-[120px]">
          <span className="text-gray-600">Experience : </span>
          <span className="text-3xl font-bold text-primary mt-2">
            {skillsAnalysis.years_of_experience || 0} <span className="text-lg font-normal"> years</span>
          </span>
        </div>

        <div className="flex flex-col items-center justify-center p-6 bg-blue-50 rounded-xl shadow-md min-h-[120px]">
          <span className="text-gray-600">Level : </span>
          <span className="text-3xl font-bold text-primary mt-2">{skillsAnalysis.experience_level || 'N/A'}</span>
        </div>

        <div className="flex flex-col items-center justify-center p-6 bg-blue-50 rounded-xl shadow-md min-h-[120px]">
          <span className="text-gray-600">Skills : </span>
          <span className="text-3xl font-bold text-primary mt-2">{skillsAnalysis.technical_skills?.length || 0}</span>
        </div>
      </div>

      {/* Skills Sections */}
      {sections.map((section, idx) =>
        section.items?.length > 0 && (
          <div key={idx}>
            <h3 className="flex items-center gap-2 text-lg font-semibold text-gray-700 mb-3">
              {section.icon} {section.title}
            </h3>
            <div className="flex flex-wrap gap-3">
              {section.items.map((item, i) => (
                <span
                  key={i}
                  className={`
                    bg-gradient-to-r ${section.color} 
                    text-black font-medium text-sm px-2 py-1 rounded-full 
                    shadow hover:scale-105 transition-transform truncate 
                  `}
                  title={item} // Shows full text on hover if truncated
                >
                  {item}
                </span>
              ))}
            </div>
          </div>
        )
      )}
    </div>
  );
}

export default SkillsAnalysis;