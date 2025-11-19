"""
ECHO ORGANISM v2.1 - COMPREHENSIVE TEST SUITE
Classification: VALIDATION PROTOCOL

Tests:
- State validation
- Manifold constraints
- Dynamics stability
- Safety properties
- Performance benchmarks
"""

import numpy as np
import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.states import CreativeState, HomeostaticState
from src.core.manifolds import project_to_simplex, project_to_sphere, validate_simplex, validate_sphere
from src.core.energy import GlobalEnergyFunction
from src.dynamics.coupling import phi, psi, g_gain_adaptation
from src.dynamics.gradients import GradientComputer
from src.memory.memory_system import MemorySystem
from src.organism import EchoOrganism


def test_creative_state():
    """Test CreativeState creation and validation"""
    print("Testing CreativeState...")

    # Random creation
    x = CreativeState.random()
    assert x.continuous.shape == (512,), "Wrong continuous shape"
    assert x.probabilistic.shape == (128,), "Wrong probabilistic shape"
    assert x.semantic.shape == (256,), "Wrong semantic shape"

    # Simplex constraint
    assert abs(np.sum(x.probabilistic) - 1.0) < 1e-4, "Simplex sum failed"
    assert np.all(x.probabilistic >= 0), "Simplex negativity"

    # Sphere constraint
    assert abs(np.linalg.norm(x.semantic) - 1.0) < 1e-4, "Sphere norm failed"

    # Checksum
    assert x.verify_integrity(), "Checksum failed"

    # Flat conversion
    x_flat = x.to_flat()
    assert len(x_flat) == 896, "Wrong flat dimension"

    x_reconstructed = CreativeState.from_flat(x_flat)
    assert np.allclose(x.continuous, x_reconstructed.continuous), "Reconstruction failed"

    print("  CreativeState: PASS")
    return True


def test_homeostatic_state():
    """Test HomeostaticState creation and bounds"""
    print("Testing HomeostaticState...")

    h = HomeostaticState.initial()
    assert h.resources.shape == (3,), "Wrong resources shape"
    assert h.stress.shape == (2,), "Wrong stress shape"
    assert h.gains.shape == (3,), "Wrong gains shape"

    # Bounds
    assert np.all(h.resources >= 0) and np.all(h.resources <= 1), "Resources out of bounds"
    assert np.all(h.stress >= 0) and np.all(h.stress <= 1), "Stress out of bounds"
    assert np.all(h.gains >= h.KAPPA_MIN) and np.all(h.gains <= h.KAPPA_MAX), "Gains out of bounds"

    print("  HomeostaticState: PASS")
    return True


def test_manifold_projections():
    """Test manifold projection functions"""
    print("Testing manifold projections...")

    # Simplex
    v = np.random.randn(128)
    p = project_to_simplex(v)
    assert validate_simplex(p), "Simplex projection failed"

    # Sphere
    v = np.random.randn(256)
    s = project_to_sphere(v)
    assert validate_sphere(s), "Sphere projection failed"

    # Edge cases
    p_zeros = project_to_simplex(np.zeros(128))
    assert validate_simplex(p_zeros), "Zero simplex projection failed"

    s_zeros = project_to_sphere(np.zeros(256))
    assert validate_sphere(s_zeros), "Zero sphere projection failed"

    print("  Manifold projections: PASS")
    return True


def test_energy_function():
    """Test global energy function"""
    print("Testing energy function...")

    energy_fn = GlobalEnergyFunction()

    x_flat = CreativeState.random().to_flat()
    x_prev_flat = CreativeState.random().to_flat()
    memory = [CreativeState.random().to_flat() for _ in range(5)]
    constraints = (0.5, 1.0, 1.0)

    # Compute energy
    E = energy_fn.compute_energy(x_flat, x_prev_flat, memory, constraints)
    assert np.isfinite(E), "Energy is not finite"

    # Compute gradient
    grad = energy_fn.compute_energy_gradient(x_flat, x_prev_flat, memory, constraints)
    assert len(grad) == 896, f"Wrong gradient dimension: {len(grad)}"
    assert np.all(np.isfinite(grad)), "Gradient contains non-finite values"

    # Detailed energy
    details = energy_fn.compute_detailed_energy(x_flat, x_prev_flat, memory, constraints)
    assert 'total' in details, "Missing total energy"
    assert abs(details['total'] - E) < 1e-10, "Energy mismatch"

    print("  Energy function: PASS")
    return True


def test_coupling_functions():
    """Test coupling functions phi, psi, g"""
    print("Testing coupling functions...")

    x_flat = CreativeState.random().to_flat()
    x_prev_flat = CreativeState.random().to_flat()
    memory = [CreativeState.random().to_flat() for _ in range(5)]

    # Phi
    influence = phi(x_flat, x_prev_flat, memory)
    assert len(influence) == 5, "Wrong influence dimension"
    assert np.all(influence >= 0) and np.all(influence <= 1), "Influence out of bounds"

    # Psi
    h = HomeostaticState.initial()
    constraints = psi(h.resources, h.stress, h.gains)
    assert len(constraints) == 3, "Wrong constraints dimension"
    b, lam, alpha = constraints
    assert 0 <= b <= 1, "b_explore out of bounds"
    assert 0 <= lam <= 5, "lambda_risk out of bounds"
    assert 0.1 <= alpha <= 2, "alpha_coherence out of bounds"

    # g
    adjustments = g_gain_adaptation(0.5, 0.5, 0.3)
    assert len(adjustments) == 3, "Wrong adjustments dimension"
    assert np.all(np.abs(adjustments) <= 0.03), "Adjustments too large"

    print("  Coupling functions: PASS")
    return True


def test_gradient_computer():
    """Test gradient computation"""
    print("Testing gradient computation...")

    gc = GradientComputer(method="analytical")
    energy_fn = GlobalEnergyFunction()

    x_flat = CreativeState.random().to_flat()
    x_prev_flat = CreativeState.random().to_flat()
    memory = [CreativeState.random().to_flat() for _ in range(5)]
    constraints = (0.5, 1.0, 1.0)

    grad = gc.compute_creative_gradient(x_flat, x_prev_flat, memory, constraints, energy_fn)

    assert len(grad) == 896, f"Wrong gradient dimension: {len(grad)}"
    assert np.all(np.isfinite(grad)), "Gradient contains non-finite"
    assert np.linalg.norm(grad) <= 2.0, f"Gradient too large: {np.linalg.norm(grad)}"

    print("  Gradient computer: PASS")
    return True


def test_memory_system():
    """Test memory system operations"""
    print("Testing memory system...")

    mem = MemorySystem(capacity=100)

    # Store
    for i in range(50):
        x_flat = CreativeState.random().to_flat()
        mem.store(x_flat, step=i)

    assert len(mem) == 50, f"Wrong memory size: {len(mem)}"

    # Retrieve
    state = mem.retrieve(0)
    assert state is not None, "Retrieve failed"
    assert len(state) == 896, "Wrong retrieved dimension"

    # Sample
    samples = mem.sample(10, method="entropy_weighted")
    assert len(samples) == 10, f"Wrong sample count: {len(samples)}"

    # Stats
    stats = mem.get_stats()
    assert 'size' in stats, "Missing stats"
    assert stats['error_rate'] == 0, "Unexpected errors"

    print("  Memory system: PASS")
    return True


def test_organism_short_run():
    """Test organism for 100 steps"""
    print("Testing organism (100 steps)...")

    org = EchoOrganism(seed=42)
    trajectory = org.run(100, verbose=False)

    assert len(trajectory) == 100, f"Wrong trajectory length: {len(trajectory)}"
    assert org.step_count == 100, "Step count mismatch"

    # Safety properties
    safety = org.validate_safety_properties()
    assert safety['bounded_exploration'], "Bounded exploration failed"
    assert safety['stress_bounded'], "Stress bounded failed"
    assert safety['energy_finite'], "Energy finite failed"

    metrics = org.get_metrics()
    assert metrics['basic']['novelty_mean'] > 0, "Novelty too low"
    assert metrics['stability']['bounded'], "Not bounded"

    print("  Organism (100 steps): PASS")
    return True


def test_organism_medium_run():
    """Test organism for 1000 steps"""
    print("Testing organism (1000 steps)...")

    org = EchoOrganism(seed=123)

    start = time.time()
    trajectory = org.run(1000, verbose=False)
    duration = time.time() - start

    assert len(trajectory) == 1000, f"Wrong trajectory length: {len(trajectory)}"

    safety = org.validate_safety_properties()
    all_pass = all(safety.values())

    metrics = org.get_metrics()
    novelty_mean = metrics['basic']['novelty_mean']
    stress_mean = metrics['basic']['stress_mean']

    print(f"    Duration: {duration:.2f}s ({1000/duration:.0f} steps/s)")
    print(f"    Novelty: {novelty_mean:.3f}, Stress: {stress_mean:.3f}")
    print(f"    Safety: {'PASS' if all_pass else 'FAIL'}")

    assert all_pass, f"Safety failed: {safety}"
    print("  Organism (1000 steps): PASS")
    return True


def test_organism_long_run():
    """Test organism for 10000 steps - full stability validation"""
    print("Testing organism (10000 steps)...")

    org = EchoOrganism(seed=456)

    start = time.time()
    trajectory = org.run(10000, verbose=False)
    duration = time.time() - start

    assert len(trajectory) == 10000, f"Wrong trajectory length: {len(trajectory)}"

    safety = org.validate_safety_properties()
    all_pass = all(safety.values())

    metrics = org.get_metrics()

    print(f"    Duration: {duration:.2f}s ({10000/duration:.0f} steps/s)")
    print(f"    Novelty: mean={metrics['basic']['novelty_mean']:.3f}, min={metrics['stability']['novelty_min']:.3f}")
    print(f"    Energy variance: {metrics['stability']['energy_variance']:.3f}")
    print(f"    Memory health: {metrics['system']['memory_health']:.3f}")

    if org.monitor:
        print(f"    Alert level: {org.monitor.current_alert_level.value}")

    assert all_pass, f"Safety failed: {safety}"
    assert metrics['stability']['novelty_min'] > 0.01, "Novelty collapsed"
    assert metrics['stability']['energy_variance'] < 10.0, "Energy unstable"

    print("  Organism (10000 steps): PASS")
    return True


def test_recovery_mechanisms():
    """Test state recovery under corruption"""
    print("Testing recovery mechanisms...")

    org = EchoOrganism(seed=789)

    # Run normally first
    org.run(100)

    # Corrupt state
    org.x.continuous[0] = np.nan
    org.x.continuous[1] = np.inf

    # Step should recover
    x_new, h_new = org.step()

    # Verify recovery worked
    assert np.all(np.isfinite(x_new.to_flat())), "Recovery failed - still has NaN/Inf"

    print("  Recovery mechanisms: PASS")
    return True


def run_all_tests():
    """Run complete test suite"""
    print("=" * 60)
    print("ECHO ORGANISM v2.1 - VALIDATION SUITE")
    print("=" * 60)
    print()

    tests = [
        test_creative_state,
        test_homeostatic_state,
        test_manifold_projections,
        test_energy_function,
        test_coupling_functions,
        test_gradient_computer,
        test_memory_system,
        test_organism_short_run,
        test_organism_medium_run,
        test_organism_long_run,
        test_recovery_mechanisms
    ]

    passed = 0
    failed = 0
    results = []

    for test in tests:
        try:
            success = test()
            if success:
                passed += 1
                results.append((test.__name__, "PASS"))
            else:
                failed += 1
                results.append((test.__name__, "FAIL"))
        except Exception as e:
            failed += 1
            results.append((test.__name__, f"ERROR: {e}"))
            print(f"  ERROR: {e}")

    print()
    print("=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)

    for name, result in results:
        status = "PASS" if result == "PASS" else "FAIL"
        print(f"  {name}: {status}")

    print()
    print(f"Total: {passed} passed, {failed} failed")

    if failed == 0:
        print()
        print("VALIDATION: PASS")
        print("Echo Organism v2.1 is ready for deployment")
        return True
    else:
        print()
        print("VALIDATION: FAIL")
        print("Please review failed tests")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
