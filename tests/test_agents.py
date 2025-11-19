"""Tests for Echo agents."""

import pytest
from echo.core.agent import EchoCore
from echo.earn.agent import EchoEarn
from echo.keeper.agent import EchoKeeper


class TestEchoCore:
    """Tests for ECHO_CORE agent."""

    def test_initialization(self):
        """Test agent initializes correctly."""
        agent = EchoCore()
        assert agent.name == "ECHO_CORE"
        assert agent.state["status"] == "initialized"

    def test_run_cycle(self):
        """Test agent runs a complete cycle."""
        agent = EchoCore()
        result = agent.run()
        assert "evaluated" in result or "error" in result
        assert agent.state["run_count"] == 1

    def test_detect_value_leak(self):
        """Test value leak detection."""
        agent = EchoCore()
        agent.run()  # Set baseline
        # Initially should not detect leak
        assert not agent.detect_value_leak()

    def test_add_problem(self):
        """Test adding problems to queue."""
        agent = EchoCore()
        problem_id = agent.add_problem({
            "description": "Test problem",
            "complexity": 0.5
        })
        assert problem_id is not None
        assert len(agent.problem_queue) == 1

    def test_sharpen_mind(self):
        """Test self-improvement proposals."""
        agent = EchoCore()
        improvements = agent.sharpen_mind()
        assert isinstance(improvements, list)

    def test_get_status(self):
        """Test status reporting."""
        agent = EchoCore()
        status = agent.get_status()
        assert status["agent"] == "ECHO_CORE"
        assert "run_count" in status


class TestEchoEarn:
    """Tests for ECHO_EARN agent."""

    def test_initialization(self):
        """Test agent initializes correctly."""
        agent = EchoEarn()
        assert agent.name == "ECHO_EARN"
        assert len(agent.scanners) > 0

    def test_scan_opportunities(self):
        """Test opportunity scanning."""
        agent = EchoEarn()
        opportunities = agent.scan_opportunities()
        assert isinstance(opportunities, list)
        assert len(opportunities) > 0

    def test_finds_profit(self):
        """Test profit detection."""
        agent = EchoEarn()
        agent.run()  # Generate opportunities
        # Should find profit after scanning
        result = agent.finds_profit()
        assert isinstance(result, bool)

    def test_run_cycle(self):
        """Test complete earn cycle."""
        agent = EchoEarn()
        result = agent.run()
        assert "opportunities_found" in result
        assert "profit_generated" in result

    def test_get_status(self):
        """Test status reporting."""
        agent = EchoEarn()
        status = agent.get_status()
        assert status["agent"] == "ECHO_EARN"
        assert "total_profit" in status


class TestEchoKeeper:
    """Tests for ECHO_KEEPER agent."""

    def test_initialization(self):
        """Test agent initializes correctly."""
        agent = EchoKeeper()
        assert agent.name == "ECHO_KEEPER"

    def test_health_check(self):
        """Test health check execution."""
        agent = EchoKeeper()
        report = agent.run_health_check()
        assert "overall_status" in report
        assert "checks" in report
        assert "disk" in report["checks"]
        assert "memory" in report["checks"]
        assert "cpu" in report["checks"]

    def test_run_cycle(self):
        """Test complete keeper cycle."""
        agent = EchoKeeper()
        result = agent.run()
        assert "health_status" in result
        assert "checks_performed" in result

    def test_get_status(self):
        """Test status reporting."""
        agent = EchoKeeper()
        status = agent.get_status()
        assert status["agent"] == "ECHO_KEEPER"
        assert "health_checks_performed" in status


class TestIntegration:
    """Integration tests for Echo system."""

    def test_all_agents_initialize(self):
        """Test all agents can initialize together."""
        core = EchoCore()
        earn = EchoEarn()
        keeper = EchoKeeper()

        assert core.state["status"] == "initialized"
        assert earn.state["status"] == "initialized"
        assert keeper.state["status"] == "initialized"

    def test_event_bus_communication(self):
        """Test agents can communicate via event bus."""
        from echo.common.events import EventBus

        bus = EventBus()
        received = []

        def handler(event):
            received.append(event)

        bus.subscribe("test_event", handler)
        bus.publish("test_event", {"data": "test"}, "test")

        assert len(received) == 1
        assert received[0]["data"]["data"] == "test"
