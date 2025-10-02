// Browse all problems page
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const BrowsePage = () => {
  const navigate = useNavigate();
  const [problems, setProblems] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load problems on mount
  useEffect(() => {
    const loadProblems = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await fetch('/api/problems/search?limit=100');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        console.log('API Response:', data);
        
        // Handle the response structure from our API
        if (data.problems && Array.isArray(data.problems)) {
          setProblems(data.problems);
        } else {
          setError('Unexpected API response format');
        }
      } catch (err: any) {
        console.error('Error loading problems:', err);
        setError(err.message || 'Failed to load problems');
      } finally {
        setLoading(false);
      }
    };
    
    loadProblems();
  }, []);

  const handleProblemClick = (problemId: string) => {
    // Navigate to database problem page
    navigate(`/db/${problemId}?seed=0`);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl font-bold mb-6">Loading problems...</h1>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl font-bold mb-6 text-red-600">Error</h1>
          <p className="text-gray-700">{error}</p>
          <p className="mt-4 text-sm text-gray-500">
            Make sure the backend server is running on port 8000
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto p-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            WeBWorK Problem Library
          </h1>
          <p className="text-lg text-gray-600">
            {problems.length} problems available from the database
          </p>
          <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
            <p className="text-sm text-green-800">
              <strong>✅ Ready!</strong> Browse {problems.length} problems and click any card to view and solve it!
              <br />
              <span className="text-xs text-green-700">Powered by Pure Python PG Renderer</span>
            </p>
          </div>
        </div>

        {/* Problems Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {problems.map((problem: any) => (
            <div
              key={problem.id}
              onClick={() => handleProblemClick(problem.id)}
              className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow cursor-pointer p-6 border border-gray-200"
            >
              {/* Problem Title */}
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {problem.name}
              </h3>

              {/* Description */}
              {problem.description && (
                <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                  {problem.description}
                </p>
              )}

              {/* Metadata Tags */}
              <div className="flex flex-wrap gap-2 mb-3">
                {problem.metadata?.subjects?.slice(0, 2).map((subject: string) => (
                  <span
                    key={subject}
                    className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
                  >
                    {subject}
                  </span>
                ))}
                {problem.metadata?.types?.slice(0, 1).map((type: string) => (
                  <span
                    key={type}
                    className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full"
                  >
                    {type}
                  </span>
                ))}
              </div>

              {/* Problem ID */}
              <p className="text-xs text-gray-400 font-mono truncate">
                {problem.id}
              </p>
            </div>
          ))}
        </div>

        {/* Empty State */}
        {problems.length === 0 && !loading && (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">No problems found</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default BrowsePage;

