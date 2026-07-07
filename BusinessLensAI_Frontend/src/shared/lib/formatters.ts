/**
 * Centralized formatting utilities for currency, numbers, percentages, and dates
 */
import { format, formatDistanceToNow, isValid, parseISO } from 'date-fns';

export type CurrencyCode = 'USD' | 'INR' | 'EUR' | 'GBP';

const CURRENCY_SYMBOLS: Record<CurrencyCode, string> = {
  USD: '$',
  INR: '₹',
  EUR: '€',
  GBP: '£',
};

/**
 * Format numeric value as currency with optional abbreviations (K, M, Cr, B)
 */
export function formatCurrency(
  value: number | undefined | null,
  currency: CurrencyCode = 'USD',
  useAbbreviation = true
): string {
  if (value === undefined || value === null || isNaN(value)) {
    return `${CURRENCY_SYMBOLS[currency] || '$'}0`;
  }

  const symbol = CURRENCY_SYMBOLS[currency] || '$';
  const absVal = Math.abs(value);
  const sign = value < 0 ? '-' : '';

  if (!useAbbreviation) {
    return `${sign}${symbol}${absVal.toLocaleString('en-US', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 2,
    })}`;
  }

  // Indian Rupee specific Crore (Cr) and Lakh (L) handling if INR
  if (currency === 'INR') {
    if (absVal >= 10000000) {
      return `${sign}${symbol}${(absVal / 10000000).toFixed(2)} Cr`;
    }
    if (absVal >= 100000) {
      return `${sign}${symbol}${(absVal / 100000).toFixed(2)} L`;
    }
  }

  // Standard K / M / B abbreviations
  if (absVal >= 1000000000) {
    return `${sign}${symbol}${(absVal / 1000000000).toFixed(2)}B`;
  }
  if (absVal >= 1000000) {
    return `${sign}${symbol}${(absVal / 1000000).toFixed(2)}M`;
  }
  if (absVal >= 1000) {
    return `${sign}${symbol}${(absVal / 1000).toFixed(1)}K`;
  }

  return `${sign}${symbol}${absVal.toFixed(absVal % 1 === 0 ? 0 : 2)}`;
}

/**
 * Format standard large numbers with optional abbreviations
 */
export function formatNumber(value: number | undefined | null, useAbbreviation = true): string {
  if (value === undefined || value === null || isNaN(value)) {
    return '0';
  }

  const absVal = Math.abs(value);
  const sign = value < 0 ? '-' : '';

  if (!useAbbreviation) {
    return `${sign}${absVal.toLocaleString('en-US')}`;
  }

  if (absVal >= 1000000000) return `${sign}${(absVal / 1000000000).toFixed(1)}B`;
  if (absVal >= 1000000) return `${sign}${(absVal / 1000000).toFixed(1)}M`;
  if (absVal >= 1000) return `${sign}${(absVal / 1000).toFixed(1)}K`;

  return `${sign}${absVal.toLocaleString('en-US')}`;
}

/**
 * Format percentage with explicit sign or standard format
 */
export function formatPercentage(value: number | undefined | null, decimals = 1, showSign = false): string {
  if (value === undefined || value === null || isNaN(value)) {
    return '0.0%';
  }

  const formatted = value.toFixed(decimals);
  if (showSign && value > 0) {
    return `+${formatted}%`;
  }
  return `${formatted}%`;
}

/**
 * Parse and format date strings safely
 */
export function formatDate(dateInput: string | Date | undefined | null, formatStr = 'MMM dd, yyyy'): string {
  if (!dateInput) return 'N/A';
  try {
    const dateObj = typeof dateInput === 'string' ? parseISO(dateInput) : dateInput;
    if (!isValid(dateObj)) {
      // Try regular Date constructor as fallback
      const fallbackDate = new Date(dateInput);
      if (isValid(fallbackDate)) {
        return format(fallbackDate, formatStr);
      }
      return 'Invalid Date';
    }
    return format(dateObj, formatStr);
  } catch {
    return 'Invalid Date';
  }
}

/**
 * Format date time with hours and minutes
 */
export function formatDateTime(dateInput: string | Date | undefined | null): string {
  return formatDate(dateInput, 'MMM dd, yyyy HH:mm');
}

/**
 * Format relative time (e.g. "5 minutes ago")
 */
export function formatTimeAgo(dateInput: string | Date | undefined | null): string {
  if (!dateInput) return 'just now';
  try {
    const dateObj = typeof dateInput === 'string' ? parseISO(dateInput) : dateInput;
    if (!isValid(dateObj)) {
      const fallbackDate = new Date(dateInput);
      if (isValid(fallbackDate)) {
        return formatDistanceToNow(fallbackDate, { addSuffix: true });
      }
      return 'recently';
    }
    return formatDistanceToNow(dateObj, { addSuffix: true });
  } catch {
    return 'recently';
  }
}
