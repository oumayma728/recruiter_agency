import { Lightbulb, CheckCircle, AlertCircle, ArrowRight } from 'lucide-react';

function Recommendations({ data }) {
    // Extract and map data from your backend structure
    const recommendationResults = data?.recommendation_results || {};
    const enhancementResults = data?.enhancement_results || {};
    const matchResults = data?.match_results || {};
    
    // Use data directly from backend (already processed by orchestrator)
    const mappedRecommendation = {
        hiring_recommendation: recommendationResults?.hiring_recommendation || 'PASS',
        overall_assessment: recommendationResults?.overall_assessment || 'No assessment available',
        confidence_level: recommendationResults?.confidence_level || 'LOW',
        strengths: recommendationResults?.strengths || [],
        concerns: recommendationResults?.concerns || [],
        next_steps: recommendationResults?.next_steps || [],
        interview_questions: recommendationResults?.interview_questions || []
    };
    
    // Get profile enhancement recommendations
    const enhancementRecommendations = enhancementResults?.recommendations || [];

    return (
        <div className="space-y-6">
            {/* Hiring Recommendation Card */}
            <div className="card">
                <h2 className="flex items-center gap-2 text-2xl font-bold text-gray-800 mb-6">
                    <Lightbulb size={28} />
                    Hiring Recommendation
                </h2>

                {/* Decision Badge */}
                {mappedRecommendation.hiring_recommendation && (
                    <div className={`inline-block px-6 py-3 rounded-lg font-bold text-lg mb-4 ${
                        mappedRecommendation.hiring_recommendation === 'PROCEED'
                            ? 'bg-green-500 text-white'
                            : mappedRecommendation.hiring_recommendation === 'CONSIDER'
                                ? 'bg-orange-500 text-white'
                                : 'bg-red-500 text-white'
                    }`}>
                        {mappedRecommendation.hiring_recommendation}
                    </div>
                )}

                {/* Overall Assessment */}
                <p className="text-gray-700 leading-relaxed mb-6">
                    {mappedRecommendation.overall_assessment || 'No assessment available'}
                </p>

                {/* Confidence Level */}
                {mappedRecommendation.confidence_level && (
                    <div className="p-4 bg-blue-50 rounded-lg mb-6">
                        <span className="text-gray-600">Confidence: </span>
                        <strong className="text-primary uppercase">
                            {mappedRecommendation.confidence_level}
                        </strong>
                    </div>
                )}

                {/* Strengths */}
                {mappedRecommendation.strengths?.length > 0 && (
                    <div className="mb-6 pt-6 border-t border-gray-200">
                        <h3 className="flex items-center gap-2 text-lg font-semibold text-gray-700 mb-3">
                            <CheckCircle size={20} className="text-green-500" />
                            Strengths
                        </h3>
                        <ul className="space-y-2">
                            {mappedRecommendation.strengths.map((strength, i) => (
                                <li key={i} className="text-gray-600 leading-relaxed pl-6 relative before:content-['✓'] before:absolute before:left-0 before:text-green-500 before:font-bold">
                                    {strength}
                                </li>
                            ))}
                        </ul>
                    </div>
                )}

                {/* Concerns */}
                {mappedRecommendation.concerns?.length > 0 && (
                    <div className="mb-6 pt-6 border-t border-gray-200">
                        <h3 className="flex items-center gap-2 text-lg font-semibold text-gray-700 mb-3">
                            <AlertCircle size={20} className="text-orange-500" />
                            Concerns
                        </h3>
                        <ul className="space-y-2">
                            {mappedRecommendation.concerns.map((concern, i) => (
                                <li key={i} className="text-gray-600 leading-relaxed pl-6 relative before:content-['⚠'] before:absolute before:left-0 before:text-orange-500">
                                    {concern}
                                </li>
                            ))}
                        </ul>
                    </div>
                )}

                {/* Next Steps */}
                {mappedRecommendation.next_steps?.length > 0 && (
                    <div className="mb-6 pt-6 border-t border-gray-200">
                        <h3 className="flex items-center gap-2 text-lg font-semibold text-gray-700 mb-3">
                            <ArrowRight size={20} className="text-primary" />
                            Next Steps
                        </h3>
                        <ol className="space-y-2 list-decimal list-inside">
                            {mappedRecommendation.next_steps.map((step, i) => (
                                <li key={i} className="text-gray-600 leading-relaxed">
                                    {step}
                                </li>
                            ))}
                        </ol>
                    </div>
                )}

                {/* Interview Questions */}
                {mappedRecommendation.interview_questions?.length > 0 && (
                    <div className="pt-6 border-t border-gray-200">
                        <h3 className="text-lg font-semibold text-gray-700 mb-3">
                            💬 Suggested Interview Questions
                        </h3>
                        <ul className="space-y-2">
                            {mappedRecommendation.interview_questions.map((q, i) => (
                                <li key={i} className="text-gray-600 leading-relaxed pl-6 relative before:content-['Q:'] before:absolute before:left-0 before:text-primary before:font-bold">
                                    {q}
                                </li>
                            ))}
                        </ul>
                    </div>
                )}
            </div>

            {/* Profile Enhancement Card */}
            {enhancementRecommendations.length > 0 && (
                <div className="card">
                    <h2 className="text-2xl font-bold text-gray-800 mb-2">
                        ✨ Profile Enhancement
                    </h2>
                    <p className="text-gray-600 mb-6">
                        Suggestions to improve this profile
                    </p>

                    <div className="space-y-4">
                        {enhancementRecommendations.map((rec, i) => (
                            <div key={i} className="flex gap-4 p-6 bg-blue-50 rounded-xl">
                                <div className="w-8 h-8 bg-primary text-white rounded-full flex items-center justify-center font-bold flex-shrink-0">
                                    {i + 1}
                                </div>
                                <p className="text-gray-700 leading-relaxed">
                                    {rec}
                                </p>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}

// Helper functions to map backend data to UI format
function getHiringRecommendation(matchResults) {
    const matchedJobs = matchResults?.matched_jobs || [];
    if (matchedJobs.length === 0) return 'CONSIDER';
    const topScore = parseInt(matchedJobs[0]?.match_score || '0%');
    if (topScore >= 70) return 'PROCEED';
    if (topScore >= 50) return 'CONSIDER';
    return 'PASS';
}

function generateOverallAssessment(matchResults, enhancementResults) {
    const matchedJobs = matchResults?.matched_jobs || [];
    if (matchedJobs.length === 0) {
        return "No strong matches found. Consider expanding search criteria or adding relevant skills.";
    }
    const topMatch = matchedJobs[0];
    const enhancementCount = enhancementResults?.recommendations?.length || 0;
    
    return `Candidate shows strong potential for ${topMatch?.title} at ${topMatch?.company} with a ${topMatch?.match_score} match score. ${enhancementCount} profile improvements suggested.`;
}

function calculateConfidence(matchResults) {
    const matchedJobs = matchResults?.matched_jobs || [];
    if (matchedJobs.length === 0) return 'LOW';
    const topScore = parseInt(matchedJobs[0]?.match_score || '0%');
    if (topScore >= 70) return 'HIGH';
    if (topScore >= 50) return 'MEDIUM';
    return 'LOW';
}

function extractStrengths(analysisResults) {
    const skills = analysisResults?.skills_analysis?.technical_skills || [];
    if (skills.length === 0) return ['Technical skills not detected'];
    return skills.slice(0, 5).map(skill => `Strong proficiency in ${skill}`);
}

function extractConcerns(matchResults) {
    const concerns = [];
    const matchedJobs = matchResults?.matched_jobs || [];
    if (matchedJobs.length === 0) {
        concerns.push("No direct job matches found");
    }
    if (matchedJobs.length > 0 && parseInt(matchedJobs[0]?.match_score || '0%') < 60) {
        concerns.push("Match score below 60% - skill gap may exist");
    }
    return concerns;
}

function generateNextSteps(matchResults) {
    const steps = [];
    const matchedJobs = matchResults?.matched_jobs || [];
    if (matchedJobs.length > 0) {
        steps.push(`Schedule technical interview for ${matchedJobs[0]?.title} position`);
        steps.push("Request portfolio review or code sample");
    } else {
        steps.push("Expand job search criteria");
        steps.push("Consider additional skill development");
    }
    steps.push("Follow up with candidate for additional information");
    return steps;
}

function generateInterviewQuestions(matchResults) {
    const matchedJobs = matchResults?.matched_jobs || [];
    if (matchedJobs.length === 0) {
        return [
            "What are your strongest technical skills?",
            "Describe a challenging project you worked on",
            "Where do you see yourself in 2 years?"
        ];
    }
    return [
        `Tell us about your experience with technologies relevant to ${matchedJobs[0]?.title}`,
        "How do you approach learning new technologies?",
        "Describe a situation where you had to solve a complex technical problem"
    ];
}

export default Recommendations;