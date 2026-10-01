/**
 * Ranks one candidate split of a caption page into two lines — lower is better.
 *
 * Only *valid* candidates reach this function: both lines fit the width, the first
 * line never ends with a one-letter word and the second never starts with a dash.
 * So this is purely about taste: which of the legal breaks reads most naturally?
 *
 * Ideas a Polish reader might care about:
 *  - balanced lines vs. a "pyramid" (shorter top line),
 *  - breaking right after punctuation (a natural pause in speech),
 *  - not separating short prepositions (na, do, od, po, za, ze, we) from their noun.
 */
export function scoreLineBreak(first: string, second: string): number {
  return Math.abs(first.length - second.length);
}
