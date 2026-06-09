import { useState } from 'react';
import { Globe, ArrowRight, ArrowLeft, Bell } from 'lucide-react';
import { Phase2Website } from '../types';
import { PendingChange } from '../App';
import { PendingChangesPopup } from './PendingChangesPopup';

interface HeaderProps {
  currentPhase: 'phase1' | 'phase2';
  onNavigateToPhase1: () => void;
  onNavigateToPhase2: () => void;
  phase2Websites: Phase2Website[];
  onApproveAll: (websiteId: string) => void;
  onRejectAll: (websiteId: string) => void;
  pendingChanges: PendingChange[];
  onRefreshPending: () => void;
}

export function Header({
  currentPhase,
  onNavigateToPhase1,
  onNavigateToPhase2,
  phase2Websites,
  onApproveAll,
  onRejectAll,
  pendingChanges,
  onRefreshPending,
}: HeaderProps) {
  const [showPending, setShowPending] = useState(false);

  const totalPending = pendingChanges.reduce(
    (sum, item) => sum + item.changes_count,
    0
  );

  return (
    <>
      <div className="border-b border-gray-200 bg-white px-8 py-4 drop-shadow-[0px_4px_20px_rgba(149,157,165,0.25)] relative z-40">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 bg-[#651fff] rounded-[6px] flex items-center justify-center">
              <Globe className="w-5 h-5 text-white" />
            </div>
            <h1 className="text-[20px] font-bold text-gray-900">WebOrbit</h1>
          </div>

          {/* Right controls */}
          <div className="flex items-center gap-3">
            {/* Pending Changes button */}
            <button
              onClick={() => setShowPending(true)}
              className="relative flex items-center gap-2 px-4 py-2 text-[12px] font-medium rounded-[6px] border border-gray-200 bg-white text-gray-700 hover:bg-gray-50 transition-colors"
            >
              <Bell className="w-4 h-4" />
              Pending Changes
              {totalPending >= 0 && (
                <span className="absolute -top-1.5 -right-1.5 min-w-[18px] h-[18px] px-1 flex items-center justify-center rounded-full bg-[#651fff] text-white text-[10px] font-bold leading-none">
                  {totalPending}
                </span>
              )}
            </button>

            {/* Phase navigation */}
            {currentPhase === 'phase1' ? (
              <button
                onClick={onNavigateToPhase2}
                className="px-4 py-2 text-[12px] font-medium flex items-center gap-2 transition-colors bg-[#651fff] text-white rounded-[6px] hover:bg-[#5817d9]"
              >
                View DP Testing Errors
                <ArrowRight className="w-4 h-4" />
              </button>
            ) : (
              <button
                onClick={onNavigateToPhase1}
                className="px-4 py-2 text-[12px] font-medium flex items-center gap-2 transition-colors bg-gray-600 text-white rounded-[6px] hover:bg-gray-700"
              >
                <ArrowLeft className="w-4 h-4" />
                Back to Status Monitoring
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Portal-style full-screen overlay */}
      {showPending && (
        <PendingChangesPopup
          pendingChanges={pendingChanges}
          onClose={() => setShowPending(false)}
          onRefresh={onRefreshPending}
        />
      )}
    </>
  );
}
