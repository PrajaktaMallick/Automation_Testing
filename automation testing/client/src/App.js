import React from 'react';
import { Routes, Route } from 'react-router-dom';
import styled from 'styled-components';
import Header from './components/Header';
import Dashboard from './pages/Dashboard';
import CreateTest from './pages/CreateTest';
import TestResults from './pages/TestResults';
import TestHistory from './pages/TestHistory';

const AppContainer = styled.div`
  min-height: 100vh;
  background-color: #f5f5f5;
`;

const MainContent = styled.main`
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
`;

function App() {
  return (
    <AppContainer>
      <Header />
      <MainContent>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/create" element={<CreateTest />} />
          <Route path="/test/:sessionId" element={<TestResults />} />
          <Route path="/history" element={<TestHistory />} />
        </Routes>
      </MainContent>
    </AppContainer>
  );
}

export default App;
