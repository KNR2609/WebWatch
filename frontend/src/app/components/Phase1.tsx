import { useState, useMemo } from 'react';
import { Phase1Website, WebsiteStatus } from '../types';
import { generatePhase1Data } from '../data/phase1Data';
import { Search, Filter, Circle } from 'lucide-react';

export function Phase1() {
  const [websites] = useState<Phase1Website[]>(generatePhase1Data());
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState<'all' | WebsiteStatus>('all');
  const [filterHttpCode, setFilterHttpCode] = useState<'all' | number>('all');

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
                placeholder="Search from 63 sites"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 text-[12px] border border-gray-300 rounded-[4px] bg-white focus:outline-none focus:ring-1 focus:ring-[#651fff] focus:border-[#651fff] transition-colors shadow-[inset_0px_1px_1px_0px_rgba(31,41,55,0.06)]"
              />
            </div>
            <div className="relative">
              <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value as any)}
                className="pl-10 pr-8 py-2 text-[12px] border border-gray-300 rounded-[4px] bg-white focus:outline-none focus:ring-1 focus:ring-[#651fff] focus:border-[#651fff] appearance-none cursor-pointer min-w-[180px] transition-colors shadow-[inset_0px_1px_1px_0px_rgba(31,41,55,0.06)]"
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
              className="px-4 py-2 text-[12px] border border-gray-300 rounded-[4px] bg-white focus:outline-none focus:ring-1 focus:ring-[#651fff] focus:border-[#651fff] appearance-none cursor-pointer min-w-[150px] transition-colors shadow-[inset_0px_1px_1px_0px_rgba(31,41,55,0.06)]"
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
                {filteredWebsites.map((website) => {
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
                      <td className="px-4 py-3 font-mono text-[14px]">{website.responseTime}</td>
                      <td className="px-4 py-3 font-mono text-[14px] font-medium">{website.httpCode}</td>
                      <td className="px-4 py-3 text-[14px]">{website.httpMessage}</td>
                    </tr>
                  );
                })}
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
