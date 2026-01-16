import { useRef, useMemo, useState } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Stars, Html, Line } from '@react-three/drei'
import * as THREE from 'three'

// Scale factor
const AU_SCALE = 2;
const DEG_TO_RAD = Math.PI / 180;

// Convert user input to orbit visualization
// Since users input distance/velocity/angle, we simulate an orbit based on those
function userInputToOrbitParams(asteroid) {
    // Distance in km -> approximate semi-major axis (rough conversion)
    const distanceKm = asteroid.distance_km || 500000;
    const distanceAU = distanceKm / 149597870.7;

    // Create semi-major axis based on distance (scaled for visibility)
    // Close asteroids (< Moon distance ~384000km) get small orbits
    // Far asteroids get larger orbits
    const semiMajorAxis = Math.max(0.8, Math.min(3.0, 0.8 + Math.log10(distanceKm / 100000)));

    // Eccentricity from trajectory angle (lower angle = more eccentric/direct)
    const angle = asteroid.trajectory_angle_deg || 45;
    const eccentricity = Math.max(0.1, 0.7 - (angle / 90) * 0.6);

    // Random but deterministic orbital orientation based on name
    const nameHash = (asteroid.asteroid_name || 'asteroid').split('').reduce((a, b) => a + b.charCodeAt(0), 0);
    const inclination = (nameHash % 20);
    const longitudeAscendingNode = (nameHash * 7) % 360;
    const argumentPerihelion = (nameHash * 13) % 360;
    const meanAnomaly = (nameHash * 17) % 360;

    return {
        name: asteroid.asteroid_name || `NEO-${asteroid.id || '?'}`,
        semiMajorAxis,
        eccentricity,
        inclination,
        longitudeAscendingNode,
        argumentPerihelion,
        meanAnomaly,
        diameter_m: asteroid.diameter_m || 100,
        risk: asteroid.risk_level || 'Medium',
        distance_km: distanceKm,
        velocity_kms: asteroid.velocity_kms
    };
}

// Solve Kepler's equation iteratively
function solveKepler(M, e) {
    let E = M;
    for (let i = 0; i < 30; i++) {
        E = M + e * Math.sin(E);
    }
    return E;
}

// Get Cartesian position from orbital elements
function getPosition(params, dayOffset = 0) {
    const a = params.semiMajorAxis;
    const e = params.eccentricity;
    const i = params.inclination * DEG_TO_RAD;
    const Omega = params.longitudeAscendingNode * DEG_TO_RAD;
    const omega = params.argumentPerihelion * DEG_TO_RAD;

    const n = 2 * Math.PI / (Math.sqrt(a * a * a) * 365.25);
    const M = (params.meanAnomaly * DEG_TO_RAD + n * dayOffset) % (2 * Math.PI);
    const E = solveKepler(M, e);

    const nu = 2 * Math.atan2(
        Math.sqrt(1 + e) * Math.sin(E / 2),
        Math.sqrt(1 - e) * Math.cos(E / 2)
    );

    const r = a * (1 - e * Math.cos(E));
    const xOrb = r * Math.cos(nu);
    const yOrb = r * Math.sin(nu);

    const cosO = Math.cos(Omega), sinO = Math.sin(Omega);
    const cosI = Math.cos(i), sinI = Math.sin(i);
    const cosW = Math.cos(omega), sinW = Math.sin(omega);

    const x = (cosO * cosW - sinO * sinW * cosI) * xOrb + (-cosO * sinW - sinO * cosW * cosI) * yOrb;
    const y = (sinO * cosW + cosO * sinW * cosI) * xOrb + (-sinO * sinW + cosO * cosW * cosI) * yOrb;
    const z = (sinW * sinI) * xOrb + (cosW * sinI) * yOrb;

    return { x: x * AU_SCALE, y: z * AU_SCALE * 0.4, z: y * AU_SCALE };
}

// Generate orbit path points
function generateOrbitPath(params, numPoints = 60) {
    const points = [];
    const period = Math.sqrt(params.semiMajorAxis ** 3) * 365.25;

    for (let i = 0; i <= numPoints; i++) {
        const dayOffset = (i / numPoints) * period;
        const pos = getPosition(params, dayOffset);
        points.push([pos.x, pos.y, pos.z]);
    }
    return points;
}

// Sun component
function Sun() {
    return (
        <group>
            <mesh>
                <sphereGeometry args={[0.18, 32, 32]} />
                <meshBasicMaterial color="#FDB813" />
            </mesh>
            <pointLight color="#FDB813" intensity={1.5} distance={15} />
            <Html position={[0, 0.32, 0]} center style={{ pointerEvents: 'none' }}>
                <div style={{ fontSize: '10px', color: '#FDB813', background: 'rgba(0,0,0,0.6)', padding: '2px 6px', borderRadius: '6px' }}>
                    ☀️ Sun
                </div>
            </Html>
        </group>
    );
}

// Earth component
function Earth({ dayOffset }) {
    const angle = (dayOffset / 365.25) * Math.PI * 2;
    const x = Math.cos(angle) * AU_SCALE;
    const z = Math.sin(angle) * AU_SCALE;

    return (
        <group position={[x, 0, z]}>
            <mesh>
                <sphereGeometry args={[0.1, 32, 32]} />
                <meshStandardMaterial color="#1a4b8c" emissive="#1a4b8c" emissiveIntensity={0.2} />
            </mesh>
            <Html position={[0, 0.18, 0]} center style={{ pointerEvents: 'none' }}>
                <div style={{ fontSize: '10px', color: '#4da6ff', background: 'rgba(0,0,0,0.6)', padding: '2px 6px', borderRadius: '6px' }}>
                    🌍 Earth
                </div>
            </Html>
        </group>
    );
}

// Earth orbit ring
function EarthOrbit() {
    const points = useMemo(() => {
        const pts = [];
        for (let i = 0; i <= 64; i++) {
            const angle = (i / 64) * Math.PI * 2;
            pts.push([Math.cos(angle) * AU_SCALE, 0, Math.sin(angle) * AU_SCALE]);
        }
        return pts;
    }, []);
    return <Line points={points} color="#4da6ff" lineWidth={1} transparent opacity={0.3} />;
}

// Asteroid orbit path
function AsteroidOrbit({ params, color }) {
    const points = useMemo(() => generateOrbitPath(params), [params]);
    return <Line points={points} color={color} lineWidth={2} transparent opacity={0.5} />;
}

// Asteroid body with label
function AsteroidBody({ params, dayOffset, color }) {
    const meshRef = useRef();
    const [hovered, setHovered] = useState(false);

    const position = useMemo(() => getPosition(params, dayOffset), [params, dayOffset]);
    const size = params.risk === 'High' ? 0.14 : params.risk === 'Medium' ? 0.11 : 0.09;

    useFrame(() => {
        if (meshRef.current) {
            meshRef.current.rotation.x += 0.015;
            meshRef.current.rotation.y += 0.02;
        }
    });

    return (
        <group position={[position.x, position.y, position.z]}>
            {/* Asteroid mesh */}
            <mesh
                ref={meshRef}
                onPointerOver={(e) => { e.stopPropagation(); setHovered(true); document.body.style.cursor = 'pointer'; }}
                onPointerOut={() => { setHovered(false); document.body.style.cursor = 'default'; }}
            >
                <icosahedronGeometry args={[size, 1]} />
                <meshStandardMaterial
                    color={hovered ? '#ffffff' : color}
                    emissive={color}
                    emissiveIntensity={0.4}
                    roughness={0.5}
                />
            </mesh>

            {/* Glow ring */}
            <mesh rotation={[Math.PI / 2, 0, 0]}>
                <ringGeometry args={[size * 1.3, size * 1.6, 16]} />
                <meshBasicMaterial color={color} transparent opacity={0.25} side={THREE.DoubleSide} />
            </mesh>

            {/* Always visible label */}
            <Html position={[0, size + 0.12, 0]} center style={{ pointerEvents: 'none' }}>
                <div style={{
                    fontSize: '11px',
                    fontWeight: 'bold',
                    color: color,
                    background: 'rgba(0,0,0,0.7)',
                    padding: '3px 8px',
                    borderRadius: '6px',
                    border: `1px solid ${color}`,
                    whiteSpace: 'nowrap'
                }}>
                    {params.name}
                </div>
            </Html>

            {/* Hover tooltip */}
            {hovered && (
                <Html position={[size + 0.2, 0, 0]} style={{ pointerEvents: 'none' }}>
                    <div className="asteroid-tooltip">
                        <div className="tooltip-header">
                            <span className={`tooltip-risk ${params.risk?.toLowerCase()}`}>{params.risk}</span>
                            <strong>{params.name}</strong>
                        </div>
                        <div className="tooltip-body">
                            <div className="tooltip-row"><span>Distance:</span><span>{params.distance_km?.toLocaleString()} km</span></div>
                            <div className="tooltip-row"><span>Velocity:</span><span>{params.velocity_kms} km/s</span></div>
                            <div className="tooltip-row"><span>Diameter:</span><span>{params.diameter_m?.toLocaleString()} m</span></div>
                            <div className="tooltip-row"><span>Orbit (AU):</span><span>{params.semiMajorAxis?.toFixed(2)}</span></div>
                        </div>
                    </div>
                </Html>
            )}
        </group>
    );
}

// Main Scene
function Scene({ asteroids }) {
    const [dayOffset, setDayOffset] = useState(0);

    useFrame((state, delta) => {
        setDayOffset(prev => prev + delta * 3);
    });

    const getRiskColor = (risk) => {
        switch (risk) {
            case 'High': return '#ff4444';
            case 'Medium': return '#ffcc00';
            case 'Low': return '#44ff44';
            default: return '#888888';
        }
    };

    // Convert user asteroids to orbital params
    const orbitalAsteroids = useMemo(() => {
        return asteroids.map(ast => userInputToOrbitParams(ast));
    }, [asteroids]);

    return (
        <>
            <ambientLight intensity={0.25} />
            <Stars radius={100} depth={50} count={2500} factor={4} saturation={0} fade speed={0.3} />

            <Sun />
            <EarthOrbit />
            <Earth dayOffset={dayOffset} />

            {orbitalAsteroids.map((params, idx) => (
                <group key={params.name + idx}>
                    <AsteroidOrbit params={params} color={getRiskColor(params.risk)} />
                    <AsteroidBody params={params} dayOffset={dayOffset} color={getRiskColor(params.risk)} />
                </group>
            ))}

            <OrbitControls enableZoom={true} enablePan={true} minDistance={2} maxDistance={15} />
        </>
    );
}

// Main component
export default function EarthViewer({ asteroids = [] }) {
    const hasAsteroids = asteroids.length > 0;

    return (
        <div className="earth-viewer" style={{ height: '450px' }}>
            <Canvas camera={{ position: [0, 3, 6], fov: 55 }}>
                <Scene asteroids={asteroids} />
            </Canvas>

            <div className="viewer-legend">
                <div className="legend-title">🛰️ Your Searched Asteroids</div>
                <div className="legend-item"><span className="legend-dot" style={{ background: '#44ff44' }}></span>Low Risk</div>
                <div className="legend-item"><span className="legend-dot" style={{ background: '#ffcc00' }}></span>Medium Risk</div>
                <div className="legend-item"><span className="legend-dot" style={{ background: '#ff4444' }}></span>High Risk</div>
            </div>

            {!hasAsteroids && (
                <div className="viewer-empty">
                    <p>🔍 Submit a prediction to see asteroids here</p>
                </div>
            )}

            <div className="viewer-instructions">
                {hasAsteroids
                    ? `${asteroids.length} asteroid${asteroids.length > 1 ? 's' : ''} • Hover for details`
                    : 'Enter asteroid data and click Analyze to visualize'
                }
            </div>
        </div>
    );
}
