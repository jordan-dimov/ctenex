# ctenex: Educational Energy Commodity Trading Exchange

## Background and Overview

This is an educational project that simulates an energy commodity trading platform. It has been built to demonstrate how modern electronic trading systems work, particularly for energy markets such as electricity, natural gas, and crude oil.

Trading exchanges are essential financial infrastructure that allow market participants to buy and sell standardized contracts efficiently. Energy commodities, unlike stocks or bonds, have unique characteristics tied to physical delivery, location, and time periods, making their trading mechanisms particularly interesting to model.

This project provides a simplified but realistic implementation of the core components found in actual trading exchanges, making it an excellent learning tool for those interested in financial markets, energy trading, or software architecture for financial systems: 

* Understanding financial market infrastructure
* Learning about order matching algorithms
* Exploring energy trading mechanisms
* Studying modern software design patterns
* Practicing with FastAPI and Python for financial applications

The system is designed with clarity and educational value in mind, making complex trading concepts accessible through well-structured code and comprehensive documentation.

## How It Works
At its core, *ctenex* operates like any modern electronic exchange, with several key components working together:

### Contracts

The system models energy commodity contracts with specific attributes:

* Commodity type: Power, natural gas, or crude oil
* Delivery period: Hourly, daily, monthly, quarterly, or yearly
* Location: Geographic delivery point (e.g., "GB" for Great Britain)
* Start and end dates: When delivery begins and ends
* Contract specifications: Including tick size (minimum price movement) and contract size

For example, the system includes a UK power baseload contract for March 2025 (UK-BL-MAR-25), which represents electricity to be delivered continuously throughout March 2025 in the UK market.

### Order Book

The order book is the heart of any exchange, organising all buy and sell orders:

* Bids: Buy orders sorted by price (highest first) and time (earliest first)
* Asks: Sell orders sorted by price (lowest first) and time (earliest first)

This organisation ensures fairness and transparency, as orders are matched following clear price-time priority rules.

### Order Types

Traders can submit different types of orders:

* Limit orders: Specify the maximum price a buyer is willing to pay or the minimum price a seller is willing to accept
* Market orders: Execute immediately at the best available price without price restrictions

### Matching Engine

The matching engine is the sophisticated system that brings buyers and sellers together:

* It processes incoming orders in sequence
* For each new order, it attempts to match it with existing orders on the opposite side
* Matches occur when a buy price meets or exceeds a sell price
* When multiple orders qualify for matching, the best price gets priority
* At equal prices, earlier orders are matched first (time priority)
* Partial fills occur when an order is only partially matched

## REST API

The system exposes its functionality through a FastAPI REST API, allowing:

* Placing new orders
* Viewing current market orders
* Checking contract specifications

## Development

To learn how to use the dev tools available, see the [Dev Tools section](./docs/dev-tools.md)
