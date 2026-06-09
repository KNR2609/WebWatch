import { useEffect, useRef } from 'react';
import { X, ExternalLink, Check, XCircle } from 'lucide-react';
import { PendingChange } from '../App';

interface PendingChangesPopupProps {
  pendingChanges: PendingChange[];
  onClose: () => void;
  onRefresh: () => void;
}

function parseFilename(filename: string) {
  // website_name_api_name.json
  const clean = filename.replace('.json', '');
  const parts = clean.split('_');
  if (parts.length > 1) {
    const website = parts.slice(0, -1).join(' ');
    const api = parts[parts.length - 1];
    return { website, api };
  }
  return { website: clean, api: 'General' };
}

export function PendingChangesPopup({
  pendingChanges,
  onClose,
  onRefresh,
}: PendingChangesPopupProps) {
  const popupRef = useRef<HTMLDivElement>(null);

  const totalPending = pendingChanges.reduce((sum, item) => sum + item.changes_count, 0);

  const handleAction = async (filename: string, action: 'approve' | 'reject') => {
    try {
      const res = await fetch(`http://localhost:5000/api/${action}/${filename}`);
      if (res.ok) {
        onRefresh();
      } else {
        console.error(`Failed to ${action} changes:`, res.statusText);
      }
    } catch (err) {
      console.error(`Error performing ${action} action:`, err);
    }
  };

  useEffect(() => {
    function handleKey(e: KeyboardEvent) {
      if (e.key === 'Escape') onClose();
    }
    document.addEventListener('keydown', handleKey);
    return () => document.removeEventListener('keydown', handleKey);
  }, [onClose]);

  return (
    // Full-screen backdrop with blur
    <div
      className="fixed inset-0 z-50 flex items-start justify-end"
      style={{ backgroundColor: 'rgba(15, 10, 40, 0.35)', backdropFilter: 'blur(4px)' }}
      onMouseDown={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      {/* Panel anchored top-right */}
      <div
        ref={popupRef}
        className="mt-[68px] mr-8 bg-white rounded-[16px] shadow-[0px_16px_60px_rgba(0,0,0,0.22)] border border-gray-100 flex flex-col"
        style={{ width: 640, maxHeight: 'calc(100vh - 100px)' }}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-5 border-b border-gray-100 flex-shrink-0">
          <div className="flex items-center gap-3">
            <h2 className="text-[20px] font-bold text-gray-900">Pending Changes</h2>
            {totalPending > 0 && (
              <span className="px-2.5 py-0.5 rounded-[20px] bg-[#651fff]/10 text-[#651fff] text-[12px] font-semibold">
                {totalPending} issues
              </span>
            )}
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 flex items-center justify-center rounded-full hover:bg-gray-100 transition-colors text-gray-400 hover:text-gray-600"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Body */}
        {!Array.isArray(pendingChanges) || pendingChanges.length === 0 ? (
          <div className="px-6 py-16 text-center text-gray-400 text-[14px]">
            No pending changes
          </div>
        ) : (
          <div className="overflow-y-auto flex-1">
            <table className="w-full">
              <thead className="sticky top-0 bg-white z-10">
                <tr className="border-b border-gray-100">
                  <th className="text-left px-6 py-3.5 text-[11px] font-semibold text-gray-400 uppercase tracking-wider">
                    Website
                  </th>
                  <th className="text-left px-4 py-3.5 text-[11px] font-semibold text-gray-400 uppercase tracking-wider">
                    File
                  </th>
                  <th className="text-center px-4 py-3.5 text-[11px] font-semibold text-gray-400 uppercase tracking-wider">
                    Records
                  </th>
                  <th className="text-center px-6 py-3.5 text-[11px] font-semibold text-gray-400 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {Array.isArray(pendingChanges) && pendingChanges.map((item) => {
                  const { website } = parseFilename(item.file);
                  return (
                    <tr
                      key={item.file}
                      className="hover:bg-gray-50/70 transition-colors"
                    >
                      <td className="px-6 py-4">
                        <span className="text-[13px] font-medium text-gray-800 capitalize">
                          {website}
                        </span>
                      </td>
                      <td className="px-4 py-4">
                        <a
                          href={`http://localhost:5000/pending/${item.file}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center gap-1.5 text-[13px] text-[#651fff] hover:underline font-medium"
                        >
                          <span className="truncate max-w-[180px]">{item.file}</span>
                          <ExternalLink className="w-3 h-3 flex-shrink-0" />
                        </a>
                      </td>
                      <td className="px-4 py-4 text-center">
                        <span className="inline-flex items-center justify-center w-7 h-7 rounded-full bg-amber-50 text-amber-600 text-[12px] font-bold">
                          {item.changes_count}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center justify-center gap-3">
                          <button
                            onClick={() => handleAction(item.file, 'approve')}
                            className="flex items-center gap-1 text-[12px] font-semibold text-emerald-600 hover:text-emerald-700 transition-colors"
                          >
                            <Check className="w-3.5 h-3.5" />
                            Approve
                          </button>
                          <span className="text-gray-200 select-none">|</span>
                          <button
                            onClick={() => handleAction(item.file, 'reject')}
                            className="flex items-center gap-1 text-[12px] font-semibold text-red-500 hover:text-red-600 transition-colors"
                          >
                            <XCircle className="w-3.5 h-3.5" />
                            Reject
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
