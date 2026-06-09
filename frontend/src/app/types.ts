// Phase 1 Types - Website Status Monitoring
export type WebsiteStatus = 'Good' | 'Slow' | 'Very Slow' | 'Server Down' | 'Website Down';

export interface Phase1Website {
  id: string;
  name: string;
  url: string;
  status: WebsiteStatus;
  responseTime: number;
  httpCode: number;
  httpMessage: string;
}

// Phase 2 Types - DP Testing Errors
export type IssueType = 'screenshot' | 'text';
export type IssueStatus = 'pending' | 'approved' | 'rejected';

export interface Issue {
  id: string;
  page: string;
  type: IssueType;
  status: IssueStatus;
  // Screenshot type fields
  baselineScreenshot?: string;
  currentScreenshot?: string;
  differenceScreenshot?: string;
  // Text difference type fields
  baselineText?: string;
  currentText?: string;
}

export interface Phase2Website {
  id: string;
  name: string;
  url: string;
  totalIssues: number;
  issues: Issue[];
}
