starts 3pm (for next day), after hours
6:30am - session open
2pm - session close


PROCEDURE:
1. Determine overnight range: OR_high and OR_low
2. Signal 1 (S1) range: S1_high, S1_low and S1_range
3. Set Trigger 1 (T1): T1_high and T1_low


Overnight range (OR):
 - the range between 12am and 6am
 - define high and low in range

Signals (S):
 - s1 = 6:30, 5 min
 - s2 = 7:00, 15 min
 - s3 = 8:15, 15 min

Listener (L):
 - a listener listens for a certain price (L_price) to be hit within a range
 - all lsiteners cutoff after 2 hours
 - if a trigger activates, it spawns a Trade (T)

Trade (T):
 - a trade has a top (Tt) and bottom price (Tb), defined as the trigger price +/- the signal range
 - Tt = L_price + S_range, Tb = L_price - S_range
 - a trade ends when 2 hours elapses from its parent trigger
 - a trade specifies whether it hit the top and/or bottom price and when (in what order)

Output:
- day
- whether Listener is IN or OUT of OR
- Listener outcome
- Trade outcome (and order)
