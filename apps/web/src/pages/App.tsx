import { Route, Routes } from 'react-router-dom';

import ProblemPage from './ProblemPage';
import SolutionPage from './SolutionPage';
import SearchPage from './SearchPage';
import BrowsePage from './BrowsePage';
import DatabaseProblemPage from './DatabaseProblemPage';

const App = () => {
  return (
    <Routes>
      <Route path="/" element={<BrowsePage />} />
      <Route path="/p/:id" element={<ProblemPage />} />
      <Route path="/db/*" element={<DatabaseProblemPage />} />
      <Route path="/solution/:variantId" element={<SolutionPage />} />
      <Route path="/search" element={<SearchPage />} />
    </Routes>
  );
};

export default App;
