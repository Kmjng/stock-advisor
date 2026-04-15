"""LangGraph StateGraph — assembles the advisor agent pipeline."""

from langgraph.graph import StateGraph, START, END

from agents.state import AdvisorState
from agents.nodes.portfolio_provider import gather_portfolio
from agents.nodes.market_scout import search_market_news
from agents.nodes.trade_reporter import search_trade_news
from agents.nodes.trade_advisor import analyze_trades


def build_advisor_graph():
    """Build and compile the advisor StateGraph.

    Flow:
        START -> gather_portfolio -> [search_market_news, search_trade_news] -> analyze_trades -> END
                                      ^^^^ parallel fan-out ^^^^                  ^^^^ fan-in ^^^^
    """
    graph = StateGraph(AdvisorState)

    # Add nodes
    graph.add_node("gather_portfolio", gather_portfolio)
    graph.add_node("search_market_news", search_market_news)
    graph.add_node("search_trade_news", search_trade_news)
    graph.add_node("analyze_trades", analyze_trades)

    # START -> PortfolioProvider
    graph.add_edge(START, "gather_portfolio")

    # Fan-out: PortfolioProvider -> MarketScout + TradeReporter (parallel)
    graph.add_edge("gather_portfolio", "search_market_news")
    graph.add_edge("gather_portfolio", "search_trade_news")

    # Fan-in: MarketScout + TradeReporter -> TradeAdvisor
    graph.add_edge("search_market_news", "analyze_trades")
    graph.add_edge("search_trade_news", "analyze_trades")

    # TradeAdvisor -> END
    graph.add_edge("analyze_trades", END)

    return graph.compile()
