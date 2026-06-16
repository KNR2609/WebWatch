import { useState, useMemo, useEffect } from 'react';
import { Phase1Website, WebsiteStatus } from '../types';
import { Search, Filter, Circle, Loader2 } from 'lucide-react';
import { API_BASE_URL } from '../config';

export function Phase1() {
  const [websites, setWebsites] = useState<Phase1Website[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState<'all' | WebsiteStatus>('all');
  const [filterHttpCode, setFilterHttpCode] = useState<'all' | number>('all');
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  useEffect(() => {
    let active = true;

    async function fetchData() {
      try {
        const res = await fetch(`${API_BASE_URL}/api/monitor`);
        if (!res.ok) {
          throw new Error(`HTTP error! status: ${res.status}`);
        }
        const data = await res.json();
        if (active) {
          if (data && Array.isArray(data.results)) {
            setWebsites(data.results);
            setError(null);
          } else {
            throw new Error('Received invalid data format from backend');
          }
        }
      } catch (err: any) {
        if (active) {
          setError(err.message || 'Failed to fetch monitoring data');
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    fetchData();
    const interval = setInterval(fetchData, 30000); // refresh every 30 seconds

    return () => {
      active = false;
      clearInterval(interval);
    };
  }, [refreshTrigger]);

  const handleRetry = () => {
    setLoading(true);
    setError(null);
    setRefreshTrigger((prev) => prev + 1);
  };

  const filteredWebsites = useMemo(() => {
    let filtered = websites;

    if (searchTerm) {
      filtered = filtered.filter(
        (site) =>
          site.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          site.url.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (filterStatus !== 'all') {
      filtered = filtered.filter((site) => site.status === filterStatus);
    }

    if (filterHttpCode !== 'all') {
      filtered = filtered.filter((site) => site.httpCode === filterHttpCode);
    }

    return filtered;
  }, [websites, searchTerm, filterStatus, filterHttpCode]);

  const stats = useMemo(() => {
    const total = websites.length;
    const good = websites.filter(w => w.status === 'Good').length;
    const slow = websites.filter(w => w.status === 'Slow').length;
    const verySlow = websites.filter(w => w.status === 'Very Slow').length;
    const serverDown = websites.filter(w => w.status === 'Server Down').length;
    const websiteDown = websites.filter(w => w.status === 'Website Down').length;

    return { total, good, slow, verySlow, serverDown, websiteDown };
  }, [websites]);

  function getStatusRowStyle(status: WebsiteStatus): string {
    switch (status) {
      case 'Very Slow': return 'bg-yellow-400 text-gray-900';
      case 'Server Down': return 'bg-fuchsia-600 text-white';
      case 'Website Down': return 'bg-red-600 text-white';
      default: return 'bg-white text-gray-900';
    }
  }

  return (
    <div className="h-full bg-gray-50 px-8 py-6 overflow-y-auto">
      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 rounded-[16px] p-4 text-red-800 flex items-start gap-4 shadow-[0px_4px_12px_rgba(239,68,68,0.1)]">
          <div className="flex-1">
            <h4 className="text-[14px] font-bold text-red-900 mb-1">Backend Connection Error</h4>
            <p className="text-[12px] text-red-700 mb-2">
              Unable to reach the website monitoring backend server. Please verify that the Flask server is running at{' '}
              <code className="bg-red-100 px-1.5 py-0.5 rounded font-mono text-red-800 text-[11px]">{API_BASE_URL}</code>.
            </p>
            <p className="text-[11px] text-red-600 font-mono">Error Details: {error}</p>
          </div>
          <button
            onClick={handleRetry}
            disabled={loading}
            className="px-3 py-1.5 bg-red-600 hover:bg-red-700 text-white font-semibold text-[11px] rounded-[6px] transition-colors cursor-pointer shadow-sm flex items-center gap-1.5 disabled:bg-red-400 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                <span>Retrying...</span>
              </>
            ) : (
              <span>Retry Connection</span>
            )}
          </button>
        </div>
      )}

      <div className="mb-6 bg-white rounded-[16px] border border-gray-200 p-5 drop-shadow-[0px_4px_20px_rgba(149,157,165,0.25)]">
          <h2 className="text-[20px] font-bold text-gray-900 mb-4">Website Monitoring Dashboard</h2>
          <div className="flex flex-wrap gap-3 text-[12px]">
            <div className="flex items-center gap-2">
              <span className="font-medium text-gray-600">Total Sites:</span>
              <span className="px-2.5 py-1 rounded-[20px] font-medium bg-gray-100 text-gray-900">{stats.total}</span>
            </div>
            <div className="flex items-center gap-2">
              <Circle className="w-3 h-3 fill-green-500 text-green-500" />
              <span className="text-gray-600">Good: <span className="font-medium text-gray-900">{stats.good}</span></span>
            </div>
            <div className="flex items-center gap-2">
              <Circle className="w-3 h-3 fill-orange-500 text-orange-500" />
              <span className="text-gray-600">Slow: <span className="font-medium text-gray-900">{stats.slow}</span></span>
            </div>
            <div className="flex items-center gap-2">
              <Circle className="w-3 h-3 fill-yellow-500 text-yellow-500" />
              <span className="text-gray-600">Very Slow: <span className="font-medium text-gray-900">{stats.verySlow}</span></span>
            </div>
            <div className="flex items-center gap-2">
              <Circle className="w-3 h-3 fill-fuchsia-600 text-fuchsia-600" />
              <span className="text-gray-600">Server Down: <span className="font-medium text-gray-900">{stats.serverDown}</span></span>
            </div>
            <div className="flex items-center gap-2">
              <Circle className="w-3 h-3 fill-red-600 text-red-600" />
              <span className="text-gray-600">Website Down: <span className="font-medium text-gray-900">{stats.websiteDown}</span></span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-[16px] border border-gray-200 p-4 mb-6 drop-shadow-[0px_4px_20px_rgba(149,157,165,0.25)]">
          <div className="flex gap-3 items-center">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder={websites.length === 0 ? "No sites to search" : `Search from ${websites.length} sites`}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                disabled={websites.length === 0}
                className="w-full pl-10 pr-4 py-2 text-[12px] border border-gray-300 rounded-[4px] bg-white focus:outline-none focus:ring-1 focus:ring-[#651fff] focus:border-[#651fff] transition-colors shadow-[inset_0px_1px_1px_0px_rgba(31,41,55,0.06)] disabled:bg-gray-100 disabled:text-gray-400 disabled:cursor-not-allowed"
              />
            </div>
            <div className="relative">
              <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value as any)}
                disabled={websites.length === 0}
                className="pl-10 pr-8 py-2 text-[12px] border border-gray-300 rounded-[4px] bg-white focus:outline-none focus:ring-1 focus:ring-[#651fff] focus:border-[#651fff] appearance-none cursor-pointer min-w-[180px] transition-colors shadow-[inset_0px_1px_1px_0px_rgba(31,41,55,0.06)] disabled:bg-gray-100 disabled:text-gray-400 disabled:cursor-not-allowed"
              >
                <option value="all">All Statuses</option>
                <option value="Good">Good</option>
                <option value="Slow">Slow</option>
                <option value="Very Slow">Very Slow</option>
                <option value="Server Down">Server Down</option>
                <option value="Website Down">Website Down</option>
              </select>
            </div>
            <select
              value={filterHttpCode}
              onChange={(e) => setFilterHttpCode(e.target.value === 'all' ? 'all' : Number(e.target.value))}
              disabled={websites.length === 0}
              className="px-4 py-2 text-[12px] border border-gray-300 rounded-[4px] bg-white focus:outline-none focus:ring-1 focus:ring-[#651fff] focus:border-[#651fff] appearance-none cursor-pointer min-w-[150px] transition-colors shadow-[inset_0px_1px_1px_0px_rgba(31,41,55,0.06)] disabled:bg-gray-100 disabled:text-gray-400 disabled:cursor-not-allowed"
            >
              <option value="all">All HTTP Codes</option>
              <option value="200">200 - OK</option>
              <option value="301">301 - Moved</option>
              <option value="302">302 - Found</option>
              <option value="403">403 - Forbidden</option>
              <option value="404">404 - Not Found</option>
              <option value="500">500 - Server Error</option>
              <option value="503">503 - Unavailable</option>
            </select>
          </div>
        </div>

        <div className="bg-white rounded-[16px] border border-gray-200 overflow-hidden drop-shadow-[0px_4px_20px_rgba(149,157,165,0.25)]">
          <div className="overflow-x-auto">
            <table className="w-full text-[14px]">
              <thead className="bg-[#f9fafb] border-b border-[rgba(4,32,69,0.1)]">
                <tr>
                  <th className="px-4 py-3 text-left font-medium text-[#6b7280] text-[12px] uppercase tracking-[0.48px]">Website Name</th>
                  <th className="px-4 py-3 text-left font-medium text-[#6b7280] text-[12px] uppercase tracking-[0.48px]">URL</th>
                  <th className="px-4 py-3 text-left font-medium text-[#6b7280] text-[12px] uppercase tracking-[0.48px]">Status</th>
                  <th className="px-4 py-3 text-left font-medium text-[#6b7280] text-[12px] uppercase tracking-[0.48px]">Response Time (ms)</th>
                  <th className="px-4 py-3 text-left font-medium text-[#6b7280] text-[12px] uppercase tracking-[0.48px]">HTTP Code</th>
                  <th className="px-4 py-3 text-left font-medium text-[#6b7280] text-[12px] uppercase tracking-[0.48px]">HTTP Message</th>
                </tr>
              </thead>
              <tbody>
                {loading && websites.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-4 py-12 text-center text-[#6b7280]">
                      <div className="flex flex-col items-center justify-center gap-2">
                        <Loader2 className="w-6 h-6 animate-spin text-[#651fff]" />
                        <span>Fetching live monitoring data from backend...</span>
                      </div>
                    </td>
                  </tr>
                ) : error && websites.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-4 py-12 text-center text-red-500 font-medium">
                      <div className="flex flex-col items-center justify-center gap-2">
                        <span className="text-[16px] font-semibold">Failed to connect to backend</span>
                        <span className="text-[12px] text-gray-500 max-w-[400px] mx-auto">
                          Make sure the Flask backend app is running at <code className="bg-red-50 px-1.5 py-0.5 rounded text-red-600 font-mono">{API_BASE_URL}</code>.
                        </span>
                        <span className="text-[11px] text-red-400 mt-1">({error})</span>
                      </div>
                    </td>
                  </tr>
                ) : filteredWebsites.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-4 py-8 text-center text-[#6b7280]">
                      No websites found matching the criteria.
                    </td>
                  </tr>
                ) : (
                  filteredWebsites.map((website) => {
                    const rowStyle = getStatusRowStyle(website.status);
                    return (
                      <tr
                        key={website.id}
                        className={`${rowStyle} border-b border-[rgba(4,32,69,0.1)] hover:bg-gray-50 transition-colors`}
                      >
                        <td className="px-4 py-3 font-medium text-gray-900">{website.name}</td>
                        <td className="px-4 py-3 text-gray-600 text-[14px]">{website.url}</td>
                        <td className="px-4 py-3">
                          <span className={`inline-flex items-center gap-1.5 ${website.status === 'Good' ? 'font-medium' : 'font-semibold'}`}>
                            {website.status}
                          </span>
                        </td>
                        <td className="px-4 py-3 font-mono text-[14px]">
                          {website.responseTime !== null && website.responseTime !== undefined ? `${website.responseTime} ms` : 'N/A'}
                        </td>
                        <td className="px-4 py-3 font-mono text-[14px] font-medium">
                          {website.httpCode !== null && website.httpCode !== undefined ? website.httpCode : 'N/A'}
                        </td>
                        <td className="px-4 py-3 text-[14px]">{website.httpMessage || 'N/A'}</td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>

      <div className="mt-4 bg-purple-50 border border-purple-200 rounded-[16px] p-3">
        <p className="text-[12px] text-gray-700">
          <span className="font-medium">Note:</span> The application checks website status every 10 minutes. To view the latest output, you must refresh the page.
        </p>
      </div>
    </div>
  );
}
