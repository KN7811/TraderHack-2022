# TraderHack-2022
## Introduction
This repository contains the code of my submission to the TraderHack 24 hour hackathon run by Optiver. The main trading code can be found in the file 'algo.py'.

The task was to create an algorithm that best trades a "dual listing" within the pressures of a constantly changing market. The trading was done in a simulated exchange, Optibook.
## The Challenge
The challenge involved trading a dual listing - "PHILIPS-A" and "PHILIPS-B", the listing of the same security of two different exchanges. A strategy was created using arbrtirage to detect opportunities in "PHILIP-B"'s order book, and the trades were hedged in the order books of "PHILIPS-A". At the same time, "PHILIPS-B" is a more illiquid market and so it was necessary to contnuously make 2-sided quotes in "PHILIPS-B"'s order book, while hedging the trades in "PHILIPS-A", in order to try to improve this market.
