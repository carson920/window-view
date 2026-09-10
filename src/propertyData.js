export const getEstate = (data, id) => data.estates.find(item => item.id === id);
export const getBuildings = (data, estateId) => getEstate(data, estateId)?.buildings ?? [];
export const getFlats = (data, estateId, buildingId) => getBuildings(data, estateId).find(item => item.id === buildingId)?.flats ?? [];
export const getWindows = (data, estateId, buildingId, flatId) => getFlats(data, estateId, buildingId).find(item => item.id === flatId)?.windows ?? [];
export function getFloors(building) {
  if (!building?.floors) return [];
  const { min, max, excluded = [] } = building.floors;
  if (!Number.isInteger(min) || !Number.isInteger(max) || max < min) return [];
  return Array.from({ length: max - min + 1 }, (_, i) => min + i).filter(floor => !excluded.includes(floor));
}
