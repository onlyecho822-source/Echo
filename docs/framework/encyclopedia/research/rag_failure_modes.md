# RAG System Failure Modes Research

**Source:** PromptQL Research - "Fundamental Failure Modes in RAG Systems"
**Date:** July 7, 2025
**URL:** https://promptql.io/blog/fundamental-failure-modes-in-rag-systems

## BENCHMARK RESULTS

Using the FRAMES benchmark (824 multi-hop questions requiring 2-15 Wikipedia articles):

| Approach | Accuracy |
|----------|----------|
| Naive RAG | ~40% |
| Agentic RAG | ~60% |
| Plan-based execution (PromptQL) | ~100% |

**Critical Finding:** Traditional RAG fails on 40-60% of complex queries. Even giving LLMs control over retrieval (Agentic RAG) only provides incremental improvement.

## FOUR PRIMARY FAILURE MODES

### 1. Extraction Errors in Processing
The LLM fails to correctly extract relevant information from retrieved documents. Even when the correct information is present in the context, the model misses or misinterprets it.

### 2. Context Size Limitations
When queries require information from multiple sources, the combined context exceeds the model's effective processing capacity. This leads to "context length errors" and information loss.

**Example:** A question requiring atomic number calculations produced a "Context length error" in Agentic RAG but was correctly answered by plan-based execution.

### 3. Inexhaustive Computation Patterns
The LLM fails to systematically explore all necessary information paths. It may stop searching prematurely or miss relevant connections between pieces of information.

### 4. Computational Reasoning Failures
Even with correct information retrieved, the LLM fails at the reasoning step—making mathematical errors, logical mistakes, or incorrect inferences.

## WHY TRADITIONAL RAG FAILS

### The Pipeline Problem
Traditional RAG follows a linear pipeline:
1. Query embedding
2. Vector similarity search
3. Context retrieval
4. LLM generation

This works for simple factual queries but fails for:
- Multi-step reasoning
- Information synthesis from multiple sources
- Numerical computation
- Temporal reasoning
- Constraint satisfaction

### The In-Context Processing Limitation
Both Naive and Agentic RAG process retrieved information within the LLM's context window. This creates fundamental limitations:
- Context window fills up with irrelevant information
- No structured memory for intermediate results
- Cannot reference previous computations
- No separation between planning and execution

## SOLUTION: PLAN-BASED EXECUTION

The research demonstrates that **decoupling planning from execution** fundamentally addresses RAG limitations:

**Key Architectural Changes:**
1. LLM generates query plans in a domain-specific language
2. Plans are executed programmatically OUTSIDE the LLM context
3. Structured memory artifacts store intermediate results
4. Outputs are referenceable across multiple reasoning steps

**Result:** Near-perfect accuracy (~100%) on complex multi-hop queries.

## IMPLICATIONS FOR ECHO SYSTEM

### Architecture Recommendations:

1. **Implement Plan-Based Retrieval**
   - Don't rely on single-shot RAG
   - Generate explicit retrieval plans
   - Execute plans programmatically

2. **Structured Memory Layer**
   - Store intermediate results outside LLM context
   - Enable cross-reference between reasoning steps
   - Maintain computation history

3. **Separate Planning from Execution**
   - Use LLM for planning/strategy
   - Use programmatic execution for retrieval
   - Verify results at each step

4. **Multi-Hop Query Detection**
   - Identify queries requiring multiple retrieval steps
   - Route complex queries to plan-based system
   - Use simple RAG only for single-hop queries

5. **Context Management**
   - Monitor context utilization
   - Implement context compression
   - Prioritize relevant information

### Integration with Echo's Sherlock Hub:

The Sherlock Hub's evidence-tiering system (Documented, Reported, Alleged) aligns well with plan-based retrieval:
- Each retrieval step can be tagged with evidence tier
- Confidence propagates through the reasoning chain
- Audit trail shows exactly what was retrieved and when

### Temporal System Integration:

Echo's temporal decay system should apply to RAG results:
- Retrieved information has a freshness score
- Older retrievals may need re-verification
- Time-sensitive queries require recent sources
