import { Lightbulb, CheckCircle, AlertCircle, ArrowRight } from 'lucide-react';

function Recommendations({ data }) {
    // Extract data safely
    const recommendation = data?.recommendation || {};
    const enhancement = data?.enhancement_results || {};

    return (
        <div className="space-y-6">
            {/* Hiring Recommendation Card */}
            <div className="card">
                {/* Heading */}
                <h2 className="flex items-center gap-2 text-2xl font-bold text-gray-800 mb-6">
                    <Lightbulb size={28} />
                    Hiring Recommendation
                </h2>

                {/* Decision Badge (PROCEED/CONSIDER/PASS) */}
                {recommendation.hiring_recommendation && (
                    <div className={`inline-block px-6 py-3 rounded-lg font-bold text-lg mb-4 ${recommendation.hiring_recommendation === 'PROCEED'
                            ? 'bg-green-500 text-white'
                            : recommendation.hiring_recommendation === 'CONSIDER'
                                ? 'bg-orange-500 text-white'
                                : 'bg-red-500 text-white'
                        }`}>
                        {recommendation.hiring_recommendation}
                    </div>
                )}

                {/* Overall Assessment */}
                <p className="text-gray-700 leading-relaxed mb-6">
                    {recommendation.overall_assessment || 'No assessment available'}
                </p>

                {/* Confidence Level */}
                {recommendation.confidence_level && (
                    <div className="p-4 bg-blue-50 rounded-lg mb-6">
                        <span className="text-gray-600">Confidence: </span>
                        <strong className="text-primary uppercase">
                            {recommendation.confidence_level}
                        </strong>
                    </div>
                )}

                {/* Strengths */}
                {recommendation.strengths?.length > 0 && (
                    <div className="mb-6 pt-6 border-t border-gray-200">
                        <h3 className="flex items-center gap-2 text-lg font-semibold text-gray-700 mb-3">
                            <CheckCircle size={20} className="text-green-500" />
                            Strengths
                        </h3>
                        <ul className="space-y-2">
                            {recommendation.strengths.map((strength, i) => (
                                <li key={i} className="text-gray-600 leading-relaxed pl-6 relative before:content-['✓'] before:absolute before:left-0 before:text-green-500 before:font-bold">
                                    {strength}
                                </li>
                            ))}
                        </ul>
                    </div>
                )}

                {/* Concerns */}
                {recommendation.concerns?.length > 0 && (
                    <div className="mb-6 pt-6 border-t border-gray-200">
                        <h3 className="flex items-center gap-2 text-lg font-semibold text-gray-700 mb-3">
                            <AlertCircle size={20} className="text-orange-500" />
                            Concerns
                        </h3>
                        <ul className="space-y-2">
                            {recommendation.concerns.map((concern, i) => (
                                <li key={i} className="text-gray-600 leading-relaxed pl-6 relative before:content-['⚠'] before:absolute before:left-0 before:text-orange-500">
                                    {concern}
                                </li>
                            ))}
                        </ul>
                    </div>
                )}

                {/* Next Steps */}
                {recommendation.next_steps?.length > 0 && (
                    <div className="mb-6 pt-6 border-t border-gray-200">
                        <h3 className="flex items-center gap-2 text-lg font-semibold text-gray-700 mb-3">
                            <ArrowRight size={20} className="text-primary" />
                            Next Steps
                        </h3>
                        <ol className="space-y-2 list-decimal list-inside">
                            {recommendation.next_steps.map((step, i) => (
                                <li key={i} className="text-gray-600 leading-relaxed">
                                    {step}
                                </li>
                            ))}
                        </ol>
                    </div>
                )}

                {/* Interview Questions */}
                {recommendation.interview_questions?.length > 0 && (
                    <div className="pt-6 border-t border-gray-200">
                        <h3 className="text-lg font-semibold text-gray-700 mb-3">
                            💬 Suggested Interview Questions
                        </h3>
                        <ul className="space-y-2">
                            {recommendation.interview_questions.map((q, i) => (
                                <li key={i} className="text-gray-600 leading-relaxed pl-6 relative before:content-['Q:'] before:absolute before:left-0 before:text-primary before:font-bold">
                                    {q}
                                </li>
                            ))}
                        </ul>
                    </div>
                )}
            </div>

            {/* Profile Enhancement Card */}
            {enhancement.recommendations?.length > 0 && (
                <div className="card">
                    <h2 className="text-2xl font-bold text-gray-800 mb-2">
                        ✨ Profile Enhancement
                    </h2>
                    <p className="text-gray-600 mb-6">
                        Suggestions to improve this profile
                    </p>

                    <div className="space-y-4">
                        {enhancement.recommendations.map((rec, i) => (
                            <div key={i} className="flex gap-4 p-6 bg-blue-50 rounded-xl">
                                <div className="w-8 h-8 bg-primary text-white rounded-full flex items-center justify-center font-bold flex-shrink-0">
                                    {i + 1}
                                </div>
                                <p className="text-gray-700 leading-relaxed">
                                    - {rec}
                                </p>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}

export default Recommendations;