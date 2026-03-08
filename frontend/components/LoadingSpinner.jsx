import { Loader2 } from 'lucide-react';

function LoadingSpinner({ message = "Analyzing resume..." }) {
    return (
        <div className="card text-center">
            <Loader2 className="mx-auto mb-4 text-primary animate-spin" size={48} />

            <p className="text-xl font-semibold text-gray-800 mb-6">
                {message}
            </p>

            <div className="flex flex-col gap-2 items-center">
                <div className="px-4 py-2 bg-blue-50 rounded-full text-sm text-gray-600 animate-pulse">
                    Extracting data...
                </div>
                <div className="px-4 py-2 bg-blue-50 rounded-full text-sm text-gray-600 animate-pulse delay-150">
                    Analyzing skills...
                </div>
                <div className="px-4 py-2 bg-blue-50 rounded-full text-sm text-gray-600 animate-pulse delay-300">
                    Matching jobs...
                </div>
            </div>
        </div>
    );
}

export default LoadingSpinner;