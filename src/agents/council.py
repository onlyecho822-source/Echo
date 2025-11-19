"""
Echo Life OS - Echo Council
===========================
Multi-agent orchestration system using LangGraph.

The Council coordinates specialized agents to handle complex tasks
with different reasoning modes and capabilities.
"""

import os
from typing import TypedDict, Annotated, Sequence, Literal, Optional, Dict, Any, List
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import json

# LangGraph imports
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

# LangChain imports for LLM integration
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI


class EthicsMode(Enum):
    """
    Ethics Dimmer - Controls reasoning texture.

    Higher levels are more conservative, lower levels more direct.
    All levels maintain ethical boundaries - they change depth, not safety.
    """
    L5_SAFE_HARBOR = 5    # Conservative, friendly, suitable for sensitive tasks
    L4_RED_TEAM = 4       # Threat modeling, defensive predictions
    L3_GREY_ZONE = 3      # Competitive intelligence, structural analysis
    L2_BLACK_LENS = 2     # Raw analysis, full consequence mapping


class TaskCategory(Enum):
    """Categories for task routing."""
    OPPORTUNITY = "opportunity"      # Scout agent
    CREATION = "creation"            # Builder agent
    COMPLIANCE = "compliance"        # Auditor agent
    STRATEGY = "strategy"            # Navigator agent
    RISK = "risk"                    # Devil Lens agent
    PATTERN = "pattern"              # Mapper agent
    ARBITRATION = "arbitration"      # Judge agent
    GENERAL = "general"              # Cortex handles directly


@dataclass
class AgentConfig:
    """Configuration for an individual agent."""
    name: str
    role: str
    system_prompt: str
    capabilities: List[str]
    temperature: float = 0.7


class CouncilState(TypedDict):
    """State passed between agents in the council."""
    messages: Annotated[Sequence[BaseMessage], "The conversation history"]
    task: str
    task_category: Optional[TaskCategory]
    ethics_mode: EthicsMode
    agent_outputs: Dict[str, str]
    final_response: Optional[str]
    metadata: Dict[str, Any]


class EchoCouncil:
    """
    Multi-agent orchestration system for Echo Life OS.

    Coordinates specialized agents:
    - Cortex: Central coordinator, task decomposition
    - Scout: Opportunity detection, market analysis
    - Builder: Generation, creation, problem-solving
    - Auditor: Safety, compliance, legal checks
    - Navigator: Strategy, planning, goal alignment
    - Devil Lens: Adversarial analysis, risk assessment
    - Mapper: Pattern recognition, behavioral analysis
    - Judge: Conflict resolution, final arbitration
    """

    def __init__(
        self,
        anthropic_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        default_ethics_mode: EthicsMode = EthicsMode.L4_RED_TEAM
    ):
        """Initialize the Echo Council."""
        self.default_ethics_mode = default_ethics_mode

        # Initialize LLMs
        self.anthropic_api_key = anthropic_api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.openai_api_key = openai_api_key or os.environ.get("OPENAI_API_KEY")

        if self.anthropic_api_key:
            self.primary_llm = ChatAnthropic(
                model="claude-sonnet-4-20250514",
                api_key=self.anthropic_api_key,
                temperature=0.7
            )
        elif self.openai_api_key:
            self.primary_llm = ChatOpenAI(
                model="gpt-4-turbo-preview",
                api_key=self.openai_api_key,
                temperature=0.7
            )
        else:
            raise ValueError("Either ANTHROPIC_API_KEY or OPENAI_API_KEY required")

        # Define agent configurations
        self.agents = self._create_agent_configs()

        # Build the graph
        self.graph = self._build_graph()

        # Memory for conversation persistence
        self.memory = MemorySaver()

    def _create_agent_configs(self) -> Dict[str, AgentConfig]:
        """Create configurations for all council agents."""
        return {
            "cortex": AgentConfig(
                name="Cortex",
                role="Central Coordinator",
                system_prompt="""You are Cortex, the central coordinator of Echo Council.
Your responsibilities:
- Analyze incoming tasks and decompose complex problems
- Route tasks to appropriate specialist agents
- Synthesize outputs from multiple agents
- Ensure coherent, unified responses

You are the primary reasoning engine. For simple tasks, handle them directly.
For complex tasks, delegate to specialists and coordinate their outputs.""",
                capabilities=["task_decomposition", "routing", "synthesis", "general_reasoning"]
            ),

            "scout": AgentConfig(
                name="Scout",
                role="Opportunity Detection",
                system_prompt="""You are Scout, the opportunity detection agent.
Your responsibilities:
- Identify opportunities in markets, careers, investments
- Analyze trends and emerging patterns
- Detect potential advantages the user can leverage
- Provide actionable intelligence

Focus on finding value and opportunities others might miss.
Be specific and actionable in your recommendations.""",
                capabilities=["market_analysis", "trend_detection", "opportunity_scanning"]
            ),

            "builder": AgentConfig(
                name="Builder",
                role="Generation & Creation",
                system_prompt="""You are Builder, the creation and generation agent.
Your responsibilities:
- Generate code, content, and solutions
- Design systems and architectures
- Solve technical problems
- Create actionable implementations

Focus on practical, buildable solutions.
Provide complete, working implementations when possible.""",
                capabilities=["code_generation", "content_creation", "system_design", "problem_solving"]
            ),

            "auditor": AgentConfig(
                name="Auditor",
                role="Safety & Compliance",
                system_prompt="""You are Auditor, the safety and compliance agent.
Your responsibilities:
- Review actions for legal compliance
- Identify ethical concerns
- Check for security vulnerabilities
- Ensure data privacy protection

Be thorough but not obstructive.
Flag real issues while enabling legitimate activities.""",
                capabilities=["legal_review", "ethics_check", "security_audit", "privacy_analysis"]
            ),

            "navigator": AgentConfig(
                name="Navigator",
                role="Strategy & Planning",
                system_prompt="""You are Navigator, the strategy and planning agent.
Your responsibilities:
- Develop long-term strategies
- Align actions with user goals
- Forecast outcomes and consequences
- Plan optimal paths to objectives

Think strategically and consider multiple time horizons.
Balance short-term actions with long-term goals.""",
                capabilities=["strategic_planning", "goal_alignment", "forecasting", "decision_support"]
            ),

            "devil_lens": AgentConfig(
                name="Devil Lens",
                role="Adversarial Analysis",
                system_prompt="""You are Devil Lens, the adversarial analysis agent.
Your responsibilities:
- Identify risks and vulnerabilities
- Model threats and attack vectors
- Challenge assumptions
- Find flaws in plans and reasoning

Be the devil's advocate. Find what could go wrong.
Your role is to strengthen decisions by exposing weaknesses.""",
                capabilities=["risk_assessment", "threat_modeling", "assumption_challenging", "vulnerability_analysis"],
                temperature=0.3  # More deterministic for security analysis
            ),

            "mapper": AgentConfig(
                name="Mapper",
                role="Pattern Recognition",
                system_prompt="""You are Mapper, the pattern recognition agent.
Your responsibilities:
- Identify patterns in data and behavior
- Recognize trends and correlations
- Map relationships and connections
- Surface hidden structures

Look for patterns others miss.
Connect dots across different domains and time periods.""",
                capabilities=["pattern_detection", "trend_analysis", "relationship_mapping", "behavioral_analysis"]
            ),

            "judge": AgentConfig(
                name="Judge",
                role="Final Arbitration",
                system_prompt="""You are Judge, the final arbitration agent.
Your responsibilities:
- Resolve conflicts between agent outputs
- Make final decisions when agents disagree
- Weigh competing considerations
- Ensure balanced, fair conclusions

Consider all perspectives before deciding.
Explain your reasoning clearly.""",
                capabilities=["conflict_resolution", "decision_making", "balance_assessment", "final_judgment"],
                temperature=0.5  # Balanced
            )
        }

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state machine for the council."""
        graph = StateGraph(CouncilState)

        # Add agent nodes
        graph.add_node("cortex", self._cortex_node)
        graph.add_node("scout", self._scout_node)
        graph.add_node("builder", self._builder_node)
        graph.add_node("auditor", self._auditor_node)
        graph.add_node("navigator", self._navigator_node)
        graph.add_node("devil_lens", self._devil_lens_node)
        graph.add_node("mapper", self._mapper_node)
        graph.add_node("judge", self._judge_node)
        graph.add_node("synthesize", self._synthesize_node)

        # Set entry point
        graph.set_entry_point("cortex")

        # Add conditional routing from cortex
        graph.add_conditional_edges(
            "cortex",
            self._route_from_cortex,
            {
                "opportunity": "scout",
                "creation": "builder",
                "compliance": "auditor",
                "strategy": "navigator",
                "risk": "devil_lens",
                "pattern": "mapper",
                "arbitration": "judge",
                "direct": "synthesize"
            }
        )

        # All specialists route to synthesize or back for more processing
        for agent in ["scout", "builder", "auditor", "navigator", "devil_lens", "mapper", "judge"]:
            graph.add_edge(agent, "synthesize")

        # Synthesize can end or loop back
        graph.add_conditional_edges(
            "synthesize",
            self._should_continue,
            {
                "continue": "cortex",
                "end": END
            }
        )

        return graph.compile(checkpointer=self.memory)

    def _get_ethics_modifier(self, mode: EthicsMode) -> str:
        """Get system prompt modifier based on ethics mode."""
        modifiers = {
            EthicsMode.L5_SAFE_HARBOR: """
Operating in SAFE HARBOR mode:
- Be conservative and cautious in recommendations
- Prioritize safety and well-established practices
- Avoid speculative or edge-case suggestions
- Use friendly, accessible language""",

            EthicsMode.L4_RED_TEAM: """
Operating in RED TEAM mode:
- Consider defensive perspectives and threat models
- Provide thorough risk analysis
- Balance caution with practical utility
- Be direct but maintain boundaries""",

            EthicsMode.L3_GREY_ZONE: """
Operating in GREY ZONE mode:
- Provide competitive intelligence analysis
- Explore structural implications deeply
- Be direct about trade-offs and consequences
- Maintain ethical boundaries while being thorough""",

            EthicsMode.L2_BLACK_LENS: """
Operating in BLACK LENS mode:
- Provide raw, unsoftened analysis
- Map full consequences without filtering
- Be maximally direct and truthful
- Maintain ethical boundaries but minimize softening"""
        }
        return modifiers.get(mode, "")

    async def _invoke_agent(
        self,
        agent_name: str,
        state: CouncilState,
        additional_context: str = ""
    ) -> str:
        """Invoke a specific agent with the current state."""
        config = self.agents[agent_name]
        ethics_modifier = self._get_ethics_modifier(state["ethics_mode"])

        # Build the prompt
        system = f"{config.system_prompt}\n\n{ethics_modifier}\n{additional_context}"

        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=system),
            MessagesPlaceholder(variable_name="messages"),
            HumanMessage(content=f"Task: {state['task']}")
        ])

        # Create chain with temperature override
        llm = self.primary_llm.with_config({"temperature": config.temperature})
        chain = prompt | llm

        # Invoke
        response = await chain.ainvoke({"messages": state["messages"]})
        return response.content

    async def _cortex_node(self, state: CouncilState) -> CouncilState:
        """Cortex agent: analyze and route tasks."""
        # Determine task category
        category = await self._classify_task(state["task"])
        state["task_category"] = category

        # Get cortex analysis
        output = await self._invoke_agent(
            "cortex",
            state,
            f"Classify this task and determine routing. Category detected: {category.value}"
        )

        state["agent_outputs"]["cortex"] = output
        return state

    async def _classify_task(self, task: str) -> TaskCategory:
        """Classify the task into a category for routing."""
        classification_prompt = f"""Classify this task into exactly one category:
- opportunity: Market analysis, finding advantages, trend detection
- creation: Building, coding, generating content, designing
- compliance: Legal checks, safety reviews, ethics evaluation
- strategy: Planning, goal-setting, decision-making
- risk: Threat analysis, vulnerability assessment, risk mapping
- pattern: Pattern recognition, behavioral analysis, trend mapping
- arbitration: Resolving conflicts, making final decisions
- general: Simple questions that don't need specialists

Task: {task}

Respond with only the category name."""

        response = await self.primary_llm.ainvoke([
            HumanMessage(content=classification_prompt)
        ])

        category_str = response.content.strip().lower()

        # Map to TaskCategory
        mapping = {
            "opportunity": TaskCategory.OPPORTUNITY,
            "creation": TaskCategory.CREATION,
            "compliance": TaskCategory.COMPLIANCE,
            "strategy": TaskCategory.STRATEGY,
            "risk": TaskCategory.RISK,
            "pattern": TaskCategory.PATTERN,
            "arbitration": TaskCategory.ARBITRATION,
            "general": TaskCategory.GENERAL
        }

        return mapping.get(category_str, TaskCategory.GENERAL)

    def _route_from_cortex(self, state: CouncilState) -> str:
        """Route from cortex to appropriate specialist."""
        category = state.get("task_category", TaskCategory.GENERAL)

        routing = {
            TaskCategory.OPPORTUNITY: "opportunity",
            TaskCategory.CREATION: "creation",
            TaskCategory.COMPLIANCE: "compliance",
            TaskCategory.STRATEGY: "strategy",
            TaskCategory.RISK: "risk",
            TaskCategory.PATTERN: "pattern",
            TaskCategory.ARBITRATION: "arbitration",
            TaskCategory.GENERAL: "direct"
        }

        return routing.get(category, "direct")

    async def _scout_node(self, state: CouncilState) -> CouncilState:
        """Scout agent: opportunity detection."""
        output = await self._invoke_agent("scout", state)
        state["agent_outputs"]["scout"] = output
        return state

    async def _builder_node(self, state: CouncilState) -> CouncilState:
        """Builder agent: generation and creation."""
        output = await self._invoke_agent("builder", state)
        state["agent_outputs"]["builder"] = output
        return state

    async def _auditor_node(self, state: CouncilState) -> CouncilState:
        """Auditor agent: safety and compliance."""
        output = await self._invoke_agent("auditor", state)
        state["agent_outputs"]["auditor"] = output
        return state

    async def _navigator_node(self, state: CouncilState) -> CouncilState:
        """Navigator agent: strategy and planning."""
        output = await self._invoke_agent("navigator", state)
        state["agent_outputs"]["navigator"] = output
        return state

    async def _devil_lens_node(self, state: CouncilState) -> CouncilState:
        """Devil Lens agent: adversarial analysis."""
        output = await self._invoke_agent("devil_lens", state)
        state["agent_outputs"]["devil_lens"] = output
        return state

    async def _mapper_node(self, state: CouncilState) -> CouncilState:
        """Mapper agent: pattern recognition."""
        output = await self._invoke_agent("mapper", state)
        state["agent_outputs"]["mapper"] = output
        return state

    async def _judge_node(self, state: CouncilState) -> CouncilState:
        """Judge agent: final arbitration."""
        output = await self._invoke_agent("judge", state)
        state["agent_outputs"]["judge"] = output
        return state

    async def _synthesize_node(self, state: CouncilState) -> CouncilState:
        """Synthesize all agent outputs into final response."""
        outputs = state["agent_outputs"]

        if len(outputs) == 1:
            # Single agent, use directly
            state["final_response"] = list(outputs.values())[0]
        else:
            # Multiple agents, synthesize
            synthesis_prompt = f"""Synthesize these agent outputs into a coherent response:

{json.dumps(outputs, indent=2)}

Task: {state['task']}

Create a unified response that:
1. Integrates all relevant insights
2. Resolves any conflicts
3. Provides actionable conclusions
4. Maintains the appropriate tone for ethics mode {state['ethics_mode'].name}"""

            response = await self.primary_llm.ainvoke([
                HumanMessage(content=synthesis_prompt)
            ])

            state["final_response"] = response.content

        return state

    def _should_continue(self, state: CouncilState) -> str:
        """Determine if processing should continue or end."""
        # For now, always end after synthesis
        # Future: could loop back for complex multi-step tasks
        return "end"

    async def process(
        self,
        task: str,
        ethics_mode: Optional[EthicsMode] = None,
        thread_id: str = "default"
    ) -> str:
        """
        Process a task through the Echo Council.

        Args:
            task: The task to process
            ethics_mode: Override default ethics mode
            thread_id: Conversation thread ID for memory

        Returns:
            The council's response
        """
        initial_state: CouncilState = {
            "messages": [],
            "task": task,
            "task_category": None,
            "ethics_mode": ethics_mode or self.default_ethics_mode,
            "agent_outputs": {},
            "final_response": None,
            "metadata": {
                "started_at": datetime.utcnow().isoformat(),
                "thread_id": thread_id
            }
        }

        config = {"configurable": {"thread_id": thread_id}}

        # Run the graph
        final_state = await self.graph.ainvoke(initial_state, config)

        return final_state["final_response"]

    def set_ethics_mode(self, mode: EthicsMode):
        """Set the default ethics mode."""
        self.default_ethics_mode = mode


# Convenience function for quick access
async def consult_council(
    task: str,
    ethics_mode: EthicsMode = EthicsMode.L4_RED_TEAM
) -> str:
    """Quick consultation with the Echo Council."""
    council = EchoCouncil(default_ethics_mode=ethics_mode)
    return await council.process(task)


# Example usage
if __name__ == "__main__":
    import asyncio

    async def main():
        # Initialize council
        council = EchoCouncil()

        # Process a task
        response = await council.process(
            task="Analyze the opportunity in building a personal AI assistant platform",
            ethics_mode=EthicsMode.L3_GREY_ZONE
        )

        print("Council Response:")
        print(response)

    asyncio.run(main())
