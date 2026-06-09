import { useState, useMemo, useEffect } from 'react';
import { Phase2Website, Issue, IssueStatus } from '../types';
import { generatePhase2Data } from '../data/phase2Data';
import { Play, Search, ArrowUpDown, CheckCircle, XCircle, FileText } from 'lucide-react';
import { TextDiff } from './TextDiff';

interface Phase2Props {
  isRunningTest: boolean;
  progress: number;
  onRunTest: () => void;
  websites: Phase2Website[];
}

export function Phase2({ isRunningTest, progress, onRunTest, websites }: Phase2Props) {
  const [selectedWebsite, setSelectedWebsite] = useState<Phase2Website | null>(websites[0]);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState<'name' | 'issues-high' | 'issues-low'>('name');
  const [selectedImage, setSelectedImage] = useState<{ src: string; title: string } | null>(null);
  const [confirmAction, setConfirmAction] = useState<{
    issueId: string;
    action: 'approve' | 'reject';
    websiteId: string;
  } | null>(null);
  const [localWebsites, setLocalWebsites] = useState<Phase2Website[]>(websites);

  useEffect(() => {
    setLocalWebsites(websites);
  }, [websites]);

  const handleActionClick = (issueId: string, action: 'approve' | 'reject', websiteId: string) => {
    setConfirmAction({ issueId, action, websiteId });
  };

  const handleConfirmAction = () => {
    if (!confirmAction) return;

    const { issueId, action, websiteId } = confirmAction;
    const newStatus: IssueStatus = action === 'approve' ? 'approved' : 'rejected';

    setLocalWebsites((prev) =>
      prev.map((website) => {
        if (website.id === websiteId) {
          return {
            ...website,
            issues: website.issues.map((issue) =>
              issue.id === issueId ? { ...issue, status: newStatus } : issue
            ),
          };
        }
        return website;
      })
    );

    if (selectedWebsite?.id === websiteId) {
      setSelectedWebsite((prev) =>
        prev
          ? {
              ...prev,
              issues: prev.issues.map((issue) =>
                issue.id === issueId ? { ...issue, status: newStatus } : issue
              ),
            }
          : null
      );
    }

    setConfirmAction(null);
  };

  const handleCancelAction = () => {
    setConfirmAction(null);
  };

  const filteredAndSortedWebsites = useMemo(() => {
    let filtered = localWebsites;

    if (searchTerm) {
      filtered = filtered.filter(
        (website) =>
          website.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          website.url.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    const sorted = [...filtered].sort((a, b) => {
      if (sortBy === 'name') {
        return a.name.localeCompare(b.name);
      } else if (sortBy === 'issues-high') {
        return b.totalIssues - a.totalIssues;
      } else {
        return a.totalIssues - b.totalIssues;
      }
    });

    return sorted;
  }, [localWebsites, searchTerm, sortBy]);

  return (
    <div className="flex h-full bg-gray-50">
      {/* Sidebar */}
      <div className="w-80 h-full bg-white border-r border-gray-200 flex flex-col ml-8">
        <div className="p-4 border-b border-gray-200">
          <h3 className="text-[16px] font-bold mb-4 text-gray-900">DP Testing Errors</h3>

          <button
            onClick={onRunTest}
            disabled={isRunningTest}
            className={`w-full mb-4 px-4 py-2 text-[12px] flex items-center justify-center gap-2 transition-colors ${
              isRunningTest
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed rounded-[6px]'
                : 'bg-[#651fff] text-white rounded-[6px] hover:bg-[#5817d9]'
            }`}
          >
            {!isRunningTest && <Play className="w-4 h-4" />}
            {isRunningTest ? 'Running Test...' : 'Run Test'}
          </button>

          {isRunningTest && (
            <div className="mb-4">
              <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className="h-full bg-[#651fff] transition-all duration-1000"
                  style={{ width: `${progress}%` }}
                ></div>
              </div>
              <p className="text-[12px] text-gray-600 mt-2 text-center font-medium">{Math.round(progress)}%</p>
            </div>
          )}

          <div className="relative mb-3">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search from 63 sites"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-3 py-2 bg-white rounded-[4px] border border-gray-300 focus:outline-none focus:ring-1 focus:ring-[#651fff] focus:border-[#651fff] text-[12px] transition-colors shadow-[inset_0px_1px_1px_0px_rgba(31,41,55,0.06)]"
            />
          </div>

          <div className="relative">
            <ArrowUpDown className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as 'name' | 'issues-high' | 'issues-low')}
              className="w-full pl-9 pr-3 py-2 bg-white rounded-[4px] border border-gray-300 text-[12px] focus:outline-none focus:ring-1 focus:ring-[#651fff] focus:border-[#651fff] appearance-none cursor-pointer transition-colors shadow-[inset_0px_1px_1px_0px_rgba(31,41,55,0.06)]"
            >
              <option value="name">Sort by Name (A-Z)</option>
              <option value="issues-high">Sort by Issues (High to Low)</option>
              <option value="issues-low">Sort by Issues (Low to High)</option>
            </select>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto">
          {filteredAndSortedWebsites.map((website) => (
            <button
              key={website.id}
              onClick={() => setSelectedWebsite(website)}
              className={`w-full px-4 py-3 text-left transition-colors border-b border-gray-100 ${
                selectedWebsite?.id === website.id
                  ? 'bg-[#e9e1ff] border-l-4 border-l-[#651fff]'
                  : 'hover:bg-gray-50'
              }`}
            >
              <div className="flex items-center justify-between gap-3 mb-1">
                <div className="flex-1 min-w-0 text-[14px] font-medium truncate text-gray-900">
                  {website.name}
                </div>
                {website.totalIssues > 0 && (
                  <span className="flex items-center justify-center min-w-[24px] h-5 px-2 bg-red-100 text-red-700 rounded-[4px] font-medium text-[12px]">
                    {website.totalIssues}
                  </span>
                )}
              </div>
              <div className="text-[12px] text-gray-500 truncate">{website.url}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 h-full overflow-y-auto mr-8">
        {selectedWebsite ? (
          <>
            <div className="border-b border-gray-200 bg-white p-5 mt-0 drop-shadow-[0px_4px_20px_rgba(149,157,165,0.25)]">
              <h1 className="text-[20px] font-bold text-gray-900 mb-2">{selectedWebsite.name}</h1>
              <div className="text-[12px] text-gray-500 mb-3">{selectedWebsite.url}</div>
              <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-red-50 border border-red-200 rounded-[4px] text-[12px] font-medium text-red-700">
                <span className="w-2 h-2 rounded-full bg-red-500"></span>
                Total Issues: {selectedWebsite.totalIssues}
              </div>
            </div>

            <div className="p-5">
              <h2 className="text-[16px] font-bold mb-5 text-gray-900">Issue Details</h2>
              <div className="space-y-4">
                {selectedWebsite.issues.map((issue) => (
                  <div
                    key={issue.id}
                    className={`relative border border-gray-200 bg-white rounded-[16px] p-5 drop-shadow-[0px_4px_20px_rgba(149,157,165,0.25)] ${
                      issue.status === 'approved'
                        ? 'border-green-300 bg-green-50/50'
                        : issue.status === 'rejected'
                        ? 'border-red-300 bg-red-50/50'
                        : ''
                    }`}
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center gap-2.5">
                        {issue.type === 'text' && <FileText className="w-5 h-5 text-[#651fff]" />}
                        <h3 className="text-[14px] font-bold text-gray-900">
                          {issue.page} {issue.type === 'text' ? '- Text Difference' : '- Visual Difference'}
                        </h3>
                        {issue.status !== 'pending' && (
                          <span
                            className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-[4px] text-[12px] font-medium ${
                              issue.status === 'approved'
                                ? 'bg-green-100 text-green-700'
                                : 'bg-red-100 text-red-700'
                            }`}
                          >
                            {issue.status === 'approved' ? (
                              <>
                                <CheckCircle className="w-3 h-3" />
                                Approved
                              </>
                            ) : (
                              <>
                                <XCircle className="w-3 h-3" />
                                Rejected
                              </>
                            )}
                          </span>
                        )}
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleActionClick(issue.id, 'approve', selectedWebsite.id)}
                          className={`flex items-center gap-1.5 px-3 py-1.5 text-[12px] font-medium transition-colors rounded-[6px] ${
                            issue.status === 'approved'
                              ? 'bg-green-600 text-white'
                              : 'bg-green-600/90 text-white hover:bg-green-600'
                          }`}
                        >
                          <CheckCircle className="w-4 h-4" />
                          Approve
                        </button>
                        <button
                          onClick={() => handleActionClick(issue.id, 'reject', selectedWebsite.id)}
                          className={`flex items-center gap-1.5 px-3 py-1.5 text-[12px] font-medium transition-colors rounded-[6px] ${
                            issue.status === 'rejected'
                              ? 'bg-red-600 text-white'
                              : 'bg-red-600/90 text-white hover:bg-red-600'
                          }`}
                        >
                          <XCircle className="w-4 h-4" />
                          Reject
                        </button>
                      </div>
                    </div>

                    {issue.type === 'screenshot' ? (
                      <div className="grid grid-cols-3 gap-4">
                        <div>
                          <div className="mb-2">
                            <span className="inline-block px-2.5 py-1 text-[12px] font-medium bg-[#e9e1ff] text-[#651fff] rounded-[4px]">
                              Baseline (Yesterday)
                            </span>
                          </div>
                          <div className="border border-gray-200 rounded-[6px] overflow-hidden bg-white cursor-pointer hover:border-[#651fff] transition-colors" onClick={() => setSelectedImage({ src: issue.baselineScreenshot!, title: `${issue.page} - Baseline` })}>
                            <img src={issue.baselineScreenshot} alt="Baseline" className="w-full h-auto" />
                          </div>
                        </div>

                        <div>
                          <div className="mb-2">
                            <span className="inline-block px-2.5 py-1 text-[12px] font-medium bg-green-50 text-green-700 rounded-[4px]">
                              Current (Today)
                            </span>
                          </div>
                          <div className="border border-gray-200 rounded-[6px] overflow-hidden bg-white cursor-pointer hover:border-green-400 transition-colors" onClick={() => setSelectedImage({ src: issue.currentScreenshot!, title: `${issue.page} - Current` })}>
                            <img src={issue.currentScreenshot} alt="Current" className="w-full h-auto" />
                          </div>
                        </div>

                        <div>
                          <div className="mb-2">
                            <span className="inline-block px-2.5 py-1 text-[12px] font-medium bg-red-50 text-red-700 rounded-[4px]">
                              Difference (Changes)
                            </span>
                          </div>
                          <div className="relative border border-gray-200 rounded-[6px] overflow-hidden bg-white cursor-pointer hover:border-red-400 transition-colors" onClick={() => setSelectedImage({ src: issue.differenceScreenshot!, title: `${issue.page} - Difference` })}>
                            <img src={issue.differenceScreenshot} alt="Difference" className="w-full h-auto" />
                            {/* Highlighted differences with labels */}
                            <div className="absolute top-2 left-2 pointer-events-none">
                              <div className="border-2 border-red-500 bg-red-500/10 w-24 h-16"></div>
                              <div className="mt-1 bg-red-600 text-white text-xs px-2 py-0.5 rounded font-medium">
                                Header Layout
                              </div>
                            </div>
                            <div className="absolute bottom-3 right-3 pointer-events-none">
                              <div className="border-2 border-red-500 bg-red-500/10 w-28 h-14"></div>
                              <div className="mt-1 bg-red-600 text-white text-xs px-2 py-0.5 rounded font-medium">
                                Button Style
                              </div>
                            </div>
                            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 pointer-events-none">
                              <div className="border-2 border-red-500 bg-red-500/10 w-32 h-12"></div>
                              <div className="mt-1 bg-red-600 text-white text-xs px-2 py-0.5 rounded font-medium whitespace-nowrap">
                                Content Alignment
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    ) : (
                      <TextDiff
                        oldText={issue.baselineText || ''}
                        newText={issue.currentText || ''}
                        label="Text Content"
                      />
                    )}
                  </div>
                ))}
              </div>
            </div>
          </>
        ) : (
          <div className="flex items-center justify-center h-full text-gray-400">
            Select a website to view details
          </div>
        )}
      </div>

      {/* Confirmation Modal */}
      {confirmAction && (
        <div
          className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-6"
          onClick={handleCancelAction}
        >
          <div
            className="max-w-md w-full bg-white rounded-[16px] border border-gray-200 p-6 drop-shadow-[0px_4px_20px_rgba(149,157,165,0.25)]"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center gap-3 mb-4">
              {confirmAction.action === 'approve' ? (
                <div className="w-10 h-10 bg-green-100 rounded-[6px] flex items-center justify-center">
                  <CheckCircle className="w-5 h-5 text-green-600" />
                </div>
              ) : (
                <div className="w-10 h-10 bg-red-100 rounded-[6px] flex items-center justify-center">
                  <XCircle className="w-5 h-5 text-red-600" />
                </div>
              )}
              <h3 className="text-[16px] font-bold text-gray-900">
                {confirmAction.action === 'approve' ? 'Approve Issue?' : 'Reject Issue?'}
              </h3>
            </div>

            <p className="text-[14px] text-gray-600 mb-4">
              {confirmAction.action === 'approve'
                ? 'Are you sure you want to approve this issue? This will mark the issue as resolved and acceptable.'
                : 'Are you sure you want to reject this issue? This will mark the issue as not valid or not requiring action.'}
            </p>
            <p className="text-[12px] text-gray-500 mb-5">
              You can change this decision at any time by clicking the other button.
            </p>

            <div className="flex gap-2">
              <button
                onClick={handleCancelAction}
                className="flex-1 px-4 py-2 text-[12px] font-medium transition-colors bg-gray-100 text-gray-700 rounded-[6px] hover:bg-gray-200"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirmAction}
                className={`flex-1 px-4 py-2 text-[12px] font-medium transition-colors ${
                  confirmAction.action === 'approve'
                    ? 'bg-green-600 text-white rounded-[6px] hover:bg-green-700'
                    : 'bg-red-600 text-white rounded-[6px] hover:bg-red-700'
                }`}
              >
                {confirmAction.action === 'approve' ? 'Approve' : 'Reject'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Image Modal */}
      {selectedImage && (
        <div
          className="fixed inset-0 bg-black/70 z-50 flex items-center justify-center p-6"
          onClick={() => setSelectedImage(null)}
        >
          <div className="max-w-5xl w-full" onClick={(e) => e.stopPropagation()}>
            <div className="mb-3 flex justify-between items-center">
              <h2 className="text-white text-[16px] font-bold">{selectedImage.title}</h2>
              <button
                onClick={() => setSelectedImage(null)}
                className="text-white hover:text-gray-300 text-2xl font-light leading-none"
              >
                ×
              </button>
            </div>
            <div className="bg-white rounded-[16px] overflow-hidden border border-gray-200 drop-shadow-[0px_4px_20px_rgba(149,157,165,0.25)]">
              <img src={selectedImage.src} alt={selectedImage.title} className="w-full h-auto" />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
