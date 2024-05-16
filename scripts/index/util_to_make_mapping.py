"""
utility script to make one-to-one mapping
"""

import json

# in-text in-index one-to-one
data = """
John Kenneth Galbraith
Galbraith, John Kenneth
Joseph Gordon-Levitt
Gordon-Levitt, Joseph
Jeremy Corbyn
Corbyn, Jeremy
Juan Benet
Benet, Juan
Julian Schillinger
Schillinger, Julian
Kim Stanley Robinson
Robinson, Kim Stanley
Laurie Anderson
Anderson, Laurie
Lex Fridman
Fridman, Lex
Lucan Way
Way, Lucan
Mat Dryhurst
Dryhurst, Mat
Matthew Yglesias
Yglesias, Matthew
Max Weber
Weber, Max
Mencius Moldbug
Moldbug, Mencius
Michael Linton
Linton, Michael
Michelle Wu
Wu, Michelle
Mykhailo Fedorov
Fedorov, Mykhailo
Neal Stephenson
Stephenson, Neal
Neil Armstrong
Armstrong, Neil
Noah Smith
Smith, Noah
Norbert Wiener
Wiener, Norbert
Oded Galor
Galor, Oded
Oliver Wendell Holmes
Holmes, Oliver Wendell
Pascual Restrepo
Restrepo, Pascual
Paul Baran
Baran, Paul
Paul Jozef Crutzen
Crutzen, Paul Jozef
Ray Kurzweil
Kurzweil, Ray
Reid Hoffman
Hoffman, Reid
Richard Nixon
Nixon, Richard
Richard Rorty
Rorty, Richard
Robert Putnam
Putnam, Robert
Robert Taylor
Taylor, Robert
Robin Dunbar
Dunbar, Robin
Santiago Ramón y Cajal
Ramón y Cajal, Santiago
Satya Nadella
Nadella, Satya
Sebastian Kurz
Kurz, Sebastian
Seth Parker
Parker, Seth
Shoshanna Zuboff
Zuboff, Shoshanna
Suzanne Simard
Simard, Suzanne
"""

data = """
The Age of Surveillance Capitalism
Age of Surveillance Capitalism, The
The Castle
Castle, The
The Circle
Circle, The
The Diversity Of Cross-species Interactions
Diversity Of Cross-species Interactions, The
The Double Coincidence Of Wants
Double Coincidence Of Wants, The
The Dream Machine
Dream Machine, The
The Emperor's New Clothes
Emperor's New Clothes, The
The Greatest Good For The Greatest Number
Greatest Good For The Greatest Number, The
The Hebbian Model Of Connections
Hebbian Model Of Connections, The
The Human Condition
Human Condition, The
The Identity Provider
Identity Provider, The
The Lord of the Flies
Lord of the Flies, The
The Lost Dao
Lost Dao, The
The Mix Of Diversity And Interconnectedness
Mix Of Diversity And Interconnectedness, The
The Network State
Network State, The
The New Republic
New Republic, The
The Public and its Problems
Public and its Problems, The
The Social Dilemma
Social Dilemma, The
The Sovereign Individual
Sovereign Individual, The
The Uncertainty Principle
Uncertainty Principle, The
The World Cafe
World Cafe, The
"""
data = """
Tim Berners-Lee
Berners-Lee, Tim
Ursula Le Guin
Le Guin, Ursula
Winslow Porter
Porter, Winslow
Youssef Nader
Nader, Youssef
"""
data = """
Audrey Tang
Tang, Audrey
Douglas Engelbart
Engelbart, Douglas
Octabia Butler
Butler, Octavia
Oscar Wilde
Wilde, Oscar
"""
lines = data.strip().splitlines()
dict = {}
for i in range(0, len(lines), 2):
    dict[lines[i + 1]] = [lines[i]]

json.dump(dict, open("tmp.json", "w"), indent=2)
