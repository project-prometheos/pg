// Browse all problems page
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

interface Collection {
  id: string;
  name: string;
  description: string;
  problem_count: number;
}

const BrowsePage = () => {
  const navigate = useNavigate();
  const [problems, setProblems] = useState<any[]>([]);
  const [collections, setCollections] = useState<Collection[]>([]);
  const [selectedCollection, setSelectedCollection] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSubject, setSelectedSubject] = useState<string | null>(null);
  const [facets, setFacets] = useState<any>({ subjects: [], types: [], categories: [] });

  // Load collections on mount
  useEffect(() => {
    const loadCollections = async () => {
      try {
        const response = await fetch('/api/problems/collections/list');
        if (response.ok) {
          const data = await response.json();
          setCollections(data);
        }
      } catch (err) {
        console.error('Error loading collections:', err);
      }
    };
    loadCollections();
  }, []);

  // Load problems when filters change
  useEffect(() => {
    const loadProblems = async () => {
      setLoading(true);
      setError(null);
      try {
        // Build query params
        const params = new URLSearchParams();
        params.set('limit', '200');  // API max is 500
        if (selectedCollection) {
          params.set('collection', selectedCollection);
        }
        if (searchQuery) {
          params.set('q', searchQuery);
        }
        if (selectedSubject) {
          params.set('subjects', selectedSubject);
        }

        const response = await fetch(`/api/problems/search?${params}`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();

        if (data.problems && Array.isArray(data.problems)) {
          setProblems(data.problems);
          setFacets(data.facets || { subjects: [], types: [], categories: [] });
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
  }, [selectedCollection, searchQuery, selectedSubject]);

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
      <div className="max-w-7xl mx-auto p-6">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            WeBWorK Problem Library
          </h1>
          <p className="text-gray-600">
            Browse and solve {problems.length} mathematics problems
          </p>
        </div>

        {/* Filters Section */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          {/* Search Bar */}
          <div className="mb-4">
            <input
              type="text"
              placeholder="Search problems..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Collection Tabs */}
          <div className="mb-4">
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => setSelectedCollection(null)}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  selectedCollection === null
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                All Collections ({collections.reduce((sum, c) => sum + c.problem_count, 0)})
              </button>
              {collections.map((collection) => (
                <button
                  key={collection.id}
                  onClick={() => setSelectedCollection(collection.id)}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                    selectedCollection === collection.id
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {collection.name} ({collection.problem_count})
                </button>
              ))}
            </div>
          </div>

          {/* Subject Filter */}
          {facets.subjects && facets.subjects.length > 0 && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Filter by Subject
              </label>
              <div className="flex flex-wrap gap-2">
                <button
                  onClick={() => setSelectedSubject(null)}
                  className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                    selectedSubject === null
                      ? 'bg-purple-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  All Subjects
                </button>
                {facets.subjects.slice(0, 10).map((subject: string) => (
                  <button
                    key={subject}
                    onClick={() => setSelectedSubject(subject)}
                    className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                      selectedSubject === subject
                        ? 'bg-purple-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {subject}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Results Count */}
        {!loading && (
          <div className="mb-4 text-sm text-gray-600">
            Showing {problems.length} {problems.length === 1 ? 'problem' : 'problems'}
            {selectedCollection && ` from ${collections.find(c => c.id === selectedCollection)?.name}`}
            {selectedSubject && ` in ${selectedSubject}`}
          </div>
        )}

        {/* Problems Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {problems.map((problem: any) => (
            <div
              key={problem.id}
              onClick={() => handleProblemClick(problem.id)}
              className="bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow cursor-pointer p-5 border border-gray-200 hover:border-blue-300"
            >
              {/* Collection Badge */}
              <div className="mb-2">
                <span className="px-2 py-0.5 bg-indigo-100 text-indigo-800 text-xs font-medium rounded">
                  {problem.source_collection.toUpperCase()}
                </span>
              </div>

              {/* Problem Title */}
              <h3 className="text-base font-semibold text-gray-900 mb-2 line-clamp-1">
                {problem.name}
              </h3>

              {/* Description */}
              {problem.description && (
                <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                  {problem.description}
                </p>
              )}

              {/* Metadata Tags */}
              <div className="flex flex-wrap gap-1.5 mb-2">
                {problem.metadata?.subjects?.slice(0, 2).map((subject: string) => (
                  <span
                    key={subject}
                    className="px-2 py-0.5 bg-blue-50 text-blue-700 text-xs rounded-full"
                  >
                    {subject}
                  </span>
                ))}
                {problem.metadata?.types?.slice(0, 1).map((type: string) => (
                  <span
                    key={type}
                    className="px-2 py-0.5 bg-green-50 text-green-700 text-xs rounded-full"
                  >
                    {type}
                  </span>
                ))}
              </div>

              {/* Problem ID */}
              <p className="text-xs text-gray-400 font-mono truncate mt-2">
                {problem.id}
              </p>
            </div>
          ))}
        </div>

        {/* Empty State */}
        {problems.length === 0 && !loading && (
          <div className="text-center py-16 bg-white rounded-lg border border-gray-200">
            <svg className="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p className="text-gray-500 text-lg font-medium mb-1">No problems found</p>
            <p className="text-gray-400 text-sm">Try adjusting your filters</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default BrowsePage;

