// Display-only labels. Keep the original names and verification metadata intact.
export const displayName = value => String(value ?? '')
  .replace(/客廳外牆窗/g, '客廳')
  .replace(/（(?:配準估算|估算|未核實)）/g, '')
  .replace(/\((?:estimated|approximate|unverified)\)/gi, '')
  .replace(/窗$/g, '')
  .trim();
