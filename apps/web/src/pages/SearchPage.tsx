// Search page component with filtering and results
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';

import { 
  searchProblems, 
  getSearchFacets, 
  type SearchFilters, 
  type SearchResponse,
  type FacetResponse 
} from '../services/searchApi';

interface SearchPageProps {}

const SearchPage: React.FC<SearchPageProps> = () => {
  const navigate = useNavigate();
  const [filters, setFilters] = useState<SearchFilters>({
    query: '',
    types: [],
    subjects: [],
    categories: [],
    keywords: [],
    macros: [],
    limit: 20,
    offset: 0
  });
  
  const [searchResults, setSearchResults] = useState<SearchResponse[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  // Fetch search facets
  const { data: facets } = useQuery({
    queryKey: ['searchFacets'],
    queryFn: getSearchFacets,
  });

  // Perform search
  const performSearch = async () => {
    if (!filters.query && !filters.types?.length && !filters.subjects?.length && 
        !filters.categories?.length && !filters.keywords?.length && !filters.macros?.length) {
      setSearchResults([]);
      return;
    }

    setIsSearching(true);
    try {
      const results = await searchProblems(filters);
      setSearchResults(results);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setIsSearching(false);
    }
  };

  // Search when filters change
  useEffect(() => {
    const timeoutId = setTimeout(performSearch, 300); // Debounce
    return () => clearTimeout(timeoutId);
  }, [filters]);

  const handleFilterChange = (key: keyof SearchFilters, value: any) => {
    setFilters(prev => ({
      ...prev,
      [key]: value,
      offset: 0 // Reset pagination
    }));
  };

  const handleMultiSelectChange = (key: keyof SearchFilters, value: string, checked: boolean) => {
    setFilters(prev => {
      const currentArray = (prev[key] as string[]) || [];
      const newArray = checked 
        ? [...currentArray, value]
        : currentArray.filter(item => item !== value);
      
      return {
        ...prev,
        [key]: newArray,
        offset: 0
      };
    });
  };

  const loadMore = () => {
    setFilters(prev => ({
      ...prev,
      offset: (prev.offset || 0) + (prev.limit || 20)
    }));
  };

  const selectProblem = (problemId: string) => {
    navigate(`/p/${problemId}`);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Problem Search</h1>
          <p className="mt-2 text-gray-600">
            Search and discover problems from the WeBWorK PG library
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Filters Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold mb-4">Filters</h2>
              
              {/* Search Query */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Search Query
                </label>
                <input
                  type="text"
                  value={filters.query || ''}
                  onChange={(e) => handleFilterChange('query', e.target.value)}
                  placeholder="Search problems..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {/* Problem Types */}
              {facets?.types && (
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Problem Types
                  </label>
                  <div className="space-y-2">
                    {facets.types.map(type => (
                      <label key={type} className="flex items-center">
                        <input
                          type="checkbox"
                          checked={filters.types?.includes(type) || false}
                          onChange={(e) => handleMultiSelectChange('types', type, e.target.checked)}
                          className="mr-2"
                        />
                        <span className="text-sm text-gray-700 capitalize">{type}</span>
                      </label>
                    ))}
                  </div>
                </div>
              )}

              {/* Subjects */}
              {facets?.subjects && (
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Subjects
                  </label>
                  <div className="space-y-2 max-h-40 overflow-y-auto">
                    {facets.subjects.map(subject => (
                      <label key={subject} className="flex items-center">
                        <input
                          type="checkbox"
                          checked={filters.subjects?.includes(subject) || false}
                          onChange={(e) => handleMultiSelectChange('subjects', subject, e.target.checked)}
                          className="mr-2"
                        />
                        <span className="text-sm text-gray-700 capitalize">{subject}</span>
                      </label>
                    ))}
                  </div>
                </div>
              )}

              {/* Categories */}
              {facets?.categories && (
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Categories
                  </label>
                  <div className="space-y-2 max-h-40 overflow-y-auto">
                    {facets.categories.map(category => (
                      <label key={category} className="flex items-center">
                        <input
                          type="checkbox"
                          checked={filters.categories?.includes(category) || false}
                          onChange={(e) => handleMultiSelectChange('categories', category, e.target.checked)}
                          className="mr-2"
                        />
                        <span className="text-sm text-gray-700 capitalize">{category}</span>
                      </label>
                    ))}
                  </div>
                </div>
              )}

              {/* Macros */}
              {facets?.macros && (
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Macros
                  </label>
                  <div className="space-y-2 max-h-40 overflow-y-auto">
                    {facets.macros.slice(0, 20).map(macro => (
                      <label key={macro} className="flex items-center">
                        <input
                          type="checkbox"
                          checked={filters.macros?.includes(macro) || false}
                          onChange={(e) => handleMultiSelectChange('macros', macro, e.target.checked)}
                          className="mr-2"
                        />
                        <span className="text-sm text-gray-700">{macro}</span>
                      </label>
                    ))}
                  </div>
                </div>
              )}

              {/* Clear Filters */}
              <button
                onClick={() => setFilters({
                  query: '',
                  types: [],
                  subjects: [],
                  categories: [],
                  keywords: [],
                  macros: [],
                  limit: 20,
                  offset: 0
                })}
                className="w-full px-4 py-2 text-sm text-gray-600 hover:text-gray-800 border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Clear All Filters
              </button>
            </div>
          </div>

          {/* Search Results */}
          <div className="lg:col-span-3">
            <div className="bg-white rounded-lg shadow">
              {/* Results Header */}
              <div className="px-6 py-4 border-b border-gray-200">
                <div className="flex justify-between items-center">
                  <h2 className="text-lg font-semibold">
                    {isSearching ? 'Searching...' : `Results (${searchResults.length})`}
                  </h2>
                  {searchResults.length > 0 && (
                    <div className="text-sm text-gray-500">
                      Showing {searchResults.length} problems
                    </div>
                  )}
                </div>
              </div>

              {/* Results List */}
              <div className="divide-y divide-gray-200">
                {searchResults.length === 0 && !isSearching ? (
                  <div className="px-6 py-12 text-center text-gray-500">
                    <p>No problems found. Try adjusting your search criteria.</p>
                  </div>
                ) : (
                  searchResults.map((result, index) => (
                    <div key={index} className="px-6 py-4 hover:bg-gray-50">
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <h3 className="text-lg font-medium text-gray-900 mb-2">
                            {result.results[0]?.name}
                          </h3>
                          
                          {result.results[0]?.description && (
                            <p className="text-gray-600 mb-3">
                              {result.results[0].description}
                            </p>
                          )}

                          {/* Metadata Tags */}
                          <div className="flex flex-wrap gap-2 mb-3">
                            {result.results[0]?.types.map(type => (
                              <span key={type} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                                {type}
                              </span>
                            ))}
                            {result.results[0]?.subjects.map(subject => (
                              <span key={subject} className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                                {subject}
                              </span>
                            ))}
                            {result.results[0]?.categories.map(category => (
                              <span key={category} className="px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded-full">
                                {category}
                              </span>
                            ))}
                          </div>

                          {/* Keywords */}
                          {result.results[0]?.keywords.length > 0 && (
                            <div className="mb-3">
                              <span className="text-sm text-gray-500">Keywords: </span>
                              <span className="text-sm text-gray-700">
                                {result.results[0].keywords.join(', ')}
                              </span>
                            </div>
                          )}

                          {/* Macros */}
                          {result.results[0]?.macros.length > 0 && (
                            <div className="mb-3">
                              <span className="text-sm text-gray-500">Macros: </span>
                              <span className="text-sm text-gray-700">
                                {result.results[0].macros.join(', ')}
                              </span>
                            </div>
                          )}

                          {/* Score and Matched Fields */}
                          {result.score !== undefined && (
                            <div className="text-xs text-gray-500">
                              Relevance: {Math.round(result.score * 100)}%
                              {result.matched_fields && result.matched_fields.length > 0 && (
                                <span className="ml-2">
                                  Matched: {result.matched_fields.join(', ')}
                                </span>
                              )}
                            </div>
                          )}
                        </div>

                        <div className="ml-4">
                          <button
                            onClick={() => selectProblem(result.results[0]?.id || '')}
                            className="px-4 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                          >
                            Open Problem
                          </button>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>

              {/* Load More Button */}
              {searchResults.length > 0 && searchResults.length >= (filters.limit || 20) && (
                <div className="px-6 py-4 border-t border-gray-200 text-center">
                  <button
                    onClick={loadMore}
                    disabled={isSearching}
                    className="px-6 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 disabled:opacity-50"
                  >
                    {isSearching ? 'Loading...' : 'Load More'}
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SearchPage;
