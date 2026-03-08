import { Briefcase, MapPin, DollarSign } from 'lucide-react';

function JobMatches({ data }) {
    // Extract matched jobs from data (safely)
    const matches = data?.match_results?.matched_jobs || [];

    // If no matches, show empty state
    if (matches.length === 0) {
        return (
            <div className="card">
                <h2 className="flex items-center gap-2 text-2xl font-bold text-gray-800 mb-6">
                    <Briefcase size={28} />
                    Job Matches
                </h2>
                <p className="text-center text-gray-500 py-12">
                    No job matches found
                </p>
            </div>
        );
    }

    // If we have matches, show them
    return (
        <div className="card">
            {/* Heading */}
            <h2 className="flex items-center gap-2 text-2xl font-bold text-gray-800 mb-2">
                <Briefcase size={28} />
                Top Job Matches
            </h2>
            <p className="text-gray-600 mb-6">
                Found {matches.length} matching positions
            </p>

            {/* Job Cards */}
            <div className="space-y-4">
                {matches.map((job, index) => (
                    <div
                        key={index}
                        className="p-6 border-2 border-gray-200 rounded-xl hover:border-primary hover:shadow-lg transition-all"
                    >
                        {/* Header: Rank + Title + Score */}
                        <div className="flex justify-between items-start mb-4">
                            <div className="flex items-center gap-3">
                                {/* Rank Badge */}
                                <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center font-bold text-gray-600">
                                    #{index + 1}
                                </div>
                                {/* Job Title */}
                                <h3 className="text-xl font-semibold text-gray-800">
                                    {job.title}
                                </h3>
                            </div>
                            {/* Match Score */}
                            <span className="px-4 py-2 bg-green-500 text-white rounded-full font-bold text-sm">
                                {job.match_score}
                            </span>
                        </div>

                        {/* Location + Salary */}
                        <div className="flex flex-wrap gap-4 mb-4">
                            <div className="flex items-center gap-2 text-gray-600">
                                <MapPin size={16} className="text-primary" />
                                <span>{job.location}</span>
                            </div>
                            <div className="flex items-center gap-2 text-gray-600">
                                <DollarSign size={16} className="text-primary" />
                                <span>{job.salary_range}</span>
                            </div>
                        </div>

                        {/* Required Skills (if exists) */}
                        {job.requirements?.length > 0 && (
                            <div className="pt-4 border-t border-gray-200">
                                <h4 className="text-sm font-semibold text-gray-700 mb-2">
                                    Required Skills:
                                </h4>
                                <div className="flex flex-wrap gap-2">
                                    {/* Show first 5 skills */}
                                    {job.requirements.slice(0, 5).map((req, i) => (
                                        <span
                                            key={i}
                                            className="px-3 py-1 bg-gray-100 text-gray-700 rounded-lg text-sm"
                                        >
                                            {req}
                                        </span>
                                    ))}
                                    {/* Show "+X more" if more than 5 */}
                                    {job.requirements.length > 5 && (
                                        <span className="px-3 py-1 bg-primary text-white rounded-lg text-sm">
                                            +{job.requirements.length - 5} more
                                        </span>
                                    )}
                                </div>
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
}

export default JobMatches;