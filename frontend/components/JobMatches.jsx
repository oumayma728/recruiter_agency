import { Briefcase, MapPin, DollarSign, ExternalLink } from "lucide-react";

function JobMatches({ data }) {
const matches = data?.match_results?.matched_jobs || [];

if (matches.length === 0) {
    return (
    <div className="bg-white/80 backdrop-blur rounded-2xl shadow-lg p-10 border border-gray-200">
        <h2 className="flex items-center gap-3 text-2xl font-bold text-gray-800 mb-6">
            <Briefcase className="text-indigo-600" size={28} />
            Job Matches
        </h2>

        <p className="text-center text-gray-500 py-16 text-lg">
            No job matches found
        </p>
        </div>
    );
}

    return (
    <div className="bg-white/80 backdrop-blur rounded-2xl shadow-lg p-10 border border-gray-200">
    
      {/* Header */}
      <div className="mb-10 flex items-center justify-between">
        <div>
          <h2 className="flex items-center gap-3 text-2xl font-bold text-gray-800">
            <Briefcase className="text-indigo-600" size={28} />
            Top Job Matches
          </h2>

          <p className="text-gray-500 mt-2">
            Found <span className="font-semibold">{matches.length}</span> matching positions
          </p>
        </div>

        <div className="text-sm text-gray-400">
          AI Powered Matching
        </div>
      </div>

      {/* Job Cards */}
      <div className="space-y-8">
        {matches.map((job, index) => (
          <div
            key={index}
            className="group relative rounded-xl border border-gray-200 bg-white p-6 transition-all duration-300 hover:shadow-xl hover:-translate-y-1"
          >
            
            {/* Gradient hover border */}
            <div className="absolute inset-0 rounded-xl opacity-0 group-hover:opacity-100 transition pointer-events-none bg-gradient-to-r from-indigo-500/10 to-purple-500/10" />

            {/* Top */}
            <div className="flex items-start justify-between mb-4 relative">
              <div className="flex gap-4 items-start">
                
                {/* Rank */}
                <div className="text-black flex items-center justify-center font-bold shadow">
                #{index + 1}
                </div>

                {/* Title */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-800">
                    {job.title}
                  </h3>

                  <p className="text-gray-500 text-sm">
                    {job.company}
                  </p>
                </div>
              </div>

            </div>

            {/* Match score progress */}
            <div className="mb-5">
            <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                className="h-full bg-gradient-to-r from-green-400 to-emerald-600"
                style={{ width: `${job.match_score.replace("%","")}%` }}
                />
            </div>
            </div>

            {/* Info */}
            <div className="flex flex-wrap gap-6 text-sm text-gray-600 mb-4">
            <div className="flex items-center gap-2">
                <MapPin size={16} className="text-indigo-500" />
                {job.location}
            </div>

            <div className="flex items-center gap-2">
                <DollarSign size={16} className="text-indigo-500" />
                {job.salary_range}
            </div>
            </div>

            {/* Skills */}
            {job.requirements?.length > 0 && (
            <div className="mb-6">

                <div className="flex flex-wrap gap-2">

                {job.requirements.length > 5 && (
                    <span className="px-3 py-1 text-xs rounded-full bg-gray-100 text-gray-600">
                    +{job.requirements.length - 5} more
                    </span>
                )}
                </div>
            </div>
            )}

            {/* Button */}
            {job.url && (
            <a
                href={job.url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 text-sm font-semibold px-4 py-2 rounded-lg bg-green-800 text-black hover:scale-105 transition-transform"
            >
                View Job on {job.source}
                <ExternalLink size={16} />
            </a>
            )}
        </div>
        ))}
    </div>
    </div>
);
}

export default JobMatches;