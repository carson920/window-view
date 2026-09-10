import { getFloors } from './propertyData.js';
import { validateCamera } from './landsdUrl.js';
const finite = value => typeof value === 'number' && Number.isFinite(value);
export function calculateAltitude(model, floor, eyeHeight = 1.5, synthetic = false) {
  const estimated = model?.allowEstimated === true && model?.confidence === 'estimated';
  if (!model || !finite(floor) || !finite(eyeHeight) || (model.verified !== true && !synthetic && !estimated)) return null;
  if (model.type === 'lookup') return finite(model.altitudes?.[floor]) ? model.altitudes[floor] + eyeHeight : null;
  if (model.type !== 'formula' || ![model.referenceFloor, model.referenceAltitude, model.floorToFloor].every(finite) || model.floorToFloor <= 0) return null;
  return model.referenceAltitude + (floor - model.referenceFloor) * model.floorToFloor + eyeHeight;
}
export function calculateCamera(estate, building, window, floor, eyeHeight = 1.5) {
  if (!window || !building || !getFloors(building).includes(floor)) return null;
  const synthetic = estate?.synthetic === true;
  const approximate = window.allowApproximate === true && window.confidence === 'review';
  if (!synthetic && !approximate && (window.windowVerified !== true || !['verified', 'high'].includes(window.confidence))) return null;
  if (window.confidence === 'unresolved') return null;
  const altitude = calculateAltitude(building.floorModel, floor, eyeHeight, synthetic);
  const camera = { latitude: window.latitude, longitude: window.longitude, altitude, heading: window.heading, tilt: window.tilt, roll: window.roll ?? 0 };
  return validateCamera(camera) ? camera : null;
}
