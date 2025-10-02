// Database problem rendering page
import { useState, useEffect } from 'react';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';
import Markdown from '../components/Markdown';

const DatabaseProblemPage = () => {
  const navigate = useNavigate();
  const params = useParams();
  const [searchParams, setSearchParams] = useSearchParams();
  
  // Extract problem ID from wildcard path (everything after /db/)
  const problemId = params['*'] || '';
  const seed = Number(searchParams.get('seed') ?? '0');
  
  const [problem, setProblem] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [studentAnswers, setStudentAnswers] = useState<Record<string, string>>({});
  const [feedback, setFeedback] = useState<any>(null);

  // Load problem on mount or when seed changes
  useEffect(() => {
    const loadProblem = async () => {
      setLoading(true);
      setError(null);
      setFeedback(null);
      
      try {
        const response = await fetch(`/api/db/${problemId}/render?seed=${seed}`);
        if (!response.ok) {
          if (response.status === 404) {
            throw new Error(`Rendering endpoint not available. Please restart the backend server:\n\ncd apps/backend\npython -m uvicorn app.main:app --reload`);
          }
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setProblem(data);
        
        // Initialize answer inputs
        const initialAnswers: Record<string, string> = {};
        data.inputs.forEach((inputId: string) => {
          initialAnswers[inputId] = '';
        });
        setStudentAnswers(initialAnswers);
      } catch (err: any) {
        console.error('Error loading problem:', err);
        setError(err.message || 'Failed to load problem');
      } finally {
        setLoading(false);
      }
    };
    
    loadProblem();
  }, [problemId, seed]);

  const handleSeedChange = (newSeed: number) => {
    setSearchParams({ seed: String(newSeed) });
  };

  const handleAnswerChange = (inputId: string, value: string) => {
    setStudentAnswers(prev => ({
      ...prev,
      [inputId]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const response = await fetch(`/api/db/${problemId}/check`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          seed,
          inputs: studentAnswers
        })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      setFeedback(result);
    } catch (err: any) {
      console.error('Error checking answers:', err);
      setError(err.message || 'Failed to check answers');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-3xl mx-auto">
          <p className="text-gray-600">Loading problem...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-3xl mx-auto">
          <button
            onClick={() => navigate('/')}
            className="mb-4 text-blue-600 hover:underline"
          >
            ← Back to Browse
          </button>
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <h2 className="text-red-800 font-semibold mb-2">Error</h2>
            <p className="text-red-700">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  if (!problem) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => navigate('/')}
            className="mb-4 text-blue-600 hover:underline text-sm"
          >
            ← Back to Browse
          </button>
          <h1 className="text-3xl font-bold text-gray-900">{problem.name}</h1>
          <p className="text-sm text-gray-500 mt-1">ID: {problem.problem_id}</p>
        </div>

        {/* Seed Control */}
        <div className="mb-6 p-4 bg-white rounded-lg shadow">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Problem Seed (for variation):
          </label>
          <div className="flex gap-2">
            <input
              type="number"
              value={seed}
              onChange={(e) => handleSeedChange(Number(e.target.value))}
              className="px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              min="0"
            />
            <button
              onClick={() => handleSeedChange(Math.floor(Math.random() * 10000))}
              className="px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded-md text-sm"
            >
              Random
            </button>
          </div>
        </div>

        {/* Problem Statement */}
        <div className="mb-6 p-6 bg-white rounded-lg shadow">
          <div className="prose max-w-none">
            <Markdown>
              {problem.statement_html.replace(/___ANSWER_BLANK_\w+___/g, '[answer blank]')}
            </Markdown>
          </div>
        </div>

        {/* Answer Form */}
        {problem.inputs && problem.inputs.length > 0 && (
          <form onSubmit={handleSubmit} className="mb-6">
            <div className="p-6 bg-white rounded-lg shadow space-y-4">
              <h2 className="text-xl font-semibold text-gray-900">Your Answers</h2>
              
              {problem.inputs.map((inputId: string, index: number) => (
                <div key={inputId}>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Answer {index + 1}:
                  </label>
                  <input
                    type="text"
                    value={studentAnswers[inputId] || ''}
                    onChange={(e) => handleAnswerChange(inputId, e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Enter your answer"
                  />
                  {feedback && feedback.results[inputId] && (
                    <p className={`mt-1 text-sm ${feedback.results[inputId].correct ? 'text-green-600' : 'text-red-600'}`}>
                      {feedback.results[inputId].message}
                    </p>
                  )}
                </div>
              ))}
              
              <button
                type="submit"
                className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-md transition-colors"
              >
                Check Answers
              </button>
            </div>
          </form>
        )}

        {/* Feedback */}
        {feedback && (
          <div className={`p-6 rounded-lg shadow ${feedback.all_correct ? 'bg-green-50 border-2 border-green-500' : 'bg-yellow-50 border-2 border-yellow-500'}`}>
            <h2 className={`text-xl font-semibold mb-2 ${feedback.all_correct ? 'text-green-800' : 'text-yellow-800'}`}>
              {feedback.all_correct ? '✓ Correct!' : 'Not quite right'}
            </h2>
            <p className={feedback.all_correct ? 'text-green-700' : 'text-yellow-700'}>
              Score: {Math.round(feedback.score * 100)}%
            </p>
          </div>
        )}

        {/* Warnings/Errors */}
        {problem.warnings && problem.warnings.length > 0 && (
          <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <h3 className="font-semibold text-yellow-800">Warnings:</h3>
            <ul className="list-disc list-inside text-yellow-700">
              {problem.warnings.map((warning: string, i: number) => (
                <li key={i}>{warning}</li>
              ))}
            </ul>
          </div>
        )}

        {problem.errors && problem.errors.length > 0 && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
            <h3 className="font-semibold text-red-800">Rendering Errors:</h3>
            <ul className="list-disc list-inside text-red-700 text-sm">
              {problem.errors.map((err: string, i: number) => (
                <li key={i}>{err}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};

export default DatabaseProblemPage;

