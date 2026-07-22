import type { ComponentType } from 'react';
import {
  FormatStation,
  FramingStation,
  HighlightingStation,
  KeywordsStation,
  ParaphraseStation,
  SpacingStation,
  SummarizeStation,
  type StationProps,
} from './StationForms';

export interface StationDef {
  id: string;
  title: string;
  emoji: string;
  description: string;
  group: 'Make it readable' | 'Understand it';
  requiresAI: boolean;
  Component: ComponentType<StationProps>;
}

export const STATIONS: StationDef[] = [
  {
    id: 'format',
    title: 'Colour & style',
    emoji: '🎨',
    description: 'Colour titles, headings and text to make structure clear.',
    group: 'Make it readable',
    requiresAI: false,
    Component: FormatStation,
  },
  {
    id: 'spacing',
    title: 'Breathing room',
    emoji: '↕️',
    description: 'Add calm space between paragraphs or sentences.',
    group: 'Make it readable',
    requiresAI: false,
    Component: SpacingStation,
  },
  {
    id: 'framing',
    title: 'Frames & borders',
    emoji: '🖼️',
    description: 'Draw gentle boxes around sections, paragraphs or sentences.',
    group: 'Make it readable',
    requiresAI: false,
    Component: FramingStation,
  },
  {
    id: 'highlighting',
    title: 'Word highlighting',
    emoji: '🖊️',
    description: 'Highlight nouns, verbs and more to aid focus.',
    group: 'Make it readable',
    requiresAI: false,
    Component: HighlightingStation,
  },
  {
    id: 'keywords',
    title: 'Section keywords',
    emoji: '🔑',
    description: 'Add the key words above each section.',
    group: 'Understand it',
    requiresAI: true,
    Component: KeywordsStation,
  },
  {
    id: 'summarize',
    title: 'Summary',
    emoji: '📝',
    description: 'Get a shorter version of the whole document.',
    group: 'Understand it',
    requiresAI: true,
    Component: SummarizeStation,
  },
  {
    id: 'paraphrase',
    title: 'Rephrase',
    emoji: '💬',
    description: 'Rewrite the text in a simpler, easier style.',
    group: 'Understand it',
    requiresAI: true,
    Component: ParaphraseStation,
  },
];

export const STATION_GROUPS: StationDef['group'][] = [
  'Make it readable',
  'Understand it',
];
