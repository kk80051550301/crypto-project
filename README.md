# Crypto Project
====

# Overview

Crypto Project is a simulator for investing crypto currency

## Description

ga_crypto.py :  

choose sceneraio from input/market_patterns.csv,  

call strategy trainer(price strategy + hyperparmeters optimize tools)  

strategy-trainer.prepare(call from optimize/base) -> prepare optimize parameters(GA params)  

strategy-trainer.train(call from optimize/base) -> run optimize easimple  

while train for each optimizing indvidual, calculate fitness/eval_func(def in opt-prepare)  in class st-trainer  

while calculate fitness call simulator.run_simulation by df

while run sim need price(tools/retrivec-rypto price) store to df in simulator.

run_simulation: timing - do trade(by price strategy) - record to history for every hour till end trade per individual

## rin memo:
for run simulation -> timing - trade - record
i wanna def timing class 
details: 
call df for hour info(price, macd, high, low...)
timing strategy decide {event:True/False, trade:buy/sell, } by df info and return record event & trade

recall price strategy tranfer2min unit and do trade return trading_price

record history.append 1.event 2.trade 3.trading fee 4.invest index to df for 1 individual 

## Demo

## VS. 

## Requirement

## Usage

## Install

## Contribution

## Licence

[MIT](https://github.com/tcnksm/tool/blob/master/LICENCE)

## Author

