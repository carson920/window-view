export function validateCamera(camera) {
  if (!camera) return false;
  const ranges = { latitude: [-90, 90], longitude: [-180, 180], altitude: [-1000, 100000], heading: [0, 360], tilt: [0, 180], roll: [-180, 180] };
  return Object.entries(ranges).every(([key, [min, max]]) => typeof camera[key] === 'number' && Number.isFinite(camera[key]) && camera[key] >= min && camera[key] <= max);
}
export function buildLandsdViewUrl(camera) {
  if (!validateCamera(camera)) throw new Error('Invalid or missing camera parameters');
  const values = ['latitude', 'longitude', 'altitude', 'heading', 'tilt', 'roll'].map(key => camera[key]);
  return `https://3d.map.gov.hk/mapviewer/app/map?flyto=${values.join(',')}&l=zh-HK`;
}
