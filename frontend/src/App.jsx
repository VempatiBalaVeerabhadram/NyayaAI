import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import Home from './pages/Home';
import SearchPage from './pages/SearchPage';
import CasesPage from './pages/CasesPage';
import ActsPage from './pages/ActsPage';
import GraphPage from './pages/GraphPage';
import EvaluationPage from './pages/EvaluationPage';
import AdminPage from './pages/AdminPage';

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100 selection:bg-blue-600 selection:text-white">
        <Navbar />
        <main className="flex-grow">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/search" element={<SearchPage />} />
            <Route path="/cases" element={<CasesPage />} />
            <Route path="/acts" element={<ActsPage />} />
            <Route path="/knowledge-graph" element={<GraphPage />} />
            <Route path="/evaluation" element={<EvaluationPage />} />
            <Route path="/admin" element={<AdminPage />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </BrowserRouter>
  );
}
