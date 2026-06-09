import { useState } from 'react';
import { Header } from './components/Header';
import { Phase1 } from './components/Phase1';
import { Phase2 } from './components/Phase2';
import { generatePhase2Data } from './data/phase2Data';
import { Phase2Website } from './types';

export default function App() {
  const [currentPhase, setCurrentPhase] = useState<'phase1' | 'phase2'>('phase1');
  const [isRunningTest, setIsRunningTest] = useState(false);
  const [progress, setProgress] = useState(0);
  const [phase2Websites, setPhase2Websites] = useState<Phase2Website[]>(generatePhase2Data());

  const handleRunTest = () => {
    setIsRunningTest(true);
    setProgress(0);

    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          return 100;
        }
        return prev + 100 / 30;
      });
    }, 1000);

    setTimeout(() => {
      clearInterval(interval);
      setProgress(100);
      const newData = generatePhase2Data();
      setPhase2Websites(newData);
      setTimeout(() => {
        setIsRunningTest(false);
        setProgress(0);
      }, 500);
    }, 30000);
  };

  const handleApproveAll = (websiteId: string) => {
    setPhase2Websites((prev) =>
      prev.map((w) =>
        w.id === websiteId
          ? { ...w, issues: w.issues.map((i) => i.status === 'pending' ? { ...i, status: 'approved' as const } : i) }
          : w
      )
    );
  };

  const handleRejectAll = (websiteId: string) => {
    setPhase2Websites((prev) =>
      prev.map((w) =>
        w.id === websiteId
          ? { ...w, issues: w.issues.map((i) => i.status === 'pending' ? { ...i, status: 'rejected' as const } : i) }
          : w
      )
    );
  };

  return (
    <div className="flex flex-col h-screen">
      <Header
        currentPhase={currentPhase}
        onNavigateToPhase1={() => setCurrentPhase('phase1')}
        onNavigateToPhase2={() => setCurrentPhase('phase2')}
        phase2Websites={phase2Websites}
        onApproveAll={handleApproveAll}
        onRejectAll={handleRejectAll}
      />

      <div className="flex-1 overflow-hidden">
        {currentPhase === 'phase1' ? (
          <Phase1 />
        ) : (
          <Phase2
            isRunningTest={isRunningTest}
            progress={progress}
            onRunTest={handleRunTest}
            websites={phase2Websites}
          />
        )}
      </div>
    </div>
  );
}
