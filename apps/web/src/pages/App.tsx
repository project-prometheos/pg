import { Route, Routes } from 'react-router-dom';

import ProblemPage from './ProblemPage';
import SolutionPage from './SolutionPage';

const App = () => {
  return (
    <Routes>
      <Route path="/" element={<ProblemPage />} />
      <Route path="/p/:id" element={<ProblemPage />} />
      <Route path="/solution/:variantId" element={<SolutionPage />} />
    </Routes>
  );
};

export default App;
