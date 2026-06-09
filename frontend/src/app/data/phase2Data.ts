import { Phase2Website, Issue, IssueType } from '../types';

const sampleScreenshots = [
  'https://images.unsplash.com/photo-1531403009284-440f080d1e12?w=800&h=600&fit=crop',
  'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&h=600&fit=crop',
  'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&h=600&fit=crop',
  'https://images.unsplash.com/photo-1504868584819-f8e8b4b6d7e3?w=800&h=600&fit=crop',
];

const pages = ['Home', 'Resources', 'Contact Us', 'Thank You Page', 'Resource Landing Page'];

const sampleTextChanges = [
  {
    baseline: 'First, API-led connectivity structures integrations into reusable layers. System APIs expose core services, process APIs orchestrate logic, and experience APIs deliver tailored outputs. This reduces redundancy and improves maintainability.',
    current: 'First, api led connectivity structures integrations into reusable layers. System APIs expose core services, process APIs orchestrate logic, and exper ience APIs deliver tailored outputs. This reduces redundancy and improves maintain.'
  },
  {
    baseline: 'Our platform delivers enterprise-grade security with end-to-end encryption. We ensure data protection at every level of your infrastructure.',
    current: 'Our platform delivers enterprise grade security with end to end encryption. We ensure data protection at every level of your infra structure.'
  },
  {
    baseline: 'Transform your business with cutting-edge technology solutions designed for modern enterprises. Our team brings decades of experience.',
    current: 'Transform you business with cutting edge technology solutions designed for modern enterprises. Our team brings decade of experience.'
  },
  {
    baseline: 'Schedule a consultation today to discover how we can help accelerate your digital transformation journey.',
    current: 'Schedule a consulation today to discover how we can help accelrate your digital transformation journey.'
  }
];

function generateIssues(count: number): Issue[] {
  const issues: Issue[] = [];
  let screenshotCount = 0;
  let textCount = 0;

  for (let i = 0; i < count; i++) {
    const issueType: IssueType = Math.random() > 0.5 ? 'screenshot' : 'text';

    if (issueType === 'screenshot') {
      issues.push({
        id: `issue-screenshot-${screenshotCount}`,
        page: pages[Math.floor(Math.random() * pages.length)],
        type: 'screenshot',
        status: 'pending',
        baselineScreenshot: sampleScreenshots[Math.floor(Math.random() * sampleScreenshots.length)],
        currentScreenshot: sampleScreenshots[Math.floor(Math.random() * sampleScreenshots.length)],
        differenceScreenshot: sampleScreenshots[Math.floor(Math.random() * sampleScreenshots.length)],
      });
      screenshotCount++;
    } else {
      const textChange = sampleTextChanges[Math.floor(Math.random() * sampleTextChanges.length)];
      issues.push({
        id: `issue-text-${textCount}`,
        page: pages[Math.floor(Math.random() * pages.length)],
        type: 'text',
        status: 'pending',
        baselineText: textChange.baseline,
        currentText: textChange.current,
      });
      textCount++;
    }
  }

  return issues;
}

// Import same website names from Phase 1
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

export function generatePhase2Data(): Phase2Website[] {
  return websiteNames.map((name, index) => {
    const issueCount = Math.floor(Math.random() * 8) + 1;
    const issues = generateIssues(issueCount);

    return {
      id: `website-${index}`,
      name,
      url: `https://${name.toLowerCase().replace(/\s+/g, '')}.com`,
      totalIssues: issueCount,
      issues,
    };
  });
}
