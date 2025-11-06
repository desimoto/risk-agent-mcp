# Code Summary - Risk Agent MCP

This document provides a comprehensive overview of the code in the `src` directory, which implements a loan risk assessment system built using FastMCP (Model Context Protocol) and Claude AI.

## Core Architecture

### 1. `main.py` - Entry Point/Orchestrator

The main execution entry point that demonstrates the complete loan assessment workflow.

**Key Features:**
- Loads environment variables for API keys
- Creates a sample loan application and processes it through the risk assessment pipeline
- Handles async execution and proper resource cleanup
- Demonstrates end-to-end workflow from application intake to risk assessment

### 2. `fastmcp_risk_agent.py` - Core AI Agent

Implements the `FastMCPRiskAgent` class, which is a ReAct (Reasoning + Acting) agent that powers the loan assessment logic.

**Key Components:**
- **Pydantic Models**: Structured input/output with `CreditInput` and `CreditOutput` classes
- **AI Integration**: Uses Anthropic's Claude Haiku model for reasoning and decision-making
- **Tool Schema Conversion**: Converts tool schemas for Anthropic API compatibility
- **Stateful Management**: Maintains conversation history across assessment steps
- **Direct Tool Integration**: Bypasses MCP server for improved efficiency
- **Multi-step Reasoning**: Implements reasoning loops with safety limits (max 5 steps)
- **Comprehensive Assessment**: Considers multiple risk factors including credit scores, business sector, and revenue ratios

### 3. `risk_agent_factory.py` - Factory Pattern

Provides a clean factory interface for creating configured risk agents with proper dependency injection.

**Features:**
- **Clean Interface**: Simplifies agent creation and configuration
- **Environment Management**: Handles API key configuration from environment variables
- **Error Handling**: Comprehensive validation and error reporting
- **Separation of Concerns**: Isolates agent creation logic from business logic
- **Example Usage**: Includes demonstration code and usage patterns

### 4. `mcp_credit_server.py` - Credit Check Service

Standalone MCP server that provides comprehensive credit checking capabilities with real external API integration.

**Core Features:**

#### Real Experian API Integration
- **OAuth2 Authentication**: Manages token lifecycle for Experian sandbox environment
- **FICO Score Retrieval**: Fetches actual credit scores using SSN for small business personal guarantees
- **Error Handling**: Comprehensive fallback mechanisms for API failures
- **Data Processing**: Handles real-world credit data formatting and validation

#### Risk Assessment Logic
- **Credit Score Analysis**: Processes FICO scores in the 300-850 range
- **Revenue Thresholds**: Applies business revenue-based risk criteria
- **Sector Considerations**: Accounts for industry-specific risk factors (e.g., technology sector volatility)
- **Multi-tier Risk Classification**: Categorizes applications as low/medium/high risk

#### Technical Infrastructure
- **Multiple Transport Modes**: Supports stdio, HTTP, and SSE protocols
- **Comprehensive Logging**: Detailed debugging and monitoring capabilities
- **Configuration Management**: Environment-based configuration for different deployment scenarios

## System Features

### AI-Powered Assessment
- **Claude Integration**: Leverages advanced language model for sophisticated loan risk analysis
- **Multi-factor Analysis**: Considers credit scores, business sectors, revenue ratios, and market conditions
- **Structured Output**: Provides consistent JSON-formatted assessments with risk levels and recommendations
- **Contextual Reasoning**: Maintains conversation context for complex multi-step assessments

### Real External Data Integration
- **Experian API**: Direct integration with credit reporting services
- **OAuth2 Flow**: Secure authentication and token management
- **Live Data Processing**: Real-time FICO score retrieval and analysis
- **Data Validation**: Robust input validation and error handling

### Flexible Architecture
- **Modular Design**: Clear separation of concerns across components
- **Factory Pattern**: Simplified instantiation and configuration management
- **Multiple Deployment Options**: Support for standalone server or integrated tool modes
- **Transport Agnostic**: Compatible with various communication protocols

### Robust Error Handling
- **Exception Management**: Comprehensive error catching and recovery
- **Fallback Mechanisms**: Graceful degradation when external services are unavailable
- **Detailed Logging**: Extensive logging for debugging and operational monitoring
- **Validation**: Input validation and sanitization throughout the pipeline

## Business Logic

### Small Business Loan Focus
- **Personal Guarantees**: Utilizes owner SSN for credit assessment in small business context
- **Revenue Analysis**: Considers business revenue patterns and sustainability
- **Industry Risk**: Sector-specific risk assessment with technology sector scrutiny
- **Loan Limit Calculations**: Revenue-based approved limit determination

### Risk Assessment Criteria
- **Credit Score Tiers**:
  - Below 600: High risk with limited approval
  - 600-700: Medium risk with moderate limits
  - Above 700: Low risk with favorable terms
- **Revenue Thresholds**: Minimum revenue requirements for loan consideration
- **Sector Volatility**: Enhanced scrutiny for high-volatility industries
- **Multi-dimensional Analysis**: Combines quantitative and qualitative factors

## Production Readiness

This system represents a production-ready loan risk assessment platform that combines:
- **AI Reasoning**: Advanced language model capabilities for complex decision-making
- **Real-world Integration**: Actual financial data sources and credit reporting APIs
- **Scalable Architecture**: Modular design supporting various deployment scenarios
- **Operational Excellence**: Comprehensive logging, error handling, and monitoring

The platform is suitable for actual small business lending operations, providing the foundation for automated loan underwriting and risk assessment workflows.