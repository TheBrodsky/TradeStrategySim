# Trade Strategy Simulator

This is a simple program designed to simulate a specific trading strategy based on predefined rules and timeframes. The simulator models the behavior of signals and trades to evaluate the outcomes of a trading strategy over a given session.

This was developed as a favor for someone else, and it only simulates 1 trading strategy. I would eventually like to learn more about trading and generalize this into a strategy modeling language.

## Overview

The program operates by:
1. Defining an **Overnight Range (OR)** to establish high and low price levels during a specific time window.
2. Generating **Signals** at predefined times to determine potential trading opportunities.
3. Setting **Listeners** based on signal ranges to initiate trades when an entry price is met.
4. Simulating **Trades** with defined exit points, tracking their outcomes.

## Output
The output of the simulation is a CSV containing the following columns:
- Date - A single trading day
- Signal, ID - ID of the signal spawning this row of data; ID counts from 0 for each day
- Signal, High/Low - Whether this row is spawned from the upper or lower bound of the signal's range
- Signal, Price - The high/low signal price for this row. Sets the anchor that determines trade entry and exit prices
- Signal, In OR - Whether the price is within the Overnight Range
- Trade Entered, Time - The time a trade is entered, empty if it isn't (because price never hit the trade entry target)
- Trade Entered, Price - The price a trade is entered at, empty if it isn't
- Trade Outcome - Whether a trade hit an exit or multiple exits and in what order (e.g. "High", "Low;High")
- Trade High, Time - The time a trade hits its upper exit price, empty if it doesn't
- Trade High, Price - The price a trade hits its upper exit price at, empty if it doesn't
- Trade Low, Time - The time a trade hits its lower exit price, empty if it doesn't
- Trade Low, Price - The price a trade hits its lower exit price at, empty if it doesn't

## How to Use
0. (optional) Edit config.ini
1. Add OHLCV data to input directory (/input/ by default)
2. Run exe
3. Output CSV is put in /output/ by default
