/**
 * Orbital Mechanics Calculations for Frontend Visualization
 * 
 * Implements Kepler's equations to compute accurate asteroid positions
 * based on orbital elements.
 */

// Constants
const AU_TO_KM = 149597870.7;
const DEG_TO_RAD = Math.PI / 180;
const RAD_TO_DEG = 180 / Math.PI;

/**
 * Solve Kepler's equation: M = E - e*sin(E)
 * Uses Newton-Raphson iteration
 */
function solveKeplerEquation(M, e, tolerance = 1e-10, maxIter = 100) {
    let E = e < 0.8 ? M : Math.PI;

    for (let i = 0; i < maxIter; i++) {
        const f = E - e * Math.sin(E) - M;
        const fPrime = 1 - e * Math.cos(E);
        const E_new = E - f / fPrime;

        if (Math.abs(E_new - E) < tolerance) {
            return E_new;
        }
        E = E_new;
    }
    return E;
}

/**
 * Convert Eccentric Anomaly to True Anomaly
 */
function eccentricToTrueAnomaly(E, e) {
    const beta = e / (1 + Math.sqrt(1 - e * e));
    return E + 2 * Math.atan2(beta * Math.sin(E), 1 - beta * Math.cos(E));
}

/**
 * Calculate orbital radius at given true anomaly
 */
function orbitalRadius(a, e, nu) {
    return a * (1 - e * e) / (1 + e * Math.cos(nu));
}

/**
 * Calculate mean motion in radians/day
 */
function meanMotion(a_au) {
    const periodYears = Math.sqrt(a_au ** 3);
    const periodDays = periodYears * 365.25;
    return 2 * Math.PI / periodDays;
}

/**
 * Convert orbital elements to Cartesian coordinates
 * Returns position in AU (scaled for visualization)
 */
export function orbitalElementsToCartesian(elements, daysSinceEpoch = 0) {
    const {
        semiMajorAxis,    // a in AU
        eccentricity,     // e
        inclination,      // i in degrees
        longitudeAscendingNode, // Ω in degrees
        argumentPerihelion,     // ω in degrees
        meanAnomaly       // M in degrees at epoch
    } = elements;

    // Convert to radians
    const a = semiMajorAxis;
    const e = eccentricity;
    const i = inclination * DEG_TO_RAD;
    const Omega = longitudeAscendingNode * DEG_TO_RAD;
    const omega = argumentPerihelion * DEG_TO_RAD;

    // Propagate mean anomaly
    const n = meanMotion(a);
    const M = ((meanAnomaly * DEG_TO_RAD) + n * daysSinceEpoch) % (2 * Math.PI);

    // Solve Kepler's equation
    const E = solveKeplerEquation(M, e);

    // True anomaly
    const nu = eccentricToTrueAnomaly(E, e);

    // Radius (in AU)
    const r = orbitalRadius(a, e, nu);

    // Position in orbital plane
    const xOrbital = r * Math.cos(nu);
    const yOrbital = r * Math.sin(nu);

    // Rotation matrices to ecliptic frame
    const cosOmega = Math.cos(omega);
    const sinOmega = Math.sin(omega);
    const x1 = cosOmega * xOrbital - sinOmega * yOrbital;
    const y1 = sinOmega * xOrbital + cosOmega * yOrbital;

    const cosI = Math.cos(i);
    const sinI = Math.sin(i);
    const x2 = x1;
    const y2 = cosI * y1;
    const z2 = sinI * y1;

    const cosOmegaNode = Math.cos(Omega);
    const sinOmegaNode = Math.sin(Omega);
    const x = cosOmegaNode * x2 - sinOmegaNode * y2;
    const y = sinOmegaNode * x2 + cosOmegaNode * y2;
    const z = z2;

    return { x, y, z };
}

/**
 * Generate orbit path points for visualization
 */
export function generateOrbitPath(elements, numPoints = 100) {
    const points = [];
    const periodYears = Math.sqrt(elements.semiMajorAxis ** 3);
    const periodDays = periodYears * 365.25;

    for (let i = 0; i <= numPoints; i++) {
        const dayOffset = (i / numPoints) * periodDays;
        const pos = orbitalElementsToCartesian(elements, dayOffset);
        points.push([pos.x, pos.y, pos.z]);
    }

    return points;
}

/**
 * Calculate Earth's position (simplified circular orbit)
 */
export function getEarthPosition(dayOfYear) {
    const angle = (dayOfYear / 365.25) * 2 * Math.PI;
    return {
        x: Math.cos(angle),
        y: Math.sin(angle),
        z: 0
    };
}

/**
 * Calculate distance between two positions
 */
export function calculateDistance(pos1, pos2) {
    return Math.sqrt(
        (pos1.x - pos2.x) ** 2 +
        (pos1.y - pos2.y) ** 2 +
        (pos1.z - pos2.z) ** 2
    );
}

/**
 * Known asteroid orbital elements
 */
export const KNOWN_ASTEROIDS = {
    apophis: {
        name: "99942 Apophis",
        semiMajorAxis: 0.9224,
        eccentricity: 0.1911,
        inclination: 3.331,
        longitudeAscendingNode: 204.446,
        argumentPerihelion: 126.393,
        meanAnomaly: 180.0,
        diameter_m: 370,
        risk: "High"
    },
    bennu: {
        name: "101955 Bennu",
        semiMajorAxis: 1.126,
        eccentricity: 0.2037,
        inclination: 6.035,
        longitudeAscendingNode: 2.060,
        argumentPerihelion: 66.223,
        meanAnomaly: 101.7,
        diameter_m: 492,
        risk: "Medium"
    },
    eros: {
        name: "433 Eros",
        semiMajorAxis: 1.458,
        eccentricity: 0.2229,
        inclination: 10.829,
        longitudeAscendingNode: 304.3,
        argumentPerihelion: 178.9,
        meanAnomaly: 320.0,
        diameter_m: 16840,
        risk: "Low"
    },
    apollo: {
        name: "1862 Apollo",
        semiMajorAxis: 1.471,
        eccentricity: 0.560,
        inclination: 6.35,
        longitudeAscendingNode: 35.7,
        argumentPerihelion: 285.9,
        meanAnomaly: 45.0,
        diameter_m: 1500,
        risk: "High"
    },
    toutatis: {
        name: "4179 Toutatis",
        semiMajorAxis: 2.511,
        eccentricity: 0.629,
        inclination: 0.447,
        longitudeAscendingNode: 128.2,
        argumentPerihelion: 274.8,
        meanAnomaly: 190.0,
        diameter_m: 2450,
        risk: "Medium"
    }
};

export default {
    orbitalElementsToCartesian,
    generateOrbitPath,
    getEarthPosition,
    calculateDistance,
    KNOWN_ASTEROIDS
};
