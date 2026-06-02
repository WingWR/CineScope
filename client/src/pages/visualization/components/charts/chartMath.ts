export function scaleLinear(value: number, domain: [number, number], range: [number, number]): number {
  const [domainMin, domainMax] = domain;
  const [rangeMin, rangeMax] = range;
  if (domainMax === domainMin) {
    return (rangeMin + rangeMax) / 2;
  }

  return rangeMin + ((value - domainMin) / (domainMax - domainMin)) * (rangeMax - rangeMin);
}

export function linePath(points: Array<{ x: number; y: number }>): string {
  return points.map((point, index) => `${index === 0 ? "M" : "L"} ${point.x.toFixed(1)} ${point.y.toFixed(1)}`).join(" ");
}
