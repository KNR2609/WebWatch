import { Phase1Website, WebsiteStatus } from '../types';

const websiteNames = [
  'TechVersions',
  'ProTech Insights',
  'TechMaster Node',
  'The Tech Affair',
  'TechPulse Daily',
  'The Best of Blockchain',
  'The Techno Bytes',
  'The Technology Square',
  'AllTech Insights',
  'BizVersions',
  'Digi Influence',
  'The BusinessCover',
  'The HR Empire',
  'TechWeb Trends',
  'The Salesmark',
  'The Business Innovations',
  'CloudTech Alert',
  'Economic Matter',
  'CXO Matters',
  'Regulatory Compliance News',
  'LearningTech Edu',
  'Healthcare Insights Today',
  'Global Supplychain News',
  'Business Mediums',
  'Delta Punch',
  'Finance Pulse Daily',
  'The Growth Insights',
  'Lead Marketwise',
  'HR Interests',
  'Tech Alert Live',
  'The Road to Profit',
  'TechMaster Pros',
  'Business Updates 360',
  'Growth Rate Finder',
  'Healthcare Business Solution',
  'HR Trends Daily',
  'HRM Ecosystem',
  'HR Pulse Daily',
  'Livingsights',
  'The Techno Digest',
  'The HR Medium',
  'Best of Business Today',
  'Business Narratives',
  'Business Proinsights',
  'Business Target',
  'Business Leader Insights',
  'Business Stories Today',
  'Finance Every Hour',
  'InfoBytes Daily',
  'Infowatch Daily',
  'Market Insights Today',
  'Sales Newton',
  'SalesMarket Scoop',
  'The Sales Insights',
  'Technobeat Daily',
  'The Economy Digest',
  'The Finances Report',
  'The Universal Insights',
  'World Business Hour',
  'Insights Living',
  'Techinsights Today',
  'Protech Empire'
];

export function generatePhase1Data(): Phase1Website[] {
  const statuses: WebsiteStatus[] = ['Good', 'Slow', 'Very Slow', 'Server Down', 'Website Down'];
  const httpCodes = [200, 200, 200, 200, 301, 302, 403, 404, 500, 503];

  return websiteNames.map((name, index) => {
    const status = statuses[Math.floor(Math.random() * statuses.length)];
    const httpCode = httpCodes[Math.floor(Math.random() * httpCodes.length)];

    let responseTime = 2000;
    if (status === 'Good') responseTime = Math.floor(Math.random() * 1500) + 500;
    else if (status === 'Slow') responseTime = Math.floor(Math.random() * 1000) + 2000;
    else if (status === 'Very Slow') responseTime = Math.floor(Math.random() * 2000) + 3400;
    else responseTime = Math.floor(Math.random() * 5000) + 5000;

    return {
      id: `site-${index}`,
      name,
      url: `https://${name.toLowerCase().replace(/\s+/g, '')}.com`,
      status,
      responseTime,
      httpCode,
      httpMessage: httpCode === 200 ? 'OK' : httpCode === 301 ? 'Moved' : httpCode === 404 ? 'Not Found' : 'Error',
    };
  });
}
