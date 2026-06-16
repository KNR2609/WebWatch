import { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { Phase1 } from './components/Phase1';
import { Phase2 } from './components/Phase2';
import { generatePhase2Data } from './data/phase2Data';
import { Phase2Website } from './types';
import { API_BASE_URL } from './config';

export interface PendingChange {
  file: string;
  changes_count: number;
}

export default function App() {
  const [currentPhase, setCurrentPhase] = useState<'phase1' | 'phase2'>('phase1');
  const [pendingChanges, setPendingChanges] = useState<PendingChange[]>([]);

  const fetchPendingChanges = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/pending-changes`);
      if (res.ok) {
        const data = await res.json();
        setPendingChanges(data);
      }
    } catch (err) {
      console.error('Failed to fetch pending changes:', err);
    }
  };

  useEffect(() => {
    fetchPendingChanges();
    const interval = setInterval(fetchPendingChanges, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col h-screen">
      <Header
        currentPhase={currentPhase}
        onNavigateToPhase1={() => setCurrentPhase('phase1')}
        onNavigateToPhase2={() => setCurrentPhase('phase2')}
        pendingChanges={pendingChanges}
        onRefreshPending={fetchPendingChanges}
      />

      <div className="flex-1 overflow-hidden">
        {currentPhase === 'phase1' ? (
          <Phase1 />
        ) : (
          <Phase2 />
        )}
      </div>
    </div>
  );
}
